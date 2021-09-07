import csv
import json
from uuid import UUID

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CommentListSerializer
from api.services import (BadRequestException, BadRequestExceptionDatetime,
                          BadRequestExceptionEntityNotFound,
                          BadRequestExceptionUserData,
                          BadRequestExceptionUserNotFound, PaginationComments,
                          PaginationHistoryUserComments,
                          get_all_child_comments,
                          get_comments_queryset_entity_with_filtered,
                          get_comments_queryset_user_with_filtered, get_date,
                          get_user, is_uuid, is_valid_comment_request)
from comments.models import Comment, EntityType, User


@api_view(["POST"])
def manage_new_comment(request):
    """Adds new comment to database and response for page.
    Processes a request to 'api/new-comments/'.
    Have only POST method.
    """

    if request.method == "POST":

        # check the validity of JSON
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            response = {
                "name": "Bad Request",
                "message": "The entered JSON is not valid.",
                "status": 400,
            }
            return Response(response, status=400)
        # check the validity of the data
        valid_data, exception_message = is_valid_comment_request(data)
        if not valid_data:
            response = {
                "name": "Bad Request",
                "message": exception_message,
                "status": 400,
            }
            return Response(response, status=400)

        # add new comment to DB
        if is_uuid(data["author"]):
            user = User.objects.get(uuid_user=data["author"])
        else:
            user = User.objects.get(nickname=data["author"])
        comment = Comment(
            user=user,
            text=data["text"],
            parent_entity=UUID(data["parent_entity_uuid"]),
            parent_entity_type=EntityType.objects.get(
                name=data["parent_entity_type"]
            ),
        )
        comment.save()

        response = {
            "name": "Created",
            "message": "New comment was created!",
            "status": 201
        }
        return Response(response, status=201)


class CommentsListView(ListAPIView):
    """Has method 'GET' for getting all first level comments
    for a specific entity.

    Processes such requests as:
        /api/first-lvl-comments?entity=<str>
        /api/first-lvl-comments?entity=<str>&page_size=<int>
        /api/first-lvl-comments?entity=<str>&page=<int>
        /api/first-lvl-comments?entity=<str>&page=<int>&page_size=<int>
    Where:
    entity - the entity for which comments are searching. Can be uuid value.
    page_size - count of comments on page.
    page - number of pagination page.
    """

    pagination_class = PaginationComments
    serializer_class = CommentListSerializer

    def get_queryset(self):
        """Returns queryset with all first level comments of a certain entity.

        :raise: BadRequestException | BadRequestExceptionEntityNotFound
        :return: Queryset of Comment's instance
        """
        entity_value = self.request.GET.get('entity', None)

        if entity_value is None:
            raise BadRequestExceptionEntityNotFound
        elif not is_uuid(str(entity_value)):
            raise BadRequestException
        else:
            return Comment.objects.filter(parent_entity=UUID(entity_value))


class CommentsUserHistoryListView(ListAPIView):
    """Has method 'GET' for getting all comments by user.
    As a parameter 'user', you can specify either the nickname or uuid.

    Processes such requests as:
        /api/history-comments?user=<str:user>
        /api/history-comments?user=<str:user>&page_size=<int>
        /api/history-comments?user=<str:user>&page=<int>
        /api/history-comments?user=<str:user>&page=<int>&page_size=<int>
    Where:
    <str:user> - string representation of the value uuid or
    nickname of specific user.
    user - the user for whom comments are searching.
    page_size - count of comments on page (default 50).
    page - number of pagination page.
    """

    pagination_class = PaginationHistoryUserComments
    serializer_class = CommentListSerializer

    def get_queryset(self):
        """Returns queryset with all comments certain user.
        The comments are arranged from newer to older.

        :raise: BadRequestException | BadRequestExceptionUserData
        :return: Queryset of Comment's instance
        """

        # get 'user' from url's queryset
        user_identify = self.request.GET.get('user', None)
        # if user value was not input
        if user_identify is None:
            raise BadRequestExceptionUserNotFound
        # if the data was skipped
        if user_identify is None:
            raise BadRequestException
        # get user instance is does it exist or None
        user = get_user(user_identify)
        # user doesn't exist
        if user is None:
            raise BadRequestExceptionUserData

        return Comment.objects.filter(user=user).order_by('created_date').\
            reverse()


class CSVUserViewSet(APIView):
    """Has method 'GET' for getting csv file with all comments for certain user.
    As a parameter 'user', you can specify either the nickname or uuid.

    Processes such requests as:
        /api/history/user?user=<str:user>
        /api/history/user?user=<str:user>&start_date=<str>
        /api/history/user?user=<str:user>&end_date=<str>
        /api/history/user?user=<str:user>&start_date=<int>&end_date=<str>

    Where:
    <str:user> - string representation of the value uuid or
    nickname of specific user.
    user - the user for whom comments are searching.
    start_date - starting from what date to output the result
    (format: YYY-MM-DDThh:mm:ss).
    end_date - ending with what date to output the result
    (format: YYY-MM-DDThh:mm:ss).

    If input invalid date raise exception.
    """
    def get(self, request):
        """The function processes 'GET' requests.

        :param request: request from user.

        :raises BadRequestException: if user value is None
        :raises BadRequestExceptionUserData: if user doesn't exists
        :raises BadRequestExceptionDatetime: if start_date or end_date
         from get parameters is invalid

        :return: response with csv file.
        """
        # check the user data
        user = request.GET.get("user", None)
        if user is None:
            raise BadRequestException
        # check is user does it exist
        user_instance = get_user(user)
        if user_instance is None:
            raise BadRequestExceptionUserData

        # get and check date
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        # check the start time data
        if start_date is not None:
            if get_date(start_date) is None:
                raise BadRequestExceptionDatetime

        # check the end time data
        if end_date is not None:
            if get_date(end_date) is None:
                raise BadRequestExceptionDatetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        field_headings = [
            'uuid_comment', 'created_date', 'user',
            'text', 'parent_entity', 'parent_entity_type'
        ]
        writer = csv.DictWriter(response, fieldnames=field_headings)
        writer.writeheader()

        # add comments from queryset to csv file
        queryset = get_comments_queryset_user_with_filtered(
            user_instance, start_date, end_date
        )
        for comment in queryset:
            writer.writerow({
                'uuid_comment': comment.uuid_comment,
                'created_date': str(comment.created_date),
                'user': user_instance.nickname,
                'text': comment.text,
                'parent_entity': comment.parent_entity,
                'parent_entity_type': comment.parent_entity_type.name
            })

        return response


class CSVEntityViewSet(APIView):
    """Has method 'GET' for getting csv file with all comments for certain entity.

    Processes such requests as:
        /api/history/entity?entity=<str:uuid>
        /api/history/entity?entity=<str:uuid>&start_date=<str>
        /api/history/entity?entity=<str:uuid>&end_date=<str>
        /api/history/entity?entity=<str:uuid>&start_date=<int>&end_date=<str>

    Where:
    <str:uuid> - uuid of entity
    entity - the entity for which comments are searching.
    start_date - starting from what date to output the result
    (format: 'YYY-MM-DDThh:mm:ss').
    end_date - ending with what date to output the result
    (format: 'YYY-MM-DDThh:mm:ss').

    If input invalid date raise exception.
    """
    def get(self, request):
        """The function processes 'GET' requests.

        :param request: request from user.

        :raises BadRequestException: if uuid is not UUID value
        :raises BadRequestExceptionDatetime: if start_date or end_date
         from get parameters is invalid

        :return: response with csv file.
        """
        uuid = request.GET.get('entity', None)
        if uuid is None:
            raise BadRequestException
        if not is_uuid(uuid):
            raise BadRequestException

        # get and check date
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        # check the start time data
        if start_date is not None:
            if get_date(start_date) is None:
                raise BadRequestExceptionDatetime

        # check the end time data
        if end_date is not None:
            if get_date(end_date) is None:
                raise BadRequestExceptionDatetime

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        field_headings = [
            'uuid_comment', 'created_date', 'user',
            'text', 'parent_entity', 'parent_entity_type'
        ]
        writer = csv.DictWriter(response, fieldnames=field_headings)
        writer.writeheader()

        # add comments from queryset to csv file
        queryset = get_comments_queryset_entity_with_filtered(
            uuid, start_date, end_date
        )
        for comment in queryset:
            writer.writerow({
                'uuid_comment': comment.uuid_comment,
                'created_date': str(comment.created_date),
                'user': comment.user.nickname,
                'text': comment.text,
                'parent_entity': str(uuid),
                'parent_entity_type': comment.parent_entity_type.name
            })

        return response


@api_view(["GET"])
def manage_all_child_comments(request):
    """Has method 'GET' for getting all child comments for input root entity.

    Processes such requests as:
        /api/child-comments?root=<uuid>
        /api/child-comments?root=<uuid>&entity_type=<str>

    Where:
    <uuid> - uuid value.
    <str> - string value.
    root - the entity to find child comments for.
    entity_type - type of root entity.

    :param request: request from user
    :return: response for user
    :rtype: Response
    """

    if request.method == "GET":
        root = request.GET.get('root', None)
        # entity_type = request.GET.get('entity_type', None)

        # check 'root' input value
        if root is None:
            response = {
                "name": "Bad Request",
                "message": "Please, input 'root' value.",
                "hint": "You need to write ?root=<uuid> parameter. "
                        "Not necessary parameter: ?entity_type=<str>",
                "status": 400,
            }
            return Response(response, status=400)
        # check valid uuid value
        elif not is_uuid(root):
            response = {
                "name": "Bad Request",
                "message": "Root is not UUID.",
                "status": 400,
            }
            return Response(response, status=400)
        # check does the uuid value exist
        elif not Comment.objects.filter(uuid_comment=root).count():
            response = {
                "name": "Bad Request",
                "message": f"Element '{root}' was not found.",
                "status": 400,
            }
            return Response(response, status=400)

        root_entity = Comment.objects.get(uuid_comment=UUID(root))
        response = {
            "uuid_comment": root_entity.uuid_comment,
            "created_date": root_entity.created_date,
            "user": root_entity.user.nickname,
            "parent_entity": str(root_entity.parent_entity),
            "parent_entity_type": root_entity.parent_entity_type.name,
            "text": root_entity.text,
            "child": get_all_child_comments(str(root_entity.uuid_comment))
        }

        return Response(response, status=200)
