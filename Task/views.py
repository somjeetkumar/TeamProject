
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    OrganizationSerializer,
    OrganizationMemberSerializer,
    AddOrganizationMemberSerializer,
    UpdateOrganizationMemberSerializer,
    TeamSerializer,
    TeamMemberSerializer,
    AddTeamMemberSerializer,
    ProjectSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    CommentCreateSerializer,
    CommentSerializer
)

from .services import (
    OrganizationService,
    OrganizationMemberService,
    TeamService,
    TeamMemberService,
    ProjectService,
    TaskService,
    CommentService
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {"access": str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"message": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            print("not run")
            return Response(
                {"message": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            print(token," ------------")
            a = token.blacklist()
            print(a, "0------=-=-")
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"message": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            organization = OrganizationService.create_organization(
                request.user, serializer.validated_data
            )
            return Response(
                OrganizationSerializer(organization).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        organizations = OrganizationService.get_all_organizations(
            request.user
        )
        return Response(
            OrganizationSerializer(organizations, many=True).data,
            status=status.HTTP_200_OK
        )


class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_id):
        organization = OrganizationService.get_organization(
            request.user, organization_id
        )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK
        )

    def put(self, request, organization_id):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            organization = OrganizationService.update_organization(
                request.user,
                organization_id,
                serializer.validated_data
            )
            return Response(
                OrganizationSerializer(organization).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, organization_id):
        OrganizationService.delete_organization(
            request.user, organization_id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationMemberView(APIView):
    permission_classes = [IsAuthenticated]



    def get(self, request, organization_id):
    
        cache_key = (
            f"organization_{organization_id}_members"
        )
    
        # 1. Check Redis
        cached_members = cache.get(cache_key)
    
        if cached_members is not None:
            return Response(
                cached_members,
                status=status.HTTP_200_OK
            )
    
        # 2. Cache MISS → Database
        members = OrganizationMemberService.get_all_members(
            request.user,
            organization_id
        )
    
        data = OrganizationMemberSerializer(
            members,
            many=True
        ).data
    
        # 3. Store in Redis
        cache.set(
            cache_key,
            data,
            timeout=60
        )
    
        # 4. Return response
        return Response(
            data,
            status=status.HTTP_200_OK
        )


    
    def post(self, request, organization_id):
        serializer = AddOrganizationMemberSerializer(data=request.data)
        if serializer.is_valid():
            member = OrganizationMemberService.add_member(
                request.user,
                organization_id,
                serializer.validated_data
            )
            return Response(
                OrganizationMemberSerializer(member).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, membership_id):
        serializer = UpdateOrganizationMemberSerializer(data=request.data)
        if serializer.is_valid():
            member = OrganizationMemberService.update_member_role(
                request.user,
                membership_id,
                serializer.validated_data
            )
            return Response(
                OrganizationMemberSerializer(member).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, membership_id):
        OrganizationMemberService.remove_member(
            request.user, membership_id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = TeamService.create_team(
                request.user,
                organization_id,
                serializer.validated_data
            )
            return Response(
                TeamSerializer(team).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, organization_id):
        teams = TeamService.get_all_teams(
            request.user, organization_id
        )
        return Response(
            TeamSerializer(teams, many=True).data,
            status=status.HTTP_200_OK
        )


class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id):
        team = TeamService.get_team(request.user, team_id)
        return Response(
            TeamSerializer(team).data,
            status=status.HTTP_200_OK
        )

    def put(self, request, team_id):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = TeamService.update_team(
                request.user,
                team_id,
                serializer.validated_data
            )
            return Response(
                TeamSerializer(team).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, team_id):
        TeamService.delete_team(request.user, team_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        serializer = AddTeamMemberSerializer(data=request.data)
        if serializer.is_valid():
            member = TeamMemberService.create_member(
                request.user,
                team_id,
                serializer.validated_data
            )
            return Response(
                TeamMemberSerializer(member).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, team_id):
        members = TeamMemberService.get_all_members(
            request.user, team_id
        )
        return Response(
            TeamMemberSerializer(members, many=True).data,
            status=status.HTTP_200_OK
        )


class TeamMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, membership_id):
        TeamMemberService.delete_member(
            request.user, membership_id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = ProjectService.get_all_projects(request.user)
        return Response(
            ProjectSerializer(projects, many=True).data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = ProjectService.create_project(
                request.user,
                serializer.validated_data
            )
            return Response(
                ProjectSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]



    def get(self, request):
    
        cache_key = f"user_{request.user.id}_projects"
    
        cached_projects = cache.get(cache_key)
    
        if cached_projects is not None:
            return Response(
                cached_projects,
                status=status.HTTP_200_OK
            )
    
        projects = ProjectService.get_all_projects(request.user)
    
        data = ProjectSerializer(
            projects,
            many=True
        ).data
    
        cache.set(
            cache_key,
            data,
            timeout=60
        )
    
        return Response(
            data,
            status=status.HTTP_200_OK
        )

    def put(self, request, project_id):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = ProjectService.update_project(
                request.user,
                project_id,
                serializer.validated_data
            )
            return Response(
                ProjectSerializer(project).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        ProjectService.delete_project(request.user, project_id)
        return Response(status=status.HTTP_204_NO_CONTENT)





class TaskFlowPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100




class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = TaskService.get_all_tasks(request.user)
        paginator = TaskFlowPagination()
        page = paginator.paginate_queryset(
            tasks,
            request
        )
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = TaskService.create_task(
                request.user,
                serializer.validated_data
            )
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = TaskService.get_single_task(request.user, task_id)
        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )

    def put(self, request, task_id):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = TaskService.update_task(
                request.user,
                task_id,
                serializer.validated_data
            )
            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        TaskService.delete_task(request.user, task_id)
        return Response(status=status.HTTP_204_NO_CONTENT)







class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):

        comments = CommentService.get_all_comments(
            request.user,
            task_id
        )

        paginator = TaskFlowPagination()
        page = paginator.paginate_queryset(
                    comments,
                    request
                )
        Serializer = CommentSerializer(page, many=True)
        return paginator.get_paginated_response(
            Serializer.data
        )

    def post(self, request, task_id):

        serializer = CommentCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            comment = CommentService.create_comment(
                request.user,
                task_id,
                serializer.validated_data
            )

            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )








class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id):

        serializer = CommentCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            comment = CommentService.update_comment(
                request.user,
                comment_id,
                serializer.validated_data
            )

            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, comment_id):

        CommentService.delete_comment(
            request.user,
            comment_id
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )