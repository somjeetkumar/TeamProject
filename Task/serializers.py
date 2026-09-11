from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import (
    User,
    Organization,
    OrganizationMembership,
    Team,
    TeamMembership,
    Project,
    Task,
    Comment
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        data["user"] = user
        return data


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "timestamps"]
        read_only_fields = ["id", "timestamps"]


class AddOrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = ["user", "role"]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model = OrganizationMembership
        fields = [
            "id", "user", "username", "email",
            "organization", "organization_name",
            "role", "timestamps"
        ]
        read_only_fields = [
            "id", "username", "email", "organization",
            "organization_name", "timestamps"
        ]


class UpdateOrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = ["role"]


class TeamSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model = Team
        fields = [
            "id", "name", "organization",
            "organization_name", "timestamps"
        ]
        read_only_fields = [
            "id", "organization",
            "organization_name", "timestamps"
        ]


class AddTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ["user"]


class TeamMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    team_name = serializers.CharField(
        source="team.name",
        read_only=True
    )

    class Meta:
        model = TeamMembership
        fields = [
            "id", "user", "username", "email",
            "team", "team_name", "timestamps"
        ]
        read_only_fields = [
            "id", "username", "email",
            "team", "team_name", "timestamps"
        ]


class TaskCreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
             "title", "description",
            "status", "priority", "assignee"
        ]




class ProjectSerializer(serializers.ModelSerializer):
    task = TaskCreateProjectSerializer(write_only=True)
    team_name = serializers.CharField(
        source="team.name",
        read_only=True
    )
    tasks = TaskCreateProjectSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = Project
        fields = [
            "id", "name", "description",
            "team", "team_name", "timestamps","task","tasks"
        ]
        read_only_fields = ["id", "team_name", "timestamps","tasks"]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "project", "title", "description",
            "status", "priority", "assignee"
        ]




class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source="project.name",
        read_only=True
    )
    team_name = serializers.CharField(
        source="project.team.name",
        read_only=True
    )
    assignee_username = serializers.CharField(
        source="assignee.username",
        read_only=True,
        allow_null=True
    )
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id", "title", "description",
            "status", "priority",
            "project", "project_name", "team_name",
            "assignee", "assignee_username",
            "created_by", "created_by_username",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "project_name", "team_name",
            "assignee_username", "created_by",
            "created_by_username", "created_at", "updated_at",
        ]





class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]



class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )

    task_title = serializers.CharField(
        source="task.title",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "task_title",
            "author",
            "author_username",
            "content",
            "timestamps",
        ]

        read_only_fields = [
            "id",
            "task",
            "author",
            "author_username",
            "task_title",
            "timestamps",
        ]




#         { 
#   "name":"new_project",
#   "description":"its desc",
#   "team":1,
#   "task":{ 
#     "title":"this is Title",
#     "description":"this is teak desc",
#     "status":"todo",
#     "priority":"low",
#     "assignee":39 }
#     } 