from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from .models import Project, ProjectMember, Task, Comment
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ProjectSerializer, 
    ProjectMemberSerializer, TaskSerializer, CommentSerializer
)
from .permissions import IsProjectAdminOrOwner, IsProjectMember, IsTaskProjectMember, IsCommentOwner


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserRegistrationView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Register a new user with username, email and password",
        responses={201: UserSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        401: 'Invalid credentials'
    },
    operation_description="Login with username and password to receive auth token"
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser() | 
                   (permissions.IsAuthenticated() & (lambda r, v, o: o.id == r.user.id))]
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Get user details",
        responses={200: UserSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update user details",
        responses={200: UserSerializer()}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update user details",
        responses={200: UserSerializer()}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete user account",
        responses={204: 'No content'}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


from drf_yasg.utils import swagger_auto_schema

class ProjectViewSet(viewsets.ModelViewSet):
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProjectAdminOrOwner()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Project.objects.none()

        return Project.objects.filter(
            models.Q(owner=user) | models.Q(members__user=user)
        ).distinct()

        
    @swagger_auto_schema(
        operation_description="List all projects where the user is owner or member",
        responses={200: ProjectSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new project",
        responses={201: ProjectSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve details of a specific project",
        responses={200: ProjectSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update project details",
        responses={200: ProjectSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update project details",
        responses={200: ProjectSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a project",
        responses={204: 'No content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProjectMemberViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectMemberSerializer
    
    def get_queryset(self):
        return ProjectMember.objects.filter(project_id=self.kwargs.get('project_id'))
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProjectAdminOrOwner()]
        return [permissions.IsAuthenticated(), IsProjectMember()]
    
    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs.get('project_id'))
        serializer.save(project=project)


from drf_yasg.utils import swagger_auto_schema

class ProjectTaskListCreateView(generics.ListCreateAPIView):
    
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        return Task.objects.filter(project_id=self.kwargs.get('project_id'))
    
    def get_permissions(self):
        project_id = self.kwargs.get('project_id')
        project = Project.objects.get(id=project_id)
        
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsProjectMember()]
        return [permissions.IsAuthenticated(), IsProjectMember()]
    
    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs.get('project_id'))
        serializer.save(project=project)
    
    @swagger_auto_schema(
        operation_description="List all tasks in a project",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new task in a project",
        request_body=TaskSerializer,
        responses={201: TaskSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsTaskProjectMember()]
        return [permissions.IsAuthenticated(), IsTaskProjectMember()]
    
    @swagger_auto_schema(
        operation_description="Get task details",
        responses={200: TaskSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update task details",
        request_body=TaskSerializer,
        responses={200: TaskSerializer()}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update task details",
        request_body=TaskSerializer,
        responses={200: TaskSerializer()}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a task",
        responses={204: 'No content'}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


from drf_yasg.utils import swagger_auto_schema

class TaskCommentListCreateView(generics.ListCreateAPIView):
    
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs.get('task_id'))
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsTaskProjectMember()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        task = Task.objects.get(id=self.kwargs.get('task_id'))
        serializer.save(task=task, user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="List all comments on a task",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new comment on a task",
        request_body=CommentSerializer,
        responses={201: CommentSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsCommentOwner()]
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Get comment details",
        responses={200: CommentSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update comment details",
        request_body=CommentSerializer,
        responses={200: CommentSerializer()}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update comment details",
        request_body=CommentSerializer,
        responses={200: CommentSerializer()}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a comment",
        responses={204: 'No content'}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)