import uuid

from api.services import is_uuid


def test_value_is_uuid():
    new_uuid = str(uuid.uuid4())
    assert is_uuid(new_uuid)


def test_value_is_not_uuid():
    assert not is_uuid("is not uuid")
