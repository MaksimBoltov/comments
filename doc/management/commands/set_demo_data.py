from datetime import datetime
from uuid import UUID

from django.core.management.base import BaseCommand

from comments.models import Comment, EntityType, User


def create_users():
    """Create User instances for demo example."""

    User.objects.get_or_create(
        uuid_user=UUID("7e3a46ec-65c1-49a3-87b2-60b34c0e14c1"),
        firstname="Ivan",
        nickname="vanya",
    )
    User.objects.get_or_create(
        uuid_user=UUID("871d2d00-c722-45a7-becd-e4332c03e4a5"),
        firstname="Maksim",
        nickname="maksim",
    )
    User.objects.get_or_create(
        uuid_user=UUID("30800c0c-ade9-411f-bdd6-20df13912e7e"),
        firstname="Oleg",
        nickname="oleg",
    )
    User.objects.get_or_create(
        uuid_user=UUID("ef1d5da4-bf29-4e1a-bfe2-5c134c57a362"),
        firstname="User",
        nickname="user",
    )


def create_entity_types():
    """Create EntityType instances for demo example."""

    EntityType.objects.get_or_create(
        id=1,
        name="Comment",
        description="Type of parent entity is comment"
    )
    EntityType.objects.get_or_create(
        id=2,
        name="Another entity",
        description="Type of parent entity is not comment"
    )


def create_comments():
    """Create Comment instances for demo example."""

    vanya = User.objects.get_or_create(
        uuid_user=UUID("7e3a46ec-65c1-49a3-87b2-60b34c0e14c1"),
        firstname="Ivan",
        nickname="vanya",
    )[0]
    maksim = User.objects.get_or_create(
        uuid_user=UUID("871d2d00-c722-45a7-becd-e4332c03e4a5"),
        firstname="Maksim",
        nickname="maksim",
    )[0]
    oleg = User.objects.get_or_create(
        uuid_user=UUID("30800c0c-ade9-411f-bdd6-20df13912e7e"),
        firstname="Oleg",
        nickname="oleg",
    )[0]
    user = User.objects.get_or_create(
        uuid_user=UUID("ef1d5da4-bf29-4e1a-bfe2-5c134c57a362"),
        firstname="User",
        nickname="user",
    )[0]

    comment = EntityType.objects.get_or_create(
        id=1,
        name="Comment",
        description="Type of parent entity is comment"
    )[0]
    no_comment = EntityType.objects.get_or_create(
        id=2,
        name="Another entity",
        description="Type of parent entity is not comment"
    )[0]

    Comment.objects.get_or_create(
        uuid_comment=UUID("d15b567b-2fc6-4ffc-b8bc-19df543d322d"),
        created_date=datetime(2021, 8, 6, 10, 0, 0),
        text="ROOT",
        parent_entity="d15b567b-2fc6-4ffc-b8bc-19df543d311d",
        parent_entity_type=no_comment,
        user=user,
    )

    Comment.objects.get_or_create(
        uuid_comment=UUID("1774b247-8c1a-4dcb-8f43-d0b1a63da7ce"),
        created_date=datetime(2021, 9, 6, 11, 16, 10),
        text="L1 child1",
        parent_entity="d15b567b-2fc6-4ffc-b8bc-19df543d322d",
        parent_entity_type=comment,
        user=maksim,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("21af83e3-bac5-484a-aab1-eb24810d0d8b"),
        created_date=datetime(2021, 9, 6, 11, 19, 11),
        text="L1 child2",
        parent_entity="d15b567b-2fc6-4ffc-b8bc-19df543d322d",
        parent_entity_type=comment,
        user=vanya,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("5272e26c-bb9f-494a-9803-173a635dad41"),
        created_date=datetime(2021, 9, 6, 11, 19, 35),
        text="L1 child3",
        parent_entity="d15b567b-2fc6-4ffc-b8bc-19df543d322d",
        parent_entity_type=comment,
        user=user,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("5a3e0b12-4d65-4290-8323-d3f9a6a8c733"),
        created_date=datetime(2021, 9, 6, 11, 19, 51),
        text="L1 child4",
        parent_entity="d15b567b-2fc6-4ffc-b8bc-19df543d322d",
        parent_entity_type=comment,
        user=oleg,
    )

    Comment.objects.get_or_create(
        uuid_comment=UUID("15aaddb4-64af-4b0d-b509-7605d214a9fd"),
        created_date=datetime(2021, 9, 6, 12, 20, 11),
        text="L2 child1",
        parent_entity="1774b247-8c1a-4dcb-8f43-d0b1a63da7ce",
        parent_entity_type=comment,
        user=oleg,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("60e8a95b-e4ba-4778-aceb-fdb6d1adbc76"),
        created_date=datetime(2021, 9, 6, 12, 20, 32),
        text="L2 child2",
        parent_entity="1774b247-8c1a-4dcb-8f43-d0b1a63da7ce",
        parent_entity_type=comment,
        user=maksim,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("71cd41f3-63cd-4ccb-b996-5dba1e818f1d"),
        created_date=datetime(2021, 9, 6, 12, 20, 57),
        text="L2 child3",
        parent_entity="5a3e0b12-4d65-4290-8323-d3f9a6a8c733",
        parent_entity_type=comment,
        user=vanya,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("8876f65d-3292-4fcd-a73d-66f5cde063c8"),
        created_date=datetime(2021, 9, 6, 13, 21, 27),
        text="L2 child4",
        parent_entity="5a3e0b12-4d65-4290-8323-d3f9a6a8c733",
        parent_entity_type=comment,
        user=user,
    )

    Comment.objects.get_or_create(
        uuid_comment=UUID("52e3317b-0abc-4815-9383-393712c4dd88"),
        created_date=datetime(2021, 9, 7, 14, 21, 50),
        text="L3 child1",
        parent_entity="15aaddb4-64af-4b0d-b509-7605d214a9fd",
        parent_entity_type=comment,
        user=user,
    )
    Comment.objects.get_or_create(
        uuid_comment=UUID("29866969-33e9-4f3c-8a7e-1c281a4a8a78"),
        created_date=datetime(2021, 9, 7, 15, 22, 11),
        text="L3 child2",
        parent_entity="8876f65d-3292-4fcd-a73d-66f5cde063c8",
        parent_entity_type=comment,
        user=user,
    )

    Comment.objects.get_or_create(
        uuid_comment=UUID("83448eb5-9725-4fcd-a5d5-cd74ff524ecb"),
        created_date=datetime(2021, 9, 7, 15, 22, 28),
        text="L4 child",
        parent_entity="52e3317b-0abc-4815-9383-393712c4dd88",
        parent_entity_type=comment,
        user=maksim,
    )


class Command(BaseCommand):
    """Run all function by creating data for demo test."""

    def handle(self, *args, **options):
        create_users()
        create_entity_types()
        create_comments()
