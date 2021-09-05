import uuid

from django.db import models


class User(models.Model):
    """Model with users."""

    uuid_user = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nickname = models.CharField(max_length=30, unique=True)
    firstname = models.CharField(max_length=100)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.nickname


class EntityType(models.Model):
    """Model with types of entity."""

    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=80)
    description = models.TextField()

    class Meta:
        verbose_name = "entity type"
        verbose_name_plural = "entity types"

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Model with comments."""

    uuid_comment = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_date = models.DateTimeField()
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="comments"
    )
    text = models.TextField()
    parent_entity = models.UUIDField()
    parent_entity_type = models.ForeignKey(
        EntityType,
        null=True,
        on_delete=models.SET_NULL,
        related_name="comments"
    )

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return self.text
