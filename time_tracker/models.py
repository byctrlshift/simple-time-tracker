import os
from django.db import models
from django.contrib.auth.models import User
from tinymce import models as tinymce_models
from django.template.defaultfilters import slugify


def get_image_path(instance, filename):
    return os.path.join('user_avatars', str(instance.user.id), filename)


class Developer(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )
    birth_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=128, blank=True)
    avatar = models.FileField(upload_to=get_image_path, blank=True)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    name = models.CharField(max_length=128)
    description = tinymce_models.HTMLField()
    slug = models.SlugField(max_length=192)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_TYPE = (
        ('N', 'Normal'),
        ('H', 'High'),
        ('U', 'Urgent')
    )

    TASK_TYPE = (
        ('F', 'Feature'),
        ('B', 'Bug'),
    )
    subject = models.CharField(max_length=128)
    description = tinymce_models.HTMLField()
    date_start = models.DateField()
    date_stop = models.DateField()
    kind = models.CharField(max_length=1, choices=TASK_TYPE, default='F')
    priority = models.CharField(max_length=1, choices=PRIORITY_TYPE, default='N')
    hours = models.FloatField()
    implementer = models.ForeignKey(Developer, null=True, on_delete=models.SET_NULL, related_name='task_implementer')
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='task_creator')
    project = models.ForeignKey(Project, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.subject


class Comment(models.Model):
    comment = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    author = models.ForeignKey(Developer, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)


class Log(models.Model):
    hours = models.FloatField()
    comment = models.TextField()
    task = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)
