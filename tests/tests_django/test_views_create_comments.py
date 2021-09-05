import json
import uuid

from django.test import TestCase

from comments.models import Comment, EntityType, User


class CreateNewCommentTest(TestCase):
    """Test class for creating new comment."""
    @classmethod
    def setUpTestData(cls):
        """Set up the data for test."""
        EntityType.objects.create(
            name="Another entity", description="Another entity"
        )
        User.objects.create(nickname="bob11", firstname="Bob")

    def test_create_successful_message(self):
        """Tests successful name, message, status in response body."""
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Created")
        self.assertEqual(data["message"], "New comment was created!")
        self.assertEqual(data["status"], 201)

    def test_comment_successfully_saved(self):
        """Tests saving data in database."""
        comments_count_before = Comment.objects.count()
        data_for_saving = {
            "author": "bob11",
            "text": "This is a new comment",
            "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
            "parent_entity_type": "Another entity",
        }
        json_body_data = json.dumps(data_for_saving)
        self.client.generic("POST", "/api/new-comments/", json_body_data)
        comments_count_after = Comment.objects.count()

        self.assertEqual(comments_count_before, 0)
        self.assertEqual(comments_count_after, 1)

    def test_created_comment_consist_author(self):
        """Tests comment's author for created data."""
        data_for_saving = {
            "author": "bob11",
            "text": "This is a new comment",
            "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
            "parent_entity_type": "Another entity",
        }
        json_body_data = json.dumps(data_for_saving)
        self.client.generic("POST", "/api/new-comments/", json_body_data)
        created_comment = Comment.objects.all()[0]

        self.assertEqual(created_comment.user.nickname, "bob11")

    def test_created_comment_consist_text(self):
        """Tests comment's text for created comment."""
        data_for_saving = {
            "author": "bob11",
            "text": "This is a new comment",
            "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
            "parent_entity_type": "Another entity",
        }
        json_body_data = json.dumps(data_for_saving)
        self.client.generic("POST", "/api/new-comments/", json_body_data)
        created_comment = Comment.objects.all()[0]

        self.assertEqual(created_comment.text, "This is a new comment")

    def test_created_comment_consist_parent_entity(self):
        """Tests parent entity for saved comment."""
        data_for_saving = {
            "author": "bob11",
            "text": "This is a new comment",
            "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
            "parent_entity_type": "Another entity",
        }
        json_body_data = json.dumps(data_for_saving)
        self.client.generic("POST", "/api/new-comments/", json_body_data)
        created_comment = Comment.objects.all()[0]

        self.assertEqual(
            created_comment.parent_entity,
            uuid.UUID("ac8abca8-050b-4fa0-8333-53c87a8588b2"),
        )

    def test_created_comment_consist_parent_entity_type(self):
        """Test value parent entity type for saved comment."""
        data_for_saving = {
            "author": "bob11",
            "text": "This is a new comment",
            "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
            "parent_entity_type": "Another entity",
        }
        json_body_data = json.dumps(data_for_saving)
        self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        created_comment = Comment.objects.all()[0]

        self.assertEqual(
            created_comment.parent_entity_type.name, "Another entity"
        )

    def test_not_found_author_key(self):
        """Tests exception's text when 'author' key not found at
        response body.
        """
        json_body_data = json.dumps(
            {
                "": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "The 'author' field was not found!")
        self.assertEqual(data["status"], 400)

    def test_not_found_text_key(self):
        """Tests exception's text when 'text' key not found at
        response body.
        """
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        resp = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(resp.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "The 'text' field was not found!")
        self.assertEqual(data["status"], 400)

    def test_not_found_parent_entity_uuid_key(self):
        """Tests exception's text when 'parent_entity_uuid' key not found
        at response body.
        """
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], "The 'parent_entity_uuid' field was not found!"
        )
        self.assertEqual(data["status"], 400)

    def test_not_found_parent_entity_type_key(self):
        """Tests exception's text when 'parent_entity_type' key not found
        at response body.
        """
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], "The 'parent_entity_type' field was not found!"
        )
        self.assertEqual(data["status"], 400)

    def test_user_not_found_with_uuid(self):
        """Tests exceptions when user not found with uuid value."""
        new_uuid = uuid.uuid4()
        json_body_data = json.dumps(
            {
                "author": str(new_uuid),
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], f"The user '{new_uuid}' was not found"
        )
        self.assertEqual(data["status"], 400)

    def test_user_not_found_with_username(self):
        """Tests exceptions when user not found with username value."""
        new_username = "new_username"
        json_body_data = json.dumps(
            {
                "author": new_username,
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], f"The user '{new_username}' was not found"
        )
        self.assertEqual(data["status"], 400)

    def test_parent_entity_uuid_is_not_uuid(self):
        """Tests key 'parent_entity_uuid' is not uuid type."""
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "not uuid",
                "parent_entity_type": "Another entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], "The parent_entity_uuid must ba uuid"
        )
        self.assertEqual(data["status"], 400)

    def test_parent_entity_type_not_found_with_id(self):
        """Tests parent entity type not found for id."""
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "100",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], "The parent_entity_type was not found"
        )
        self.assertEqual(data["status"], 400)

    def test_parent_entity_type_not_found_with_name(self):
        """Tests parent entity type not found for name."""
        json_body_data = json.dumps(
            {
                "author": "bob11",
                "text": "This is a new comment",
                "parent_entity_uuid": "ac8abca8-050b-4fa0-8333-53c87a8588b2",
                "parent_entity_type": "Not entity",
            }
        )
        response = self.client.generic(
            "POST", "/api/new-comments/", json_body_data
        )
        data = json.loads(response.content)

        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(
            data["message"], "The parent_entity_type was not found"
        )
        self.assertEqual(data["status"], 400)
