from rest_framework import permissions
from .models import Project, ProjectMember, Task, Comment

class IsProjectAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if obj.owner == request.user:
            return True
        
        
        try:
            member = ProjectMember.objects.get(project=obj, user=request.user)
            return member.role == 'Admin'
        except ProjectMember.DoesNotExist:
            return False

class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if obj.owner == request.user:
            return True
        
        return ProjectMember.objects.filter(project=obj, user=request.user).exists()

class IsTaskProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        project = obj.project
        if project.owner == request.user:
            return True
        
        return ProjectMember.objects.filter(project=project, user=request.user).exists()

class IsCommentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
