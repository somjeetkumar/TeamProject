from rest_framework import serializers
from .models import User, Organization,Team,Project




class OrganizationSerializers(serializers.ModelSerializer):
  class Meta:
    model = Organization
    fields = ['name']


class TeamSerializers(serializers.ModelSerializer):
  organization_name = serializers.CharField(source='organization.name',read_only=True)

  organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),write_only=True)
  print(organization_name)
  class Meta:
    model = Team
    fields = ['name','organization','organization_name']





    
class ProjectSerializers(serializers.ModelSerializer):
  team_name = serializers.CharField(source='team.name', read_only=True)
  team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), write_only=True)
  
  class Meta:
    model = Project
    fields = ['name','description','team','team_name']

  