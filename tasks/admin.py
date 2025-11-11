from django.contrib import admin
from tasks.models import Task,TaskExecution

# Register your models here.

admin.site.register(Task)
admin.site.register(TaskExecution)
