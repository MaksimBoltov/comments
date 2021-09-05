import json
from uuid import UUID

from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.serializers import CommentListSerializer
from api.services import (BadRequestException, BadRequestExceptionUserData,
                          PaginationComments, PaginationHistoryUserComments)
from comments.models import Comment, EntityType, User


def is_uuid(check_uuid: str) -> bool:
    """Returns whether the check_uuid is a uuid.

    :param check_uuid: string for checking value
    :type check_uuid: str

    :rtype: bool
    :return: whether the check_uuid is a uuid value
    """

    try:
        UUID(check_uuid)
        return True
    except ValueError:
        return False


def is_valid_comment_request(data: dict) -> (bool, str):
    """Returns True if request's data is valid and False otherwise.
    Also returns exceptions message if data is not valid.

    :param data: new comment's data that adding to database
    :type data: dict

    :rtype: (bool, str)
    :return: is request's data valid and exception message if it is required
    """

    # checking the availability of keys
    required_keys = [
        "author", "text", "parent_entity_uuid", "parent_entity_type"
    ]
    for key in required_keys:
        try:
            data[key]
        except KeyError as exc:
            return False, f"The {exc} field was not found!"

    # checking that the user exists
    if is_uuid(data["author"]):
        if not User.objects.filter(uuid_user=data["author"]).count():
            return False, f"The user '{data['author']}' was not found"
    elif not User.objects.filter(nickname=data["author"]).count():
        return False, f"The user '{data['author']}' was not found"

    # checking that parent_entity_uuid is uuid
    if not is_uuid(data["parent_entity_uuid"]):
        return False, "The parent_entity_uuid must ba uuid"

    # checking that the parent entity type exists
    if str(data["parent_entity_type"]).isdigit():
        if not len(EntityType.objects.filter(id=data["parent_entity_type"])):
            return False, "The parent_entity_type was not found"
    elif not len(EntityType.objects.filter(name=data["parent_entity_type"])):
        return False, "The parent_entity_type was not found"

    return True, ""


@api_view(["POST"])
def manage_new_comment(request):
    """Adds new comment to database and response for page.
    Processes a request to 'api/new-comments/'.
    Have only POST method.
    """

    if request.method == "POST":

        # check the validity of the data
        data = json.loads(request.body)
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
        /api/first-lvl-comments/<str:uuid>
        /api/first-lvl-comments/<str:uuid>?page_size=<int>
        /api/first-lvl-comments/<str:uuid>?page=<int>
        /api/first-lvl-comments/<str:uuid>?page=<int>&page_size=<int>
    Where:
    <str:uuid> - string representation of the value uuid of specific entity.
    page_size - count of comments on page.
    page - number of pagination page.
    """

    pagination_class = PaginationComments
    serializer_class = CommentListSerializer

    def get_queryset(self):
        """Returns queryset with all first level comments of a certain entity.

        :raise: BadRequestException
        :return: Queryset of Comment's instance
        """
        uuid_value = self.kwargs.get('uuid', None)
        if not is_uuid(str(uuid_value)):
            raise BadRequestException
        else:
            return Comment.objects.filter(parent_entity=UUID(uuid_value))


class CommentsUserHistoryListView(ListAPIView):
    """Has method 'GET' for getting all comments by user.
    As a parameter 'user', you can specify either the nickname or uuid.

    Processes such requests as:
        /api/history-comments/<str:user>
        /api/history-comments/<str:user>?page_size=<int>
        /api/history-comments/<str:user>?page=<int>
        /api/history-comments/<str:user>?page=<int>&page_size=<int>
    Where:
    <str:user> - string representation of the value uuid or
    nickname of specific user.
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
        user_identify = self.kwargs.get('user', None)
        # if the data was skipped
        if user_identify is None:
            raise BadRequestException
        # if the uuid value was entered
        elif is_uuid(user_identify):
            if User.objects.filter(uuid_user=user_identify).count() == 0:
                # raise 400 exception if user not found in db
                raise BadRequestExceptionUserData
            user = User.objects.get(uuid_user=user_identify)
        # if the nickname value was entered
        else:
            if User.objects.filter(nickname=user_identify).count() == 0:
                # raise 400 exception if user not found in db
                raise BadRequestExceptionUserData
            user = User.objects.get(nickname=user_identify)

        return Comment.objects.filter(user=user).order_by('created_date').\
            reverse()
