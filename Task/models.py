from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
  timestamps = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.username



class Organization(models.Model):
  name = models.CharField(max_length=100)
  timestamps = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name


class Team(models.Model):
  name = models.CharField(max_length=100)
  organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="organizations")
  timestamps = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.name



class Project(models.Model):
  name = models.CharField(max_length=100)
  team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team")
  description = models.TextField()
  timestamps = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.name





# User
# id
# name
# email
# password_hash
# timestamps


# Organization
# id
# name
# timestamps

# OrganizationMembership
# user
# organization
# role (Owner, Admin, Member)

# Team
# id
# organization
# name
# timestamps


# Project
# id
# team
# name
# description
# timestamps