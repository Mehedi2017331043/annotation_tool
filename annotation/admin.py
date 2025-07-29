from django.contrib import admin
from .models import Project, Document, Label, Annotation, Profile, ProjectMembership

# Register your models here.

admin.site.register(Profile)
admin.site.register(Document)
admin.site.register(Label)
admin.site.register(Annotation)
admin.site.register(ProjectMembership)


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMembershipInline]
    list_display = ['name', 'description', 'created_at', 'updated_at']