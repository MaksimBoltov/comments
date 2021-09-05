import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from rest_framework.decorators import api_view
from rest_framework.response import Response

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

        # checking the validity of the data
        data = json.loads(request.body)
        valid_data, exception_message = is_valid_comment_request(data)
        if not valid_data:
            response = {
                "name": "Bad Request",
                "message": exception_message,
                "status": 400,
            }
            return Response(response, status=400)

        # adding new comment to DB
        if is_uuid(data["author"]):
            comment = Comment(
                created_date=datetime.now(tz=timezone(timedelta(hours=0))),
                user=User.objects.get(uuid_user=data["author"]),
                text=data["text"],
                parent_entity=UUID(data["parent_entity_uuid"]),
                parent_entity_type=EntityType.objects.get(
                    name=data["parent_entity_type"]
                ),
            )
            comment.save()
        else:
            comment = Comment(
                created_date=datetime.now(tz=timezone(timedelta(hours=0))),
                user=User.objects.get(nickname=data["author"]),
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
