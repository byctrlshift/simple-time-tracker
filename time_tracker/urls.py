from .views import *
from django.urls import path

urlpatterns = [
    path('', HomeView.as_view(), name='homepage'),
    path('tracker/', TrackerHomeView.as_view(), name='tracker-home'),
    path('tracker/time-log', TimeLogListView.as_view(), name='time-log-list'),
    path('tracker/project/create', ProjectCreateView.as_view(), name='project-create'),
    path('tracker/project/<slug:slug>', ProjectDetailView.as_view(), name='project-info'),
    path('tracker/project/<slug:slug>/edit', ProjectUpdateView.as_view(), name='project-edit'),
    path('tracker/project/<slug:slug>/task/create', TaskCreateView.as_view(), name='task-create'),
    path('tracker/project/<slug:slug>/task/<int:task_id>', TaskDetailView.as_view(), name='task-info'),
    path('tracker/project/<slug:slug>/task/<int:task_id>/edit', TaskUpdateView.as_view(), name='task-edit'),
]
