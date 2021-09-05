import json
import uuid

from django.test import TestCase

from comments.models import Comment, EntityType, User


class PaginationTest(TestCase):
    """Test work custom pagination class 'PaginationComments'."""
    parent_entity = uuid.uuid4()
    comments_text = ['Comment1', 'Comment2', 'Comment3']

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 3 child comment for test.
        """
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        user = User.objects.create(nickname="nick", firstname="Nick")

        for text in cls.comments_text:
            Comment.objects.create(
                user=user,
                text=text,
                parent_entity=cls.parent_entity,
                parent_entity_type=entity_type
            )

    def test_pagination_with_standard_page_size_comments_count(self):
        """Get first level comments with standard page size - 10."""
        response = self.client.get(
            f"/api/first-lvl-comments/{self.parent_entity}"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['comments_count'], 3)
        self.assertEqual(len(data['comments']), 3)

    def test_pagination_two_comments_in_page_first_page(self):
        """Test the first page of pagination with page_size = 2."""
        response_first_page = self.client.get(
            f"/api/first-lvl-comments/{self.parent_entity}?page_size=2"
        )
        data_first = json.loads(response_first_page.content)

        self.assertEqual(response_first_page.status_code, 200)
        self.assertEqual(data_first['comments_count'], 3)
        self.assertEqual(len(data_first['comments']), 2)

    def test_pagination_two_comments_in_page_second_page(self):
        """Test the second page of pagination with page_size = 2."""
        response_second_page = self.client.get(
            f"/api/first-lvl-comments/{self.parent_entity}?page=2&page_size=2"
        )
        data_second = json.loads(response_second_page.content)

        self.assertEqual(response_second_page.status_code, 200)
        self.assertEqual(data_second['comments_count'], 3)
        self.assertEqual(len(data_second['comments']), 1)

    def test_pagination_two_comments_in_page_third_page_exception(self):
        """Test that is not third page at pagination 3 comment by 2 on page."""
        response = self.client.get(
            f"/api/first-lvl-comments/{self.parent_entity}?page=3&page_size=2"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['detail'], "Invalid page.")


class GetFirsLevelCommentsTest(TestCase):
    """Test work custom pagination class 'PaginationComments'."""
    parent_entity = uuid.uuid4()

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 1 child comment for test data.
        """
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        user = User.objects.create(nickname="nick", firstname="Nick")

        Comment.objects.create(
            user=user,
            text='Text',
            parent_entity=cls.parent_entity,
            parent_entity_type=entity_type
        )

    def test_get_first_lvl_comments_data(self):
        """Get first level comments correct data."""
        response = self.client.get(
            f"/api/first-lvl-comments/{self.parent_entity}"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['comments_count'], 1)
        self.assertEqual(len(data['comments']), 1)
        self.assertEqual(data['comments'][0]['text'], 'Text')

    def test_is_not_object_in_db(self):
        """Test there is not object with invalid uuid in db."""
        response = self.client.get(f"/api/first-lvl-comments/{uuid.uuid4()}")
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["comments_count"], 0)
        self.assertEqual(data["comments"], [])


class BadRequestExceptionTest(TestCase):
    """Tests work custom exception class 'BadRequestException'."""

    def test_invalid_uuid_value(self):
        """Processing an invalid value of uuid."""
        response = self.client.get("/api/first-lvl-comments/uuid")
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "Value was not UUID")
