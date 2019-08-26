from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from time_tracker.models import Project, Task, Log, Developer, Comment
from django.views.generic import View, TemplateView, ListView, CreateView, DetailView, UpdateView
from time_tracker.forms import CreateTaskForm, EditTaskForm, AddTimeToTaskForm, AddCommentToTaskForm, ProjectForm


@receiver(pre_save, sender=Task)
def task_send_message(instance, sender, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        html = get_template('email/email.html')
        d = {'old': old, 'new': instance}

        subject, from_email, to = 'Changed task', settings.EMAIL_HOST_USER, [old.creator.email,
                                                                             instance.implementer.user.email]
        html_content = html.render(d)
        msg = EmailMultiAlternatives(subject, "text_content", from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class HomeView(TemplateView):
    template_name = 'index.html'


class TimeLogListView(ListView):
    model = Log
    template_name = 'list/log_index.html'
    context_object_name = 'logs'


class TrackerHomeView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            projects = Project.objects.all()
        else:
            dev = Developer.objects.get(user__username=request.user.username)
            projects_id = Task.objects.filter(implementer=dev).all()
            projects = Project.objects.filter(pk__in=[x.project.pk for x in projects_id])

        return render(request, 'tracker/tracker_home.html', {'projects': projects})


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'tracker/project/project_info.html'
    context_object_name = 'project'
    calc_time = time = 0

    def set_time(self, tasks):
        for task in tasks:
            self.calc_time += task.hours
            for l in Log.objects.filter(task_id=task.id):
                self.time += float(l.hours)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.filter(project__slug=self.object.slug)
        self.set_time(tasks)
        context['tasks'] = tasks
        context['hours'] = self.time
        context['caclTime'] = self.calc_time
        return context


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tracker/task/task_info.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Task, id=self.kwargs.get('task_id'))

    def post(self, request, *args, **kwargs):
        f_time = AddTimeToTaskForm(request.POST, prefix='time')
        f_comment = AddCommentToTaskForm(request.POST, prefix='comment')

        if f_time.is_valid():
            f_time.save()
            return redirect('task-info', slug=self.kwargs.get('slug'), task_id=self.kwargs.get('task_id'))

        if f_comment.is_valid():
            f_comment.save()
            return redirect('task-info', slug=self.kwargs.get('slug'), task_id=self.kwargs.get('task_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spent_time = 0
        project = Project.objects.get(slug=self.kwargs.get('slug'))
        comments = Comment.objects.filter(task_id=self.kwargs.get('task_id')).order_by('-createdAt')
        time = Log.objects.filter(task_id=self.kwargs.get('task_id'))
        for t in time:
            spent_time += t.hours

        context['f_time'] = AddTimeToTaskForm(
            initial={'task': self.get_object(), 'user': User.objects.get(username=self.request.user)},
            prefix='time')
        context['f_comment'] = AddCommentToTaskForm(
            initial={'task': self.get_object(), 'author': User.objects.get(username=self.request.user)},
            prefix='comment')
        context['project'] = project
        context['comments'] = comments
        context['time_list'] = time
        context['spent_time'] = spent_time

        return context


class TaskUpdateView(UpdateView):
    model = Task
    template_name = 'tracker/task/edit_task_info.html'
    form_class = EditTaskForm

    def get_object(self, queryset=None):
        return get_object_or_404(Task, id=self.kwargs.get('task_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(slug=self.kwargs.get('slug'))
        return context


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tracker/project/create_project.html'
    success_url = reverse_lazy('tracker-home')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tracker/project/edit_project.html'
    success_url = reverse_lazy('tracker-home')

    def get_object(self, queryset=None):
        return get_object_or_404(Project, slug=self.kwargs.get('slug'))

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)


class TaskCreateView(CreateView):
    model = Task
    form_class = CreateTaskForm
    template_name = 'tracker/task/create_task.html'
    success_url = reverse_lazy('tracker-home')

    def get_initial(self):
        project = Project.objects.get(slug=self.kwargs.get('slug'))
        return {'project': project, 'creator': self.request.user}

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(TaskCreateView, self).dispatch(*args, **kwargs)
