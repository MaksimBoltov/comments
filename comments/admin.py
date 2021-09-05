from django.contrib import admin

from .models import Comment, EntityType, User

admin.site.register(User)
admin.site.register(EntityType)
admin.site.register(Comment)
