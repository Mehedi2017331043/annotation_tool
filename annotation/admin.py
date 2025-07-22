from django.contrib import admin
from .models import Project, Document, Label, Annotation, Profile

# Register your models here.

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Document)
admin.site.register(Label)
admin.site.register(Annotation)