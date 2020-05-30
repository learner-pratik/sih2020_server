from rest_framework import serializers
from .models import Tasks, LANGUAGE_CHOICES, STYLE_CHOICES

class Task_serializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ['task_id', 'task_info', 'deadline', 'task_from', 'task_to', 'status']