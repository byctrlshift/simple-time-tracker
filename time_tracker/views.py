from pprint import pprint
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import pre_save
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
from time_tracker.models import Project, Task, Log, Developer, Comment
from time_tracker.forms import CreateTaskForm, EditTaskForm, AddTimeToTaskForm, AddCommentToTaskForm, ProjectForm


@receiver(pre_save, sender=Task)
def task_send_message(instance, sender, **kwargs):
    html = get_template('email.html')
    d = {'old': Task.objects.get(pk=instance.pk), 'new': instance}

    subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
    html_content = html.render(d)
    msg = EmailMultiAlternatives(subject, "text_content", from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def home(request):
    return render(request, 'index.html')


def tracker_home(request):
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        dev = Developer.objects.get(user__username=request.user.username)
        projects_id = Task.objects.filter(implementer=dev).all()
        projects = Project.objects.filter(pk__in=[x.project.pk for x in projects_id])

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
    spent_time = 0
    for t in time:
        spent_time += t.hours

    if request.POST:
        f_time = AddTimeToTaskForm(request.POST, prefix='time')
        f_comment = AddCommentToTaskForm(request.POST, prefix='comment')
        if f_time.is_valid():
            f_time.save()
        if f_comment.is_valid():
            f_comment.save()

        return redirect('task-info', slug=slug, task_id=task_id)
    else:
        f_time = AddTimeToTaskForm(initial={'task': task}, prefix='time')
        f_comment = AddCommentToTaskForm(
            initial={'task': task, 'author': User.objects.get(username=request.user)}, prefix='comment')

    args = {'project': project, 'task': task, 'f_time': f_time, 'spent_time': spent_time,
            'f_comment': f_comment, 'time_list': time, 'comments': comments}

    return render(request, 'tracker/task_info.html', args)


def edit_task(request, slug, task_id):
    project = Project.objects.get(slug=slug)
    task = Task.objects.get(id=task_id)

    if request.POST:
        form = EditTaskForm(request.POST, instance=task)
        if form.is_valid():
            new = form.save()
            # task_send_message(task, new)
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
        form = CreateTaskForm(initial={'project': project, 'creator': request.user})

    return render(request, 'tracker/create_task.html', {'form': form, 'project': project})
