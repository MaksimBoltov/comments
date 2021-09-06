import uuid
from collections import OrderedDict
from datetime import datetime
from typing import Union
from uuid import UUID

from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Services for check and get data to views. #
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
        return False, "The parent_entity_uuid must be uuid"

    # checking that the parent entity type exists
    if str(data["parent_entity_type"]).isdigit():
        if not len(EntityType.objects.filter(id=data["parent_entity_type"])):
            return False, "The parent_entity_type was not found"
    elif not len(EntityType.objects.filter(name=data["parent_entity_type"])):
        return False, "The parent_entity_type was not found"

    return True, ""


def get_user(user_value: str) -> Union[User, None]:
    """Check user exist and return User instance (if user exist)
    and None otherwise.

    :param user_value: nickname or uuid of user
    :type user_value: str

    :return: User instance or Non if user not found
    """

    # if the uuid value was entered
    if is_uuid(user_value):
        if User.objects.filter(uuid_user=user_value).count() == 0:
            return None
        else:
            return User.objects.get(uuid_user=user_value)
    # if the nickname value was entered
    else:
        if User.objects.filter(nickname=user_value).count() == 0:
            return None
        else:
            return User.objects.get(nickname=user_value)


def get_date(date: str) -> Union[datetime, None]:
    """Check format of date and convert str to datetime.
    Need date format:
        %Y-%m-%dT%H:%M:%S
    Example:
        '2000-01-01T08:00:00'

    :param date:
    :type date: str
    :return: datetime or None if date format incorrect
    """
    try:
        date_result = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        return date_result

    except ValueError:
        return None


def get_comments_queryset_user_with_filtered(
        user: User,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime]
) -> Comment:
    """Return Comment queryset with filtering by parameters: start_time, end_time.

    :param user: the user for whom we are searching comments
    :type user: User

    :param start_date: starting from what date to output the result
    :type start_date: str | datetime

    :param end_date: ending with what date to output the result
    :type end_date: str | datetime

    :return: Comment queryset with filtered
    :rtype: Comment
    """
    if start_date and end_date:
        return Comment.objects.filter(
            user=user,
            created_date__gte=start_date,
            created_date__lte=end_date
        )
    elif start_date:
        return Comment.objects.filter(
            user=user,
            created_date__gte=start_date,
        )
    elif end_date:
        return Comment.objects.filter(
            user=user,
            created_date__lte=end_date
        )
    else:
        return Comment.objects.filter(
            user=user
        )


def get_comments_queryset_entity_with_filtered(
        entity_uuid: uuid.uuid4,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime]
) -> Comment:
    """Return Comment queryset with filtering by parameters: start_time, end_time.

    :param entity_uuid: the entity for which we are searching comments
    :type entity_uuid: uuid.uuid4

    :param start_date: starting from what date to output the result
    :type start_date: str | datetime

    :param end_date: ending with what date to output the result
    :type end_date: str | datetime

    :return: Comment queryset with filtered
    :rtype: Comment
    """
    if start_date and end_date:
        return Comment.objects.filter(
            parent_entity=entity_uuid,
            created_date__gte=start_date,
            created_date__lte=end_date
        )
    elif start_date:
        return Comment.objects.filter(
            parent_entity=entity_uuid,
            created_date__gte=start_date,
        )
    elif end_date:
        return Comment.objects.filter(
            parent_entity=entity_uuid,
            created_date__lte=end_date
        )
    else:
        return Comment.objects.filter(
            parent_entity=entity_uuid
        )


# Another services #

class PaginationComments(PageNumberPagination):
    """Custom pagination class with custom response
    on the similarity of this:
    {
      "comments_count": 1,
      "next": 'http://...' | null,
      "previous": 'http://...' | null,
      "comments": [...]
    }

    A comment has presentation as follows:
    {
      "uuid_comment": uuid.uuid4(),
      "user": 'nickname',
      "parent_entity_type": 'Type_name',
      "created_date": "2021-01-01T00:00:00.000001Z",
      "text": "text",
      "parent_entity": uuid.uuid4()
    }
    """

    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """Processes requests with pagination."""
        return Response(OrderedDict([
            ('comments_count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('comments', data),
        ]), status=200)


class PaginationHistoryUserComments(PageNumberPagination):
    """Custom pagination class with custom response
    on the similarity of this:
    {
      "comments_count": 1,
      "next": 'http://...' | null,
      "previous": 'http://...' | null,
      "comments": [...]
    }

    A comment has presentation as follows:
    {
      "uuid_comment": uuid.uuid4(),
      "user": 'nickname',
      "parent_entity_type": 'Type_name',
      "created_date": "2021-01-01T00:00:00.000001Z",
      "text": "text",
      "parent_entity": uuid.uuid4()
    }
    """

    page_size = 50
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """Processes requests with pagination."""
        return Response(OrderedDict([
            ('comments_count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('comments', data),
        ]), status=200)


# exceptions #

class BadRequestException(APIException):
    """Exception by invalid uuid value in 'CommentsListView'."""

    status_code = 400
    default_detail = {
        "name": "Bad Request",
        "message": "Value was not UUID",
        "status": 400,
    }
    default_code = 'service_unavailable'


class BadRequestExceptionUserData(APIException):
    """Exception is for the situation when the user is not found in the db."""

    status_code = 400
    default_detail = {
        "name": "Bad Request",
        "message": "User was not found.",
        "status": 400,
    }
    default_code = 'service_unavailable'


class BadRequestExceptionDatetime(APIException):
    """Exception is for the situation when datetime is incorrect."""

    status_code = 400
    default_detail = {
        "name": "Bad Request",
        "message": "Date you entered is incorrect.",
        "status": 400,
    }
    default_code = 'service_unavailable'
