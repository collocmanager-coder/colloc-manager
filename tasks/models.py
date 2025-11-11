from datetime import timedelta
from django.db import models
from users.models import RoomMember, Room


# Create your models here.

class Task(models.Model):
    taskName = models.CharField(max_length=255)
    taskDescription = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE,related_name='home_tasks')
    durationDays = models.IntegerField()
    rotation_order = models.JSONField(default=list, blank=True)
    def __str__(self):
        return self.taskName +" de la chambre "+self.room.roomNumber


class TaskExecution(models.Model):
    roomTask = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='executions')
    executor = models.ForeignKey(RoomMember, on_delete=models.CASCADE,related_name='tasks_executed')
    isDone = models.BooleanField(default=False)
    execution_time = models.DateTimeField(auto_now_add=True)
    turn_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        room_number = self.roomTask.room.roomNumber if self.roomTask.room else 'N/A'
        return f"{self.executor.username} - {self.roomTask.taskName} ({room_number})"
    
