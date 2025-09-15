"""
タスク管理設定

Cloud Tasksの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class TasksConfig:
    """タスク管理設定"""
    project_id: str = ""
    location: str = "asia-northeast1"
    queue_name: str = "darwin-queue"
    service_account_email: Optional[str] = None
    base_url: str = ""
    timeout_seconds: int = 3600
    retry_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        import os
        
        if not self.project_id:
            self.project_id = os.getenv("GCP_PROJECT_ID", "")
        
        if not self.queue_name:
            self.queue_name = os.getenv("TASKS_QUEUE_NAME", "darwin-queue")
        
        if not self.base_url:
            self.base_url = os.getenv("TASKS_BASE_URL", "")
        
        if not self.service_account_email:
            self.service_account_email = os.getenv("TASKS_SERVICE_ACCOUNT_EMAIL")
        
        # デフォルトのリトライ設定
        if not self.retry_config:
            self.retry_config = {
                'max_attempts': 3,
                'max_retry_duration': '600s',
                'min_backoff': '5s',
                'max_backoff': '60s',
                'max_doublings': 3
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'project_id': self.project_id,
            'location': self.location,
            'queue_name': self.queue_name,
            'service_account_email': self.service_account_email,
            'base_url': self.base_url,
            'timeout_seconds': self.timeout_seconds,
            'retry_config': self.retry_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TasksConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def get_queue_path(self) -> str:
        """キューパスを取得"""
        return f"projects/{self.project_id}/locations/{self.location}/queues/{self.queue_name}"
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # プロジェクトIDの検証
        if not self.project_id:
            return False
        
        # キュー名の検証
        if not self.queue_name:
            return False
        
        # ベースURLの検証
        if not self.base_url:
            return False
        
        # タイムアウトの検証
        if self.timeout_seconds < 1 or self.timeout_seconds > 3600:
            return False
        
        return True
