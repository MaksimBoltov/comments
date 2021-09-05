from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from comments.models import Comment


class CommentListSerializer(ModelSerializer):
    """Serializer class for model 'Comment'"""

    user = serializers.SlugRelatedField(slug_field='nickname', read_only=True)
    parent_entity_type = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = "__all__"
