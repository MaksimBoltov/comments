from django.urls import path

from .views import (CommentsListView, CommentsUserHistoryListView,
                    CSVEntityViewSet, CSVUserViewSet,
                    manage_all_child_comments, manage_new_comment)

urlpatterns = [
    path("new-comments/", manage_new_comment, name="new_comments"),
    path("first-lvl-comments", CommentsListView.as_view()),
    path("history-comments", CommentsUserHistoryListView.as_view()),
    path("history/user", CSVUserViewSet.as_view()),
    path("history/entity", CSVEntityViewSet.as_view()),
    path("child-comments", manage_all_child_comments, name='all_child')
]
