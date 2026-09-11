from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import (
    Organization,
    OrganizationMembership,
    Team,
    TeamMembership,
    Project,
    Task,
    Comment
)
from .permissions import check_permission


class OrganizationService:
    @staticmethod
    def get_all_organizations(user):
        return Organization.objects.filter(
            memberships__user=user
        ).distinct()

    @staticmethod
    def create_organization(user, data):
        with transaction.atomic():
            organization = Organization.objects.create(**data)
            OrganizationMembership.objects.create(
                user=user,
                organization=organization,
                role="owner"
            )
        return organization

    @staticmethod
    def get_organization(user, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")
        check_permission(user, organization, "Organization", "view")
        return organization

    @staticmethod
    def update_organization(user, organization_id, data):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")
        check_permission(user, organization, "Organization", "update")
        for field, value in data.items():
            setattr(organization, field, value)
        organization.save()
        return organization

    @staticmethod
    def delete_organization(user, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")
        check_permission(user, organization, "Organization", "delete")
        organization.delete()
        return True


class OrganizationMemberService:
    @staticmethod
    def get_all_members(user, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")
        check_permission(
            user, organization, "OrganizationMembership", "view"
        )
        return OrganizationMembership.objects.filter(
            organization=organization
        ).select_related("user", "organization")

    @staticmethod
    def add_member(user, organization_id, data):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")

        requester = check_permission(
            user, organization, "OrganizationMembership", "create"
        )
        new_user = data["user"]
        role = data.get("role", "member")

        if role == "owner":
            if requester.role != "owner":
                raise PermissionDenied(
                    "Only the Owner can assign the Owner role."
                )
            raise ValidationError(
                "Use ownership transfer logic to assign Owner."
            )

        if OrganizationMembership.objects.filter(
            user=new_user,
            organization=organization
        ).exists():
            raise ValidationError(
                "User is already a member of this organization."
            )

        return OrganizationMembership.objects.create(
            user=new_user,
            organization=organization,
            role=role
        )

    @staticmethod
    def update_member_role(user, membership_id, data):
        try:
            membership = OrganizationMembership.objects.select_related(
                "organization", "user"
            ).get(id=membership_id)
        except OrganizationMembership.DoesNotExist:
            raise NotFound("Organization membership not found.")

        requester = check_permission(
            user,
            membership.organization,
            "OrganizationMembership",
            "update"
        )
        new_role = data["role"]

        if membership.role == "owner":
            if requester.role != "owner":
                raise PermissionDenied(
                    "Admin cannot modify the Owner."
                )
            raise ValidationError(
                "Use ownership transfer logic to change Owner."
            )

        if new_role == "owner":
            if requester.role != "owner":
                raise PermissionDenied(
                    "Only the Owner can assign the Owner role."
                )
            raise ValidationError(
                "Use ownership transfer logic to assign Owner."
            )

        membership.role = new_role
        membership.save(update_fields=["role"])
        return membership

    @staticmethod
    def remove_member(user, membership_id):
        try:
            membership = OrganizationMembership.objects.select_related(
                "organization", "user"
            ).get(id=membership_id)
        except OrganizationMembership.DoesNotExist:
            raise NotFound("Organization membership not found.")

        requester = check_permission(
            user,
            membership.organization,
            "OrganizationMembership",
            "delete"
        )

        if membership.role == "owner":
            if requester.role != "owner":
                raise PermissionDenied(
                    "Admin cannot remove the Owner."
                )
            raise PermissionDenied(
                "Owner cannot be removed. Transfer ownership first."
            )

        membership.delete()
        return True


class TeamService:
    @staticmethod
    def get_all_teams(user, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")

        membership = check_permission(
            user, organization, "Team", "view"
        )

        if membership.role == "member":
            return Team.objects.filter(
                organization=organization,
                memberships__user=user
            ).distinct()

        return Team.objects.filter(organization=organization)

    @staticmethod
    def create_team(user, organization_id, data):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")

        check_permission(user, organization, "Team", "create")
        return Team.objects.create(
            organization=organization,
            **data
        )

    @staticmethod
    def get_team(user, team_id):
        try:
            team = Team.objects.select_related("organization").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        membership = check_permission(
            user, team.organization, "Team", "view"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user, team=team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this team."
                )

        return team

    @staticmethod
    def update_team(user, team_id, data):
        try:
            team = Team.objects.select_related("organization").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        check_permission(
            user, team.organization, "Team", "update"
        )

        for field, value in data.items():
            setattr(team, field, value)

        team.save()
        return team

    @staticmethod
    def delete_team(user, team_id):
        try:
            team = Team.objects.select_related("organization").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        check_permission(
            user, team.organization, "Team", "delete"
        )
        team.delete()
        return True


class TeamMemberService:
    @staticmethod
    def create_member(user, team_id, data):
        try:
            team = Team.objects.select_related("organization").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        check_permission(
            user, team.organization, "TeamMembership", "create"
        )

        new_user = data["user"]

        if not OrganizationMembership.objects.filter(
            user=new_user,
            organization=team.organization
        ).exists():
            raise ValidationError(
                "User must be a member of the same organization."
            )

        if TeamMembership.objects.filter(
            user=new_user,
            team=team
        ).exists():
            raise ValidationError(
                "User is already a member of this team."
            )

        return TeamMembership.objects.create(
            user=new_user,
            team=team
        )

    @staticmethod
    def get_all_members(user, team_id):
        try:
            team = Team.objects.select_related("organization").get(id=team_id)
        except Team.DoesNotExist:
            raise NotFound("Team not found.")

        check_permission(
            user, team.organization, "TeamMembership", "view"
        )

        return TeamMembership.objects.filter(
            team=team
        ).select_related("user", "team")

    @staticmethod
    def delete_member(user, membership_id):
        try:
            membership = TeamMembership.objects.select_related(
                "team", "team__organization"
            ).get(id=membership_id)
        except TeamMembership.DoesNotExist:
            raise NotFound("Team membership not found.")

        check_permission(
            user,
            membership.team.organization,
            "TeamMembership",
            "delete"
        )

        membership.delete()
        return True


class ProjectService:
    @staticmethod
    def get_all_projects(user):
        owner_admin_org_ids = OrganizationMembership.objects.filter(
            user=user,
            role__in=["owner", "admin"]
        ).values_list("organization_id", flat=True)

        member_team_ids = TeamMembership.objects.filter(
            user=user
        ).values_list("team_id", flat=True)

        return Project.objects.filter(
            Q(team__organization_id__in=owner_admin_org_ids)
            | Q(team_id__in=member_team_ids)
        ).distinct()

    @staticmethod
    def create_project(user, data):
        team = data.get("team")

        if not team:
            raise ValidationError("Team is required.")

        check_permission(
            user, team.organization, "Project", "create"
        )
        with transaction.atomic():
            project = Project.objects.create(
                name =data["name"],
                description = data["description"],
                team=data["team"],
                )

            assignee = data["task"]["assignee"]

            if assignee:
                if not TeamMembership.objects.filter(
                    user=assignee,
                    team=project.team
                ).exists():
                    raise ValidationError(
                        "Assignee must be a member of the project's team."
                    )

            Task.objects.create(
                project=project,
                title=data["task"]["title"],
                description=data["task"]["description"],
                status = data["task"]["status"],
                priority=data["task"]["priority"],
                assignee=data["task"]["assignee"],
                created_by=user,

            )
        return project

    @staticmethod
    def get_project(user, project_id):
        try:
            project = Project.objects.select_related(
                "team", "team__organization"
            ).get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")

        membership = check_permission(
            user,
            project.team.organization,
            "Project",
            "view"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user, team=project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this project team."
                )

        return project

    @staticmethod
    def update_project(user, project_id, data):
        try:
            project = Project.objects.select_related(
                "team", "team__organization"
            ).get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")

        check_permission(
            user, project.team.organization, "Project", "update"
        )

        for field, value in data.items():
            setattr(project, field, value)

        project.save()
        return project

    @staticmethod
    def delete_project(user, project_id):
        try:
            project = Project.objects.select_related(
                "team", "team__organization"
            ).get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")

        check_permission(
            user, project.team.organization, "Project", "delete"
        )
        project.delete()
        return True


class TaskService:
    @staticmethod
    def get_all_tasks(user):
        owner_admin_org_ids = OrganizationMembership.objects.filter(
            user=user,
            role__in=["owner", "admin"]
        ).values_list("organization_id", flat=True)

        member_team_ids = TeamMembership.objects.filter(
            user=user
        ).values_list("team_id", flat=True)

        return Task.objects.select_related(
            "project",
            "project__team",
            "project__team__organization",
            "assignee",
            "created_by"
        ).filter(
            Q(project__team__organization_id__in=owner_admin_org_ids)
            | Q(project__team_id__in=member_team_ids)
        ).distinct()

    @staticmethod
    def get_single_task(user, task_id):
        try:
            task = Task.objects.select_related(
                "project",
                "project__team",
                "project__team__organization",
                "assignee",
                "created_by"
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        membership = check_permission(
            user,
            task.project.team.organization,
            "Task",
            "view"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=task.project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this task's team."
                )

        return task

    @staticmethod
    def create_task(user, data):
        project = data.get("project")

        if not project:
            raise ValidationError("Project is required.")

        membership = check_permission(
            user,
            project.team.organization,
            "Task",
            "create"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this project team."
                )

        assignee = data.get("assignee")

        if assignee:
            if not TeamMembership.objects.filter(
                user=assignee,
                team=project.team
            ).exists():
                raise ValidationError(
                    "Assignee must be a member of the project's team."
                )

        return Task.objects.create(
            created_by=user,
            **data
        )

    @staticmethod
    def update_task(user, task_id, data):
        try:
            task = Task.objects.select_related(
                "project",
                "project__team",
                "project__team__organization"
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        membership = check_permission(
            user,
            task.project.team.organization,
            "Task",
            "update"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=task.project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this task's team."
                )

        new_project = data.get("project", task.project)

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=new_project.team
            ).exists():
                raise PermissionDenied(
                    "You cannot move the task to another team."
                )

        new_assignee = data.get("assignee", task.assignee)

        if new_assignee:
            if not TeamMembership.objects.filter(
                user=new_assignee,
                team=new_project.team
            ).exists():
                raise ValidationError(
                    "Assignee must be a member of the project's team."
                )

        for field, value in data.items():
            setattr(task, field, value)

        task.save()
        return task

    @staticmethod
    def delete_task(user, task_id):
        try:
            task = Task.objects.select_related(
                "project",
                "project__team",
                "project__team__organization"
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        membership = check_permission(
            user,
            task.project.team.organization,
            "Task",
            "delete"
        )

        if membership.role in ["owner", "admin"]:
            task.delete()
            return True

        if not TeamMembership.objects.filter(
            user=user,
            team=task.project.team
        ).exists():
            raise PermissionDenied(
                "You are not a member of this task's team."
            )

        if task.created_by != user:
            raise PermissionDenied(
                "You can only delete tasks created by you."
            )

        task.delete()
        return True







class CommentService:

    @staticmethod
    def get_all_comments(user, task_id):
        try:
            task = Task.objects.select_related(
                "project",
                "project__team",
                "project__team__organization"
            ).get(id=task_id)

        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        membership = check_permission(
            user,
            task.project.team.organization,
            "Comment",
            "view"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=task.project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this task's team."
                )

        return Comment.objects.filter(
            task=task
        ).select_related("author", "task")


    @staticmethod
    def create_comment(user, task_id, data):

        try:
            task = Task.objects.select_related(
                "project",
                "project__team",
                "project__team__organization"
            ).get(id=task_id)

        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        membership = check_permission(
            user,
            task.project.team.organization,
            "Comment",
            "create"
        )

        if membership.role == "member":
            if not TeamMembership.objects.filter(
                user=user,
                team=task.project.team
            ).exists():
                raise PermissionDenied(
                    "You are not a member of this task's team."
                )

        return Comment.objects.create(
            task=task,
            author=user,
            content=data["content"]
        )


    @staticmethod
    def update_comment(user, comment_id, data):

        try:
            comment = Comment.objects.select_related(
                "task",
                "task__project",
                "task__project__team",
                "task__project__team__organization",
                "author"
            ).get(id=comment_id)

        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        membership = check_permission(
            user,
            comment.task.project.team.organization,
            "Comment",
            "update"
        )

        if membership.role == "member":
            if comment.author != user:
                raise PermissionDenied(
                    "You can only update your own comments."
                )

        comment.content = data["content"]
        comment.save(update_fields=["content"])

        return comment


    @staticmethod
    def delete_comment(user, comment_id):

        try:
            comment = Comment.objects.select_related(
                "task",
                "task__project",
                "task__project__team",
                "task__project__team__organization",
                "author"
            ).get(id=comment_id)

        except Comment.DoesNotExist:
            raise NotFound("Comment not found.")

        membership = check_permission(
            user,
            comment.task.project.team.organization,
            "Comment",
            "delete"
        )

        if membership.role == "member":
            if comment.author != user:
                raise PermissionDenied(
                    "You can only delete your own comments."
                )

        comment.delete()

        return True