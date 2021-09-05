from django.urls import path

from . import views
from .views import manage_new_comment

urlpatterns = [
    path("new-comments/", manage_new_comment, name="new_comments"),
    path("first-lvl-comments/<str:uuid>", views.CommentsListView.as_view())
]
