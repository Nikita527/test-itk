from django.db import models


class TaskQueue(models.Model):
    """Модель для хранения задач в очереди."""

    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Возвращает имя задачи."""
        return self.task_name
