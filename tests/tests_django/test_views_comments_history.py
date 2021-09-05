import json
import uuid

from django.test import TestCase

from comments.models import Comment, EntityType, User


class CommentsHistoryPaginationTest(TestCase):
    """Test work custom pagination class 'PaginationHistoryUserComments'."""
    nickname = 'nick'
    uuid_user = uuid.uuid4()
    comments_text = ['Comment1', 'Comment2', 'Comment3']

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 3 child comment for test.
        """
        # create type of entity
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        # create user
        user = User.objects.create(
            uuid_user=cls.uuid_user,
            nickname=cls.nickname,
            firstname="Nick"
        )
        # create comments by user
        for text in cls.comments_text:
            Comment.objects.create(
                user=user,
                text=text,
                parent_entity=uuid.uuid4(),
                parent_entity_type=entity_type
            )

    def test_pagination_with_standard_page_size_comments_count(self):
        """Get first level comments with standard page size - 50."""
        response = self.client.get(
            f"/api/history-comments/{self.nickname}"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['comments_count'], 3)
        self.assertEqual(len(data['comments']), 3)

    def test_pagination_two_comments_in_page_first_page(self):
        """Test the first page of pagination with page_size = 2."""
        response_first_page = self.client.get(
            f"/api/history-comments/{self.nickname}?page_size=2"
        )
        data_first = json.loads(response_first_page.content)

        self.assertEqual(response_first_page.status_code, 200)
        self.assertEqual(data_first['comments_count'], 3)
        self.assertEqual(len(data_first['comments']), 2)

    def test_pagination_two_comments_in_page_second_page(self):
        """Test the second page of pagination with page_size = 2."""
        response_second_page = self.client.get(
            f"/api/history-comments/{self.nickname}?page=2&page_size=2"
        )
        data_second = json.loads(response_second_page.content)

        self.assertEqual(response_second_page.status_code, 200)
        self.assertEqual(data_second['comments_count'], 3)
        self.assertEqual(len(data_second['comments']), 1)

    def test_pagination_two_comments_in_page_third_page_exception(self):
        """Test that is not third page at pagination 3 comment by 2 on page."""
        response = self.client.get(
            f"/api/history-comments/{self.nickname}?page=3&page_size=2"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['detail'], "Invalid page.")


class GetHistoryCommentsByUserTest(TestCase):
    """Test work getting comments for certain user."""
    nickname = 'nick'
    uuid_user = uuid.uuid4()

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 1 child comment for test data.
        """
        # create instance of EntityType
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        # create User's instance
        user = User.objects.create(
            uuid_user=cls.uuid_user,
            nickname=cls.nickname,
            firstname="Nick"
        )
        # create Comment's instance
        Comment.objects.create(
            user=user,
            text='Text',
            parent_entity=uuid.uuid4(),
            parent_entity_type=entity_type
        )

    def test_get_comments_history_for_nickname(self):
        """Get first level comments correct data."""
        response = self.client.get(
            f"/api/history-comments/{self.nickname}"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['comments_count'], 1)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['text'], 'Text')

    def test_get_comments_history_for_uuid(self):
        """Get first level comments correct data."""
        response = self.client.get(
            f"/api/history-comments/{self.uuid_user}"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['comments_count'], 1)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['text'], 'Text')


class BadRequestExceptionUserDataTest(TestCase):
    """Tests work custom exception class 'BadRequestExceptionUserData'."""

    def test_there_is_not_user_in_db_for_uuid(self):
        """Test the user was not found by uuid."""
        response = self.client.get(f"/api/history-comments/{uuid.uuid4()}")
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "User was not found.")

    def test_there_is_not_user_in_db_for_nickname(self):
        """Test the user was not found by nickname."""
        response = self.client.get("/api/history-comments/11111")
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "User was not found.")
