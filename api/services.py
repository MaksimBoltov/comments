from collections import OrderedDict

from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


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
