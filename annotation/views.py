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

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('project_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def Logout(request):
    # user = User.objects.get(username=request.user.username)
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
    labels = Label.objects.filter(project=project)
    return render(request, 'annotation/project_detail.html', {
        'project': project, 'documents': documents, 'labels': labels
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
def annotate(request, project_pk, doc_pk):
    project = get_object_or_404(Project, pk=project_pk)
    document = get_object_or_404(Document, pk=doc_pk, project=project)
    labels = Label.objects.filter(project=project)
    annotations = Annotation.objects.filter(document=document)
    if request.method == "POST":
        label_id = request.POST.get("label_id")
        start = int(request.POST.get("start"))
        end = int(request.POST.get("end"))
        suggestions = request.POST.getlist("suggestions[]")
        label = get_object_or_404(Label, pk=label_id)

        annotation = Annotation.objects.create(
            document=document,
            label=label,
            start_offset=start,
            end_offset=end,
            user=request.user
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
    return render(request, 'annotation/annotation_list.html', {
        'project': project,
        'annotations': annotations
    })
    

@login_required
def annotation_edit(request, annotation_id):
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    if request.method == "POST":
        label_id = request.POST.get("label_id")
        annotation.label = get_object_or_404(Label, pk=label_id)
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