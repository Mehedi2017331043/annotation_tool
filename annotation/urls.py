from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('register/', views.register, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/import/', views.import_documents, name='import_documents'),
    path('projects/<int:pk>/add_label/', views.add_label, name='add_label'),
    path('projects/<int:project_pk>/documents/<int:doc_pk>/annotate/', views.annotate, name='annotate'),
    path('projects/<int:pk>/export/csv/', views.export_annotations_csv, name='export_annotations_csv'),
    path('projects/<int:pk>/export/json/', views.export_annotations_json, name='export_annotations_json'),
    path('projects/<int:project_pk>/annotations/', views.annotation_list, name='annotation_list'),
    path('annotations/<int:annotation_id>/edit/', views.annotation_edit, name='annotation_edit'),
    path('annotations/<int:annotation_id>/delete/', views.annotation_delete, name='annotation_delete'),
] 