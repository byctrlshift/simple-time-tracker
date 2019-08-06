from .views import *
from django.urls import path

urlpatterns = [
    path('', home, name='homepage'),
    path('tracker/', tracker_home, name='tracker-home'),
    path('tracker/time-log', time_log_list, name='time-log-list'),
    path('tracker/project/create', create_project, name='project-create'),
    path('tracker/project/<slug:slug>', project_info, name='project-info'),
    path('tracker/project/<slug:slug>/edit', edit_project, name='project-edit'),
    path('tracker/project/<slug:slug>/task/create', create_task, name='task-create'),
    path('tracker/project/<slug:slug>/task/<int:task_id>', task_info, name='task-info'),
    path('tracker/project/<slug:slug>/task/<int:task_id>/edit', edit_task, name='task-edit'),
]
