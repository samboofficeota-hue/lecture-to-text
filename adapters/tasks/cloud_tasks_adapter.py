"""
Cloud Tasksアダプター

Cloud Tasksとの連携を実装します。
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from ...utils.logging import get_logger

logger = get_logger(__name__)


class TaskPriority(Enum):
    """タスク優先度"""
    LOW = 0
    NORMAL = 1
    HIGH = 2


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CloudTasksAdapter:
    """Cloud Tasksアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Cloud Tasksアダプターを初期化
        
        Args:
            config: タスク管理設定
        """
        self.config = config or {}
        self.client = None
        self.queue_path = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Cloud Tasksクライアントを初期化"""
        try:
            # クライアントを作成
            self.client = tasks_v2.CloudTasksClient()
            
            # キューパスを設定
            project_id = self.config.get('project_id')
            location = self.config.get('location', 'asia-northeast1')
            queue_name = self.config.get('queue_name', 'darwin-queue')
            
            self.queue_path = self.client.queue_path(project_id, location, queue_name)
            
            logger.info(f"Cloud Tasks client initialized: {self.queue_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Tasks client: {e}")
            raise
    
    def create_task(
        self, 
        task_name: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        タスクを作成
        
        Args:
            task_name: タスク名
            endpoint: エンドポイント
            payload: ペイロード
            headers: ヘッダー
            
        Returns:
            Optional[str]: タスク名
        """
        try:
            if not self.client or not self.queue_path:
                raise ValueError("Cloud Tasks client not initialized")
            
            # ベースURLを取得
            base_url = self.config.get('base_url', '')
            if not base_url:
                raise ValueError("Base URL not configured")
            
            # 完全なURLを構築
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # リクエストボディを作成
            if payload:
                body = json.dumps(payload).encode('utf-8')
            else:
                body = b''
            
            # タスクを作成
            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': url,
                    'headers': {
                        'Content-Type': 'application/json',
                        **(headers or {})
                    },
                    'body': body
                }
            }
            
            # スケジュール時間を設定
            if delay_seconds > 0:
                schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(schedule_time)
                task['schedule_time'] = timestamp
            
            # タスクを作成
            response = self.client.create_task(
                parent=self.queue_path,
                task=task
            )
            
            task_name = response.name
            logger.info(f"Task created: {task_name}")
            return task_name
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    def create_lecture_processing_task(
        self, 
        lecture_id: str,
        audio_file_path: str,
        pdf_file_path: Optional[str] = None,
        domain: str = "general",
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> Optional[str]:
        """
        講義処理タスクを作成
        
        Args:
            lecture_id: 講義ID
            audio_file_path: 音声ファイルパス
            pdf_file_path: PDFファイルパス
            domain: 分野
            priority: 優先度
            
        Returns:
            Optional[str]: タスク名
        """
        payload = {
            'lecture_id': lecture_id,
            'audio_file_path': audio_file_path,
            'pdf_file_path': pdf_file_path,
            'domain': domain,
            'created_at': datetime.utcnow().isoformat()
        }
        
        headers = {
            'X-Task-Type': 'lecture-processing',
            'X-Lecture-ID': lecture_id
        }
        
        return self.create_task(
            task_name=f"lecture-processing-{lecture_id}",
            endpoint="/api/v1/process-lecture",
            payload=payload,
            priority=priority,
            headers=headers
        )
    
    def create_rag_processing_task(
        self, 
        lecture_id: str,
        text_content: str,
        domain: str = "general",
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> Optional[str]:
        """
        RAG処理タスクを作成
        
        Args:
            lecture_id: 講義ID
            text_content: テキスト内容
            domain: 分野
            priority: 優先度
            
        Returns:
            Optional[str]: タスク名
        """
        payload = {
            'lecture_id': lecture_id,
            'text_content': text_content,
            'domain': domain,
            'created_at': datetime.utcnow().isoformat()
        }
        
        headers = {
            'X-Task-Type': 'rag-processing',
            'X-Lecture-ID': lecture_id
        }
        
        return self.create_task(
            task_name=f"rag-processing-{lecture_id}",
            endpoint="/api/v1/process-rag",
            payload=payload,
            priority=priority,
            headers=headers
        )
    
    def create_notification_task(
        self, 
        user_id: str,
        message: str,
        notification_type: str = "info",
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> Optional[str]:
        """
        通知タスクを作成
        
        Args:
            user_id: ユーザーID
            message: メッセージ
            notification_type: 通知タイプ
            priority: 優先度
            
        Returns:
            Optional[str]: タスク名
        """
        payload = {
            'user_id': user_id,
            'message': message,
            'notification_type': notification_type,
            'created_at': datetime.utcnow().isoformat()
        }
        
        headers = {
            'X-Task-Type': 'notification',
            'X-User-ID': user_id
        }
        
        return self.create_task(
            task_name=f"notification-{user_id}-{int(datetime.utcnow().timestamp())}",
            endpoint="/api/v1/send-notification",
            payload=payload,
            priority=priority,
            headers=headers
        )
    
    def get_task(
        self, 
        task_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        タスクを取得
        
        Args:
            task_name: タスク名
            
        Returns:
            Optional[Dict[str, Any]]: タスク情報
        """
        try:
            if not self.client:
                return None
            
            task = self.client.get_task(name=task_name)
            
            return {
                'name': task.name,
                'schedule_time': task.schedule_time.ToDatetime().isoformat() if task.schedule_time else None,
                'create_time': task.create_time.ToDatetime().isoformat() if task.create_time else None,
                'dispatch_deadline': task.dispatch_deadline.total_seconds() if task.dispatch_deadline else None,
                'dispatch_count': task.dispatch_count,
                'response_count': task.response_count,
                'first_attempt': {
                    'schedule_time': task.first_attempt.schedule_time.ToDatetime().isoformat() if task.first_attempt.schedule_time else None,
                    'dispatch_time': task.first_attempt.dispatch_time.ToDatetime().isoformat() if task.first_attempt.dispatch_time else None,
                    'response_time': task.first_attempt.response_time.ToDatetime().isoformat() if task.first_attempt.response_time else None,
                    'response_status': task.first_attempt.response_status.code if task.first_attempt.response_status else None
                } if task.first_attempt else None,
                'last_attempt': {
                    'schedule_time': task.last_attempt.schedule_time.ToDatetime().isoformat() if task.last_attempt.schedule_time else None,
                    'dispatch_time': task.last_attempt.dispatch_time.ToDatetime().isoformat() if task.last_attempt.dispatch_time else None,
                    'response_time': task.last_attempt.response_time.ToDatetime().isoformat() if task.last_attempt.response_time else None,
                    'response_status': task.last_attempt.response_status.code if task.last_attempt.response_status else None
                } if task.last_attempt else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None
    
    def list_tasks(
        self, 
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        タスク一覧を取得
        
        Args:
            max_results: 最大取得数
            
        Returns:
            List[Dict[str, Any]]: タスク一覧
        """
        try:
            if not self.client or not self.queue_path:
                return []
            
            tasks = self.client.list_tasks(parent=self.queue_path)
            
            task_list = []
            count = 0
            for task in tasks:
                if count >= max_results:
                    break
                
                task_info = {
                    'name': task.name,
                    'schedule_time': task.schedule_time.ToDatetime().isoformat() if task.schedule_time else None,
                    'create_time': task.create_time.ToDatetime().isoformat() if task.create_time else None,
                    'dispatch_count': task.dispatch_count,
                    'response_count': task.response_count
                }
                
                task_list.append(task_info)
                count += 1
            
            return task_list
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []
    
    def delete_task(
        self, 
        task_name: str
    ) -> bool:
        """
        タスクを削除
        
        Args:
            task_name: タスク名
            
        Returns:
            bool: 削除の成功/失敗
        """
        try:
            if not self.client:
                return False
            
            self.client.delete_task(name=task_name)
            logger.info(f"Task deleted: {task_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False
    
    def pause_queue(self) -> bool:
        """
        キューを一時停止
        
        Returns:
            bool: 一時停止の成功/失敗
        """
        try:
            if not self.client or not self.queue_path:
                return False
            
            queue = self.client.pause_queue(name=self.queue_path)
            logger.info(f"Queue paused: {self.queue_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause queue: {e}")
            return False
    
    def resume_queue(self) -> bool:
        """
        キューを再開
        
        Returns:
            bool: 再開の成功/失敗
        """
        try:
            if not self.client or not self.queue_path:
                return False
            
            queue = self.client.resume_queue(name=self.queue_path)
            logger.info(f"Queue resumed: {self.queue_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume queue: {e}")
            return False
    
    def get_queue_info(self) -> Optional[Dict[str, Any]]:
        """
        キュー情報を取得
        
        Returns:
            Optional[Dict[str, Any]]: キュー情報
        """
        try:
            if not self.client or not self.queue_path:
                return None
            
            queue = self.client.get_queue(name=self.queue_path)
            
            return {
                'name': queue.name,
                'state': queue.state.name,
                'purge_time': queue.purge_time.ToDatetime().isoformat() if queue.purge_time else None,
                'rate_limits': {
                    'max_dispatches_per_second': queue.rate_limits.max_dispatches_per_second,
                    'max_burst_size': queue.rate_limits.max_burst_size,
                    'max_concurrent_dispatches': queue.rate_limits.max_concurrent_dispatches
                },
                'retry_config': {
                    'max_attempts': queue.retry_config.max_attempts,
                    'max_retry_duration': queue.retry_config.max_retry_duration.total_seconds() if queue.retry_config.max_retry_duration else None,
                    'min_backoff': queue.retry_config.min_backoff.total_seconds() if queue.retry_config.min_backoff else None,
                    'max_backoff': queue.retry_config.max_backoff.total_seconds() if queue.retry_config.max_backoff else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue info: {e}")
            return None
