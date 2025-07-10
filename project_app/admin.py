from django.contrib import admin
from .models import Project, ProjectMember, Task, Comment
from django.contrib.auth.models import User
# Register your models here.

# admin.site.register(User)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Task)
admin.site.register(Comment)
