import json
import uuid
from datetime import datetime
from uuid import UUID

from django.test import TestCase

from api.services import is_uuid
from comments.models import Comment, EntityType, User


def csv_reader(data: str):
    """Generator of Comment's instance from csv file."""

    for row in data.split('\n'):
        if row == '':
            continue

        uuid, date, user, text, parent, parent_type = row.split(',')
        if uuid == "uuid_comment":
            continue

        if is_uuid(user):
            comment = Comment(
                uuid_comment=UUID(uuid),
                created_date=date,
                user=User.objects.get(uuid_user=user),
                text=text,
                parent_entity=parent,
                parent_entity_type=EntityType.objects.get(
                    name=parent_type.strip()
                ),
            )
        else:
            comment = Comment(
                uuid_comment=UUID(uuid),
                created_date=date,
                user=User.objects.get(nickname=user),
                text=text,
                parent_entity=parent,
                parent_entity_type=EntityType.objects.get(
                    name=parent_type.strip()
                ),
            )

        yield comment


class CommentsHistoryForEntityTest(TestCase):
    """Test filtered and return comments for certain entity."""
    uuid_entity = uuid.uuid4()
    comments_date = [
        datetime.strptime('2000-01-01T08:00:01', "%Y-%m-%dT%H:%M:%S"),
        datetime.strptime('2000-01-01T08:00:10', "%Y-%m-%dT%H:%M:%S")
    ]

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 2 comment with different created date.
        """
        # create type of entity
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        # create user
        user = User.objects.create(
            uuid_user=uuid.uuid4(),
            nickname='nick',
            firstname="Nick"
        )
        # create comments by user
        for comment_date in cls.comments_date:
            Comment.objects.create(
                user=user,
                text='Text',
                created_date=comment_date,
                parent_entity=cls.uuid_entity,
                parent_entity_type=entity_type
            )

    def test_get_all_comments_for_certain_entity(self):
        """Get all comments for certain user with uuid parameter."""
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}"
        )
        data = response.content
        # generate all comments from csv file
        comment_generator = csv_reader(data.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(comment_generator)), 2)

    def test_start_time_threshold_less(self):
        """Test threshold value of start_time.
        Minimum datetime for two comments: 2000-01-01T08:00:01
        Input datetime: 2000-01-01T08:00:00
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}"
            f"&start_date=2000-01-01T08:00:00"
        )
        data = response.content
        # generate all comments from csv file
        comment_generator = csv_reader(data.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(comment_generator)), 2)

    def test_start_time_equal(self):
        """Test threshold value of start_time.
        Minimum datetime for two comments: 2000-01-01T08:00:01
        Input datetime: 2000-01-01T08:00:01
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2000-01-01T08:00:01"
        )
        data = response.content
        # generate all comments from csv file
        comment_generator = csv_reader(data.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(comment_generator)), 2)

    def test_start_time_more(self):
        """Test threshold value of start_time.
        Minimum datetime for two comments: 2000-01-01T08:00:01
        Input datetime: 2000-01-01T08:00:02
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2000-01-01T08:00:02"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].created_date, '2000-01-01 08:00:10+00:00')

    def test_end_time_more(self):
        """Test threshold value of end_time.
        Maximum datetime for two comments: 2000-01-01T08:00:10
        Input end datetime: 2000-01-01T08:00:11
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"end_date=2000-01-01T08:00:11"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 2)

    def test_end_time_equal(self):
        """Test threshold value of end_time.
        Maximum datetime for two comments: 2000-01-01T08:00:10
        Input end datetime: 2000-01-01T08:00:10
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"end_date=2000-01-01T08:00:10"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 2)

    def test_end_time_less(self):
        """Test threshold value of end_time.
        Maximum datetime for two comments: 2000-01-01T08:00:10
        Input end datetime: 2000-01-01T08:00:09
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"end_date=2000-01-01T08:00:09"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].created_date, '2000-01-01 08:00:01+00:00')

    def test_there_are_comments_in_datetime_interval(self):
        """Test interval input.
        There are all two comments inside interval.
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2000-01-01T08:00:00&end_date=2000-01-01T08:00:11"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 2)

    def test_there_is_not_comments_in_datetime_interval(self):
        """Test interval input.
        There are none comments inside interval.
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2000-01-01T08:00:05&end_date=2000-01-01T08:00:06"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 0)

    def test_there_is_one_comments_in_datetime_interval(self):
        """Test interval input.
        There is only one comments inside interval.
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2000-01-01T08:00:00&end_date=2000-01-01T08:00:05"
        )
        data = response.content
        # generate all comments from csv file
        comments = list(csv_reader(data.decode("utf-8")))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].created_date, '2000-01-01 08:00:01+00:00')


class ExceptionHistoryByEntityTest(TestCase):
    """Test filtered and return comments for certain user."""

    uuid_entity = uuid.uuid4()

    @classmethod
    def setUpTestData(cls):
        """Set up the data for test.
        Create 2 comment with different created date.
        """
        # create type of entity
        entity_type = EntityType.objects.create(
            name="Comment", description=""
        )
        # create user
        user = User.objects.create(
            uuid_user=uuid.uuid4(),
            nickname='nick',
            firstname="Nick"
        )
        # create comment by user
        Comment.objects.create(
            user=user,
            text='Text',
            created_date='2000-01-01T08:00:10',
            parent_entity=cls.uuid_entity,
            parent_entity_type=entity_type
        )

    def test_input_incorrect_datetime_start_date(self):
        """Test raise exception 'BadRequestExceptionDatetime' when
        was written incorrect datetime in start_date.
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"start_date=2021.01.01"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "Date you entered is incorrect.")

    def test_input_incorrect_datetime_end_date(self):
        """Test raise exception 'BadRequestExceptionDatetime' when
        was written incorrect datetime in end_date.
        """
        response = self.client.get(
            f"/api/history/entity?entity={self.uuid_entity}&"
            f"end_date=2021.01.01"
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(data["message"], "Date you entered is incorrect.")
