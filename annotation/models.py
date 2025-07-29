from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, through='ProjectMembership', related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ProjectMembership(models.Model):
    ADMIN = 'admin'
    COLLABORATOR = 'collaborator'
    ROLE_CHOICES = [(ADMIN, 'Admin'), (COLLABORATOR, 'Collaborator')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'project')
        
    def __str__(self):
        return self.user.username

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.TextField()


class Label(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#FFCC00')
    
class Annotation(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()
    suggestions_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Suggestions(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='suggestions_set')
    text = models.TextField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    pass1 = models.CharField(max_length=128)
    pass2 = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username