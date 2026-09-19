from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Organization(models.Model):
    name = models.CharField(max_length=100)
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="organization_memberships")
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="memberships")
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default="member")
    timestamps = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} - {self.role}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="teams")
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="team_memberships")
    team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="memberships")
    timestamps = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_user_team"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"


class Project(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="projects")
    description = models.TextField(blank=True)
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = (
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    )

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )

    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_tasks")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name="created_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="todo")
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default="medium")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["status"]),
            models.Index(fields=["assignee"]),
        ]

    def __str__(self):
        return self.title





class Comment(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comments")
    content = models.TextField()
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - Task {self.task.id}"
    

# Test@12345


# { "name":"new_project", "description":"its desc", "team":1, "task":{ "title":"this is Title", "description":"this is teak desc", "status":"todo" "priority":"low" "assignee":39 } } { "non_field_errors": [ "Invalid data. Expected a dictionary, but got str." ] }
# {
#   "username":"watkinspaul",
#   "password":"Test@12345"
# }

# http://127.0.0.1:8000/organizations/4/members/


# watkinspaul - 45 task


#  {
#   "project":2,
#    "assignee":5,
#    "title":"hii task",
#    "description":"my task"
#  }