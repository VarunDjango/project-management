from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    path('users/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('users/login/', views.login_user, name='user-login'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    path('projects/<int:project_id>/members/', views.ProjectMemberViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-members-list'),
    path('projects/<int:project_id>/members/<int:pk>/', views.ProjectMemberViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
    ), name='project-member-detail'),
    
    path('projects/<int:project_id>/tasks/', views.ProjectTaskListCreateView.as_view(), name='project-tasks-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    
    path('tasks/<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comments-list'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
]