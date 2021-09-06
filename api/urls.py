from django.urls import path

from .views import (CommentsListView, CommentsUserHistoryListView,
                    CSVEntityViewSet, CSVUserViewSet, manage_new_comment)

urlpatterns = [
    path("new-comments/", manage_new_comment, name="new_comments"),
    path("first-lvl-comments/<str:uuid>", CommentsListView.as_view()),
    path("history-comments/<str:user>", CommentsUserHistoryListView.as_view()),
    path("history/user/<str:user>", CSVUserViewSet.as_view()),
    path("history/entity/<str:uuid>", CSVEntityViewSet.as_view())
]
