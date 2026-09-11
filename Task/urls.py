from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    OrganizationView,
    OrganizationDetailView,
    OrganizationMemberView,
    OrganizationMemberDetailView,
    TeamView,
    TeamDetailView,
    TeamMemberView,
    TeamMemberDetailView,
    ProjectView,
    ProjectDetailView,
    TaskView,
    TaskDetailView,
    TaskCommentView,CommentDetailView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("organizations/", OrganizationView.as_view(), name="organizations"),
    path(
        "organizations/<int:organization_id>/",
        OrganizationDetailView.as_view(),
        name="organization-detail"
    ),

    path(
        "organizations/<int:organization_id>/members/",
        OrganizationMemberView.as_view(),
        name="organization-members"
    ),
    path(
        "organization-members/<int:membership_id>/",
        OrganizationMemberDetailView.as_view(),
        name="organization-member-detail"
    ),

    path(
        "organizations/<int:organization_id>/teams/",
        TeamView.as_view(),
        name="teams"
    ),
    path(
        "teams/<int:team_id>/",
        TeamDetailView.as_view(),
        name="team-detail"
    ),

    path(
        "teams/<int:team_id>/members/",
        TeamMemberView.as_view(),
        name="team-members"
    ),
    path(
        "team-members/<int:membership_id>/",
        TeamMemberDetailView.as_view(),
        name="team-member-detail"
    ),

    path("projects/", ProjectView.as_view(), name="projects"),
    path(
        "projects/<int:project_id>/",
        ProjectDetailView.as_view(),
        name="project-detail"
    ),

    path("tasks/", TaskView.as_view(), name="tasks"),
    path(
        "tasks/<int:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail"
    ),
    path(
    "tasks/<int:task_id>/comments/",
    TaskCommentView.as_view(),
    name="task-comments"
),

path(
    "comments/<int:comment_id>/",
    CommentDetailView.as_view(),
    name="comment-detail"
),
]
