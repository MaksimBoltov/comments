import uuid
from datetime import datetime

import pytest

from api.services import get_date, get_user, is_uuid, is_valid_comment_request
from comments.models import EntityType, User


def test_value_is_uuid():
    """Test that input value is UUID."""
    new_uuid = str(uuid.uuid4())
    assert is_uuid(new_uuid)


def test_value_is_not_uuid():
    """Test that input value is not UUID."""
    assert not is_uuid("is not uuid")


@pytest.mark.parametrize(
    "input_dict",
    [
        {
            "author": "user",
            "text": "text",
            "parent_entity_uuid": str(uuid.uuid4()),
            "parent_entity_type": "Comment",
        }
    ],
)
@pytest.mark.django_db
def test_input_new_comments_dict_is_valid(input_dict):
    """Test correct input data before adding to db."""
    # ready data for test
    User.objects.create(nickname="user", firstname="User")
    EntityType.objects.create(name="Comment")

    result, message = is_valid_comment_request(input_dict)
    assert result and message == ""


@pytest.mark.parametrize(
    "input_dict, error_key",
    [
        (
            {
                "a": "user",
                "text": "text",
                "parent_entity_uuid": str(uuid.uuid4()),
                "parent_entity_type": "Comment",
            },
            "author",
        ),
        (
            {
                "author": "user",
                "t": "text",
                "parent_entity_uuid": str(uuid.uuid4()),
                "parent_entity_type": "Comment",
            },
            "text",
        ),
        (
            {
                "author": "user",
                "text": "text",
                "p": str(uuid.uuid4()),
                "parent_entity_type": "Comment",
            },
            "parent_entity_uuid",
        ),
        (
            {
                "author": "user",
                "text": "text",
                "parent_entity_uuid": str(uuid.uuid4()),
                "p": "Comment",
            },
            "parent_entity_type",
        ),
    ],
)
@pytest.mark.django_db
def test_input_new_comments_invalid_dict_key(input_dict, error_key):
    """Test input with wrong keys."""
    User.objects.create(nickname="user", firstname="User")
    EntityType.objects.create(name="Comment")

    result, message = is_valid_comment_request(input_dict)
    assert not result and message == f"The '{error_key}' field was not found!"


@pytest.mark.parametrize(
    "input_dict",
    [
        {
            "author": "",
            "text": "text",
            "parent_entity_uuid": str(uuid.uuid4()),
            "parent_entity_type": "Comment",
        }
    ],
)
@pytest.mark.parametrize("author_field", ["new_user", str(uuid.uuid4())])
@pytest.mark.django_db
def test_input_new_comments_user_not_found(input_dict, author_field):
    """Test input wrong user data."""
    User.objects.create(nickname="user1", firstname="User")
    EntityType.objects.create(name="Comment")
    input_dict["author"] = author_field
    result, message = is_valid_comment_request(input_dict)

    assert not result and message == f"The user '{author_field}' was not found"


@pytest.mark.parametrize(
    "input_dict",
    [
        {
            "author": "user",
            "text": "text",
            "parent_entity_uuid": "not_uuid_value",
            "parent_entity_type": "Comment",
        }
    ],
)
@pytest.mark.django_db
def test_input_new_comments_parent_entity_is_not_uuid(input_dict):
    """Test input wrong parent_entity_uuid data."""
    User.objects.create(nickname="user", firstname="User")
    EntityType.objects.create(name="Comment")
    result, message = is_valid_comment_request(input_dict)

    assert not result and message == "The parent_entity_uuid must be uuid"


@pytest.mark.parametrize(
    "input_dict",
    [
        {
            "author": "user",
            "text": "text",
            "parent_entity_uuid": "",
            "parent_entity_type": "Comment",
        }
    ],
)
@pytest.mark.parametrize("parent_val_fields", ["C", "10"])
@pytest.mark.django_db
def test_input_new_comments_parent_entity_uuid_is_not_uuid(
    input_dict, parent_val_fields
):
    """Test input wrong parent_entity_uuid data."""
    User.objects.create(nickname="user", firstname="User")
    EntityType.objects.create(name="Comment")
    input_dict["parent_entity_uuid"] = parent_val_fields
    result, message = is_valid_comment_request(input_dict)

    assert not result and message == "The parent_entity_uuid must be uuid"


@pytest.mark.parametrize(
    "input_dict",
    [
        {
            "author": "user",
            "text": "text",
            "parent_entity_uuid": str(uuid.uuid4()),
            "parent_entity_type": "",
        }
    ],
)
@pytest.mark.parametrize("parent_val_fields", ["C", "10"])
@pytest.mark.django_db
def test_input_new_comments_parent_entity_type_not_found(
        input_dict, parent_val_fields
):
    """Test input wrong parent_entity_type data."""
    User.objects.create(nickname="user", firstname="User")
    EntityType.objects.create(name="Comment")
    input_dict["parent_entity_type"] = parent_val_fields
    result, message = is_valid_comment_request(input_dict)

    assert not result and message == "The parent_entity_type was not found"


@pytest.mark.django_db
def test_get_user_user_found_uuid():
    """Test get_user func with input uuid."""
    new_user_uuid = uuid.uuid4()
    created_user = User.objects.create(
        uuid_user=new_user_uuid, nickname="user", firstname="User"
    )
    result_user = get_user(str(new_user_uuid))

    assert result_user == created_user


@pytest.mark.django_db
def test_get_user_user_found_nickname():
    """Test get_user func with input nickname."""
    new_user_nickname = "user"
    created_user = User.objects.create(nickname="user", firstname="User")
    result_user = get_user(new_user_nickname)

    assert result_user == created_user


@pytest.mark.django_db
def test_get_user_user_not_found_uuid():
    """Test get_user func with input uuid."""
    User.objects.create(nickname="user", firstname="User")

    assert get_user(str(uuid.uuid4())) is None


@pytest.mark.django_db
def test_get_user_user_not_found_nickname():
    """Test get_user func with input nickname."""
    User.objects.create(nickname="user", firstname="User")

    assert get_user("another_user") is None


def test_get_date_valid_date_input():
    """Test wit valid str date."""
    assert get_date("2000-01-01T01:01:01") == datetime(2000, 1, 1, 1, 1, 1)


def test_get_date_invalid_date_input():
    """Test wit valid str date."""
    assert get_date("2000.0.0") is None
