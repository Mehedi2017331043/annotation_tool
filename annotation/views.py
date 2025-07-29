from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Document, Label, Annotation, Profile, Suggestions
from .forms import ProjectForm, DocumentImportForm, LabelForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import csv
import json


def home_page(request):
    return render(request, 'annotation/home.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('project_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def Logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('pass1')
        new_user = User.objects.create_user(username=username, password=password)
        new_user.email = email
        new_user.first_name = first_name        
        new_user.last_name = last_name
        new_user.save()
        new_profile = Profile.objects.create(
            user=new_user,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        new_profile.save()
        return redirect('login')
    return render(request, 'registration/register.html')


@login_required
def project_list(request):
    projects = request.user.projects.all()
    return render(request, 'annotation/project_list.html', {'projects': projects})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    return render(request, 'annotation/project_delete.html', {'project': project})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.description = request.POST.get('project_description', '')
        project.name = request.POST.get('project_name', project.name)
        project.save()
        messages.success(request, 'Project updated successfully.')
        return redirect('project_list')
    return render(request, 'annotation/project_edit.html', {'project': project})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            project.users.add(request.user)
            messages.success(request, 'Project created successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'annotation/project_create.html', {'form': form})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    documents = Document.objects.filter(project=project)
    annotations = Annotation.objects.filter(document__project=project)
    labels = Label.objects.filter(project=project)
    annotated_doc_ids = set(annotations.values_list('document_id', flat=True))
    return render(request, 'annotation/project_detail.html', {
        'project': project, 'documents': documents, 'labels': labels, 
        'annotated_doc_ids': annotated_doc_ids,
    })
    
    
@login_required
def import_documents(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = DocumentImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            lines = file.read().decode('utf-8').splitlines()
            for line in lines:
                if line.strip():
                    Document.objects.create(project=project, text=line.strip())
            messages.success(request, "Documents imported!")
            return redirect('project_detail', pk=pk)
    else:
        form = DocumentImportForm()
    return render(request, 'annotation/import_documents.html', {'form': form, 'project': project})


@login_required
def add_label(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.project = project
            label.save()
            return redirect('project_detail', pk=pk)
    else:
        form = LabelForm()
    return render(request, 'annotation/add_label.html', {'form': form, 'project': project})

@login_required
def edit_label(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    
    if request.method == 'POST':
        label.text = request.POST.get('label')
        label.color = request.POST.get('color')
        label.save()
        return redirect('project_detail', pk=label.project.id)
    
    return render(request, 'annotation/edit_label.html', {
        'label': label
    })
    

@login_required
def delete_label(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    if request.method == 'POST':
        label.delete()
        return redirect('project_detail', label.project.id)
    return render(request, 'annotation/delete_label.html', {
        'label': label
    })


@login_required
def annotate(request, project_pk, doc_pk):
    project = get_object_or_404(Project, pk=project_pk)
    document = get_object_or_404(Document, pk=doc_pk, project=project)
    labels = Label.objects.filter(project=project)
    annotations = Annotation.objects.filter(document=document)

    if request.method == "POST":
        label_id = request.POST.get("label_id")
        content = request.POST.get("content", "")
        suggestions = request.POST.getlist("suggestions[]")
        start_offset = int(request.POST.get('start'))
        end_offset = int(request.POST.get('end'))
        document.text = content
        document.save()
        
        if label_id:
            label = get_object_or_404(Label, pk=label_id)
            annotation = Annotation.objects.create(
                document=document,
                label=label,
                user=request.user,
                start_offset=start_offset,
                end_offset=end_offset
            )
            for suggestion_text in suggestions:
                Suggestions.objects.create(annotation=annotation, text=suggestion_text)
            annotation.suggestions_text = suggestions
            annotation.save()

        return JsonResponse({"status": "ok"})

    return render(request, "annotation/annotate.html", {
        "project": project,
        "document": document,
        "labels": labels,
        "annotations": annotations
    })


    
@login_required
def export_annotations_csv(request, pk):
    project = get_object_or_404(Project, pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="annotations_{project.name}.csv"'
    writer = csv.writer(response)
    writer.writerow(['document_id', 'document_text', 'label', 'start_offset', 'end_offset', 'selected_text', 'suggestions'])
    for ann in Annotation.objects.filter(document__project=project).select_related('document', 'label'):
        selected_text = ann.document.text[ann.start_offset:ann.end_offset]
        writer.writerow([ann.document.id, ann.document.text, ann.label.text, ann.start_offset, ann.end_offset, selected_text, ann.suggestions_text])
    return response


    
@login_required
def export_annotations_json(request, pk):
    project = get_object_or_404(Project, pk=pk)
    data = []
    for ann in Annotation.objects.filter(document__project=project).select_related('document', 'label'):
        data.append({
            'document_id': ann.document.id,
            'document_text': ann.document.text,
            'label': ann.label.text,
            'start_offset': ann.start_offset,
            'end_offset': ann.end_offset,
            'selected_text': ann.document.text[ann.start_offset:ann.end_offset]
        })
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="annotations_{project.name}.json"'
    return response


@login_required
def annotation_list(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    annotations = Annotation.objects.filter(document__project=project).select_related('document', 'label', 'user')
    selected_texts = []
    for ann in annotations:
        start = ann.start_offset
        end = ann.end_offset
        if start > end:
            tmp = start
            start = end
            end = tmp
        selected_text = ann.document.text[start:end]
        selected_texts.append(selected_text)
    annotationsAndSelectedTexts = zip(annotations, selected_texts)
    return render(request, 'annotation/annotation_list.html', {
        'project': project,
        'annotationsAndSelectedTexts': annotationsAndSelectedTexts
    })
    

@login_required
def annotation_edit(request, annotation_id):
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    if request.method == "POST":
        label_id = request.POST.get("label_id")
        annotation.label = get_object_or_404(Label, pk=label_id)
        annotation.document = request.POST.get("document")
        annotation.start_offset = int(request.POST.get("start_offset"))
        annotation.end_offset = int(request.POST.get("end_offset"))
        annotation.suggestions_text = request.POST.get("suggestions_text", "")
        annotation.save()
        return redirect('annotation_list', project_pk=annotation.document.project.id)
    labels = Label.objects.filter(project=annotation.document.project)
    return render(request, 'annotation/annotation_edit.html', {
        'annotation': annotation,
        'labels': labels
    })

@login_required
def annotation_delete(request, annotation_id):
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    project_pk = annotation.document.project.id
    if request.method == "POST":
        annotation.delete()
        return redirect('annotation_list', project_pk=project_pk)
    return render(request, 'annotation/annotation_delete_confirm.html', {'annotation': annotation})

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    if request.method == 'POST':
        document.delete()
        return redirect('project_detail', pk=document.project.id)
    return render(request, 'annotation/delete_document.html', {
        'project': document.project
    })