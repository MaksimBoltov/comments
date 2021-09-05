from django.urls import path

from .views import manage_new_comment

urlpatterns = [
    path("new-comments/", manage_new_comment, name="new_comments")
]
