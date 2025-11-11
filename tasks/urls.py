from django.urls import path
from tasks import views

urlpatterns = [
    path('all/tasks/', views.TaskListView.as_view(), name='task_list'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/executions/all/',views.TaskExecutionListView.as_view(),name='task_execution'),
    path('tasks/my-taks/',views.MyTasksListView.as_view(),name='my_taks'),
    path('tasks/my-tasks/mark-done/<int:pk>/', views.MarkTaskDoneView.as_view(), name='mark_task_done'),
]