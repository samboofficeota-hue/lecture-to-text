"""
タスク管理アダプター

Cloud Tasksとの連携を行います。
"""

from .cloud_tasks_adapter import CloudTasksAdapter
from .tasks_config import TasksConfig

__all__ = [
    'CloudTasksAdapter',
    'TasksConfig'
]
