from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import TeamSerializers,ProjectSerializers,OrganizationSerializers
from .models import Organization,Team,Project,User
# Create your views here.

class OrganizationView(APIView):
  def post(self,request):
    serializers = OrganizationSerializers(data=request.data)
    if serializers.is_valid():
      serializers.save()
      return Response({"message":"Organization is created successgulle"},status=status.HTTP_201_CREATED)
    return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


  def get(self,request):
    organizations = Organization.objects.all()
    return Response(OrganizationSerializers(organizations, many=True).data,status=status.HTTP_200_OK)



class OrganizationIdView(APIView):
  def put(self,request,id):
    try:
      organization = Organization.objects.get(id=id)
    except Organization.DoesNotExist:
       return Response({"error": "Organization not found"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrganizationSerializers(organization, data=request.data)

    if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    


  def get(self,request,id):
    try:
      organization = Organization.objects.get(id=id)
    except Organization.DoesNotExist:
       return Response({"error": "Organization not found"},status=status.HTTP_404_NOT_FOUND)
    
    return Response(OrganizationSerializers(organization).data,status=status.HTTP_200_OK)

    








class TeamView(APIView):
  def post(self,request):
    serializers = TeamSerializers(data=request.data)
    if serializers.is_valid():
      serializers.save()
      return Response({"message":"Team is created successgulle"},status=status.HTTP_201_CREATED)
    return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


  def get(self,request):
    team = Team.objects.all()
    return Response(TeamSerializers(team, many=True).data,status=status.HTTP_200_OK)



class TeamIdView(APIView):
  def put(self,request,id):
    try:
      team = team.objects.get(id=id)
    except Team.DoesNotExist:
       return Response({"error": "Organization not found"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = TeamSerializers(team, data=request.data)

    if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    


  def get(self,request,id):
    try:
      team = Team.objects.get(id=id)
    except Team.DoesNotExist:
       return Response({"error": "team not found"},status=status.HTTP_404_NOT_FOUND)
    
    return Response(TeamSerializers(team).data,status=status.HTTP_200_OK)

    







class ProjectView(APIView):
  def post(self,request):
    serializers = ProjectSerializers(data=request.data)
    if serializers.is_valid():
      serializers.save()
      return Response({"message":"Project is created successgulle"},status=status.HTTP_201_CREATED)
    return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


  def get(self,request):
    project = Project.objects.all()
    return Response(ProjectSerializers(project, many=True).data,status=status.HTTP_200_OK)



class PeojectIdView(APIView):
  def put(self,request,id):
    try:
      project = Project.objects.get(id=id)
    except Project.DoesNotExist:
       return Response({"error": "Organization not found"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProjectSerializers(project, data=request.data)

    if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    


  def get(self,request,id):
    try:
      project = Project.objects.get(id=id)
    except Project.DoesNotExist:
       return Response({"error": "Organization not found"},status=status.HTTP_404_NOT_FOUND)
    
    return Response(ProjectSerializers(project).data,status=status.HTTP_200_OK)

    
