import uuid
from datetime import datetime, timedelta, timezone

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

    def save(self, *args, **kwargs):
        """"Set datetime.now for created_date by default."""
        if not self.created_date:
            self.created_date = datetime.now(tz=timezone(timedelta(hours=0)))
        return super(Comment, self).save(*args, **kwargs)

    def __str__(self):
        return self.text
