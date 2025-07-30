from django.contrib import admin
from .models import Project, Document, Label, Annotation, Profile, ProjectMembership

# Register your models here.

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'is_active']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'first_name', 'last_name', 'email', 'created_at', 'updated_at']

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['project', 'text']

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'label', 'suggestions_text']
    
class LabelAdmin(admin.ModelAdmin):
    list_display = ['creator_list', 'project', 'text', 'color']
    
    def creator_list(self, obj):
        return ", ".join([user.username for user in obj.project.users.all()])
    
    creator_list.short_description = 'Creators'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('project') # This  is trigger object fild in Label model
    
class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMembershipInline]
    list_display = ['users_list', 'name', 'description', 'created_at', 'updated_at']
    
    def users_list(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    users_list.short_description = 'Users'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('users') # This  is trigger object fild in Project model
    
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)

