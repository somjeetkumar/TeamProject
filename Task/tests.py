from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    Organization,
    OrganizationMembership,
    Team,
    TeamMembership,
    Project,
    Task,
)


User = get_user_model()


class TaskFlowAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Users
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="Password123"
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="Password123"
        )

        self.member = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="Password123"
        )

        self.other_member = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="Password123"
        )

        # Organization
        self.organization = Organization.objects.create(
            name="TaskFlow"
        )

        # Organization memberships
        OrganizationMembership.objects.create(
            user=self.owner,
            organization=self.organization,
            role="owner"
        )

        OrganizationMembership.objects.create(
            user=self.admin,
            organization=self.organization,
            role="admin"
        )

        OrganizationMembership.objects.create(
            user=self.member,
            organization=self.organization,
            role="member"
        )

        OrganizationMembership.objects.create(
            user=self.other_member,
            organization=self.organization,
            role="member"
        )

        # Teams
        self.team = Team.objects.create(
            name="Backend Team",
            organization=self.organization
        )

        self.other_team = Team.objects.create(
            name="Frontend Team",
            organization=self.organization
        )

        # Team memberships
        TeamMembership.objects.create(
            user=self.member,
            team=self.team
        )

        TeamMembership.objects.create(
            user=self.other_member,
            team=self.other_team
        )

        # Projects
        self.project = Project.objects.create(
            name="Backend API",
            team=self.team,
            description="Backend project"
        )

        self.other_project = Project.objects.create(
            name="Frontend App",
            team=self.other_team,
            description="Frontend project"
        )

    # --------------------------------------------------
    # Helper
    # --------------------------------------------------

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    def test_user_registration(self):
        # response = self.client.post(
        #     reverse("register"),
        #     {
        #         "username": "newuser",
        #         "email": "new@test.com",
        #         "password": "Password123"
        #     }
        # )
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "Password123",
                "password2": "Password123"
            }
        )
        # self.assertEqual(
        #     response.status_code,
        #     status.HTTP_201_CREATED
        # )

        print(response.data)
        
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

    def test_user_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "owner",
                "password": "Password123"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # --------------------------------------------------
    # ORGANIZATION
    # --------------------------------------------------

    def test_owner_can_view_organization(self):
        self.authenticate(self.owner)

        response = self.client.get(
            reverse(
                "organization-detail",
                kwargs={
                    "organization_id": self.organization.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_member_can_view_organization(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "organization-detail",
                kwargs={
                    "organization_id": self.organization.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_cannot_delete_organization(self):
        self.authenticate(self.admin)

        response = self.client.delete(
            reverse(
                "organization-detail",
                kwargs={
                    "organization_id": self.organization.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_owner_can_delete_organization(self):
        self.authenticate(self.owner)

        response = self.client.delete(
            reverse(
                "organization-detail",
                kwargs={
                    "organization_id": self.organization.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    # --------------------------------------------------
    # ORGANIZATION MEMBERSHIP
    # --------------------------------------------------

    def test_owner_can_add_organization_member(self):
        new_user = User.objects.create_user(
            username="newmember",
            email="newmember@test.com",
            password="Password123"
        )

        self.authenticate(self.owner)

        response = self.client.post(
            reverse(
                "organization-members",
                kwargs={
                    "organization_id": self.organization.id
                }
            ),
            {
                "user": new_user.id,
                "role": "member"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=new_user,
                organization=self.organization
            ).exists()
        )

    def test_member_cannot_add_organization_member(self):
        new_user = User.objects.create_user(
            username="newmember2",
            email="newmember2@test.com",
            password="Password123"
        )

        self.authenticate(self.member)

        response = self.client.post(
            reverse(
                "organization-members",
                kwargs={
                    "organization_id": self.organization.id
                }
            ),
            {
                "user": new_user.id,
                "role": "member"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------
    # TEAM
    # --------------------------------------------------

    def test_admin_can_create_team(self):
        self.authenticate(self.admin)

        response = self.client.post(
            reverse(
                "teams",
                kwargs={
                    "organization_id": self.organization.id
                }
            ),
            {
                "name": "DevOps Team"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Team.objects.filter(
                name="DevOps Team",
                organization=self.organization
            ).exists()
        )

    def test_member_cannot_create_team(self):
        self.authenticate(self.member)

        response = self.client.post(
            reverse(
                "teams",
                kwargs={
                    "organization_id": self.organization.id
                }
            ),
            {
                "name": "New Team"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_member_can_view_own_team(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "team-detail",
                kwargs={
                    "team_id": self.team.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_member_cannot_view_other_team(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "team-detail",
                kwargs={
                    "team_id": self.other_team.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------
    # TEAM MEMBERSHIP
    # --------------------------------------------------

    def test_admin_can_add_team_member(self):
        self.authenticate(self.admin)

        response = self.client.post(
            reverse(
                "team-members",
                kwargs={
                    "team_id": self.team.id
                }
            ),
            {
                "user": self.other_member.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                user=self.other_member,
                team=self.team
            ).exists()
        )

    def test_member_cannot_add_team_member(self):
        new_user = User.objects.create_user(
            username="teamuser",
            email="teamuser@test.com",
            password="Password123"
        )

        OrganizationMembership.objects.create(
            user=new_user,
            organization=self.organization,
            role="member"
        )

        self.authenticate(self.member)

        response = self.client.post(
            reverse(
                "team-members",
                kwargs={
                    "team_id": self.team.id
                }
            ),
            {
                "user": new_user.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------
    # PROJECT
    # --------------------------------------------------

    def test_owner_can_create_project(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("projects"),
            {
                "name": "New Project",
                "team": self.team.id,
                "description": "New project"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_member_cannot_create_project(self):
        self.authenticate(self.member)

        response = self.client.post(
            reverse("projects"),
            {
                "name": "Member Project",
                "team": self.team.id,
                "description": "Should fail"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_member_can_view_own_team_project(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "project-detail",
                kwargs={
                    "project_id": self.project.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_member_cannot_view_other_team_project(self):
        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "project-detail",
                kwargs={
                    "project_id": self.other_project.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------
    # TASK
    # --------------------------------------------------

    def test_member_can_create_task_in_own_team(self):
        self.authenticate(self.member)

        response = self.client.post(
            reverse("tasks"),
            {
                "project": self.project.id,
                "title": "Create API",
                "description": "Create API endpoint",
                "status": "todo",
                "priority": "high",
                "assignee": self.member.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Task.objects.filter(
                title="Create API"
            ).exists()
        )

    def test_member_cannot_create_task_in_other_team(self):
        self.authenticate(self.member)

        response = self.client.post(
            reverse("tasks"),
            {
                "project": self.other_project.id,
                "title": "Other Team Task",
                "description": "Should fail",
                "status": "todo",
                "priority": "medium",
                "assignee": self.member.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_member_cannot_assign_task_to_user_outside_team(self):
        self.authenticate(self.member)

        response = self.client.post(
            reverse("tasks"),
            {
                "project": self.project.id,
                "title": "Invalid Assignment",
                "description": "Invalid assignee",
                "status": "todo",
                "priority": "medium",
                "assignee": self.other_member.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_owner_can_create_task(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("tasks"),
            {
                "project": self.project.id,
                "title": "Owner Task",
                "description": "Created by owner",
                "status": "todo",
                "priority": "high",
                "assignee": self.member.id
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_member_can_view_own_team_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Backend Task",
            description="Test task",
            status="todo",
            priority="medium",
            assignee=self.member,
            created_by=self.member
        )

        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "task-detail",
                kwargs={
                    "task_id": task.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_member_cannot_view_other_team_task(self):
        task = Task.objects.create(
            project=self.other_project,
            title="Frontend Task",
            description="Other team task",
            status="todo",
            priority="medium",
            assignee=self.other_member,
            created_by=self.other_member
        )

        self.authenticate(self.member)

        response = self.client.get(
            reverse(
                "task-detail",
                kwargs={
                    "task_id": task.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # --------------------------------------------------
    # TASK DELETE
    # --------------------------------------------------

    def test_member_can_delete_own_task(self):
        task = Task.objects.create(
            project=self.project,
            title="My Task",
            description="Created by member",
            status="todo",
            priority="medium",
            assignee=self.member,
            created_by=self.member
        )

        self.authenticate(self.member)

        response = self.client.delete(
            reverse(
                "task-detail",
                kwargs={
                    "task_id": task.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Task.objects.filter(id=task.id).exists()
        )

    def test_member_cannot_delete_other_members_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Other Member Task",
            description="Created by other member",
            status="todo",
            priority="medium",
            assignee=self.member,
            created_by=self.other_member
        )

        self.authenticate(self.member)

        response = self.client.delete(
            reverse(
                "task-detail",
                kwargs={
                    "task_id": task.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_delete_task(self):
        task = Task.objects.create(
            project=self.project,
            title="Admin Delete Task",
            description="Test",
            status="todo",
            priority="medium",
            assignee=self.member,
            created_by=self.member
        )

        self.authenticate(self.admin)

        response = self.client.delete(
            reverse(
                "task-detail",
                kwargs={
                    "task_id": task.id
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )