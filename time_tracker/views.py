from pprint import pprint
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from time_tracker.models import Project, Task, Log, Developer, Comment
from time_tracker.forms import CreateTaskForm, EditTaskForm, AddTimeToTaskForm, AddCommentToTaskForm, ProjectForm


def home(request):
    return render(request, 'index.html')


def tracker_home(request):
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        user = Developer.objects.get(user__username=request.user)
        projects_id = Task.objects.filter(implementer=user).values_list('id', flat=True)
        projects = Project.objects.filter(id__in=projects_id)

    return render(request, 'tracker/tracker_home.html', {'projects': projects})


def project_info(request, slug):
    project = Project.objects.get(slug=slug)
    tasks = Task.objects.filter(project=project)
    calc_time = time = 0

    for task in tasks:
        calc_time += task.hours
        for l in Log.objects.filter(task_id=task.id):
            time += float(l.hours)

    args = {'project': project, 'tasks': tasks, 'hours': time, 'caclTime': calc_time}
    return render(request, 'tracker/project_info.html', args)


def task_info(request, slug, task_id):
    project = Project.objects.get(slug=slug)
    task = Task.objects.get(id=task_id)
    time = Log.objects.filter(task_id=task_id)
    comments = Comment.objects.filter(task_id=task_id).order_by('-createdAt')

    if request.POST:
        f_time = AddTimeToTaskForm(request.POST or None)
        f_comment = AddCommentToTaskForm(request.POST or None)
        if f_time.is_valid():
            f_time.save()
        elif f_comment.is_valid():
            f_comment.save()

        return redirect('task-info', slug=slug, task_id=task_id)
    else:
        f_time = AddTimeToTaskForm(initial={'task': task}, prefix='time')
        f_comment = AddCommentToTaskForm(initial={'task': task}, prefix='comment')

    args = {'project': project, 'task': task, 'f_time': f_time,
            'f_comment': f_comment, 'time_list': time, 'comments': comments}

    return render(request, 'tracker/task_info.html', args)


def edit_task(request, slug, task_id):
    project = Project.objects.get(slug=slug)
    task = Task.objects.get(id=task_id)

    if request.POST:
        form = EditTaskForm(request.POST, instance=task)
        if form.is_valid():
            pprint(form.cleaned_data)
            form.save()
            return redirect('task-info', slug=slug, task_id=task_id)
    else:
        form = EditTaskForm(instance=task)

    args = {'form': form, 'project': project, 'task': task}
    return render(request, 'tracker/edit_task_info.html', args)


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def create_project(request):
    if request.POST:
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker-home')
    else:
        form = ProjectForm()

    return render(request, 'tracker/create_project.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def edit_project(request, slug):
    project = Project.objects.get(slug=slug)
    if request.POST:
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project-info', slug=slug)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'tracker/edit_project.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='/')
def create_task(request, slug):
    project = Project.objects.get(slug=slug)
    if request.POST:
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker-home')
    else:
        form = CreateTaskForm(initial={'project': project})

    return render(request, 'tracker/create_task.html', {'form': form, 'project': project})
