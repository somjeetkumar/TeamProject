from django.contrib import admin
from .models import Project,Team,User,Organization

# Register your models here.

admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Team)

