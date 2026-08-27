from django.urls import path
from .views import OrganizationIdView,OrganizationView,TeamView,TeamIdView,PeojectIdView,ProjectView

urlpatterns = [
    path('organizations/',OrganizationView.as_view(), name='organization'),
    path('organization/<int:id>/',OrganizationIdView.as_view(), name='OrganizationId'),

    path('teams/', TeamView.as_view(), name='team'),
    path('team/<int:id>/', TeamIdView.as_view(), name='teamId'),

    path('projects/', ProjectView.as_view(), name='project'),
    path('project/<int:id>/', PeojectIdView.as_view(), name='projectId')

    
]
