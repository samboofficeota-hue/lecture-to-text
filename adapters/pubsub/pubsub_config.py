"""
Pub/Sub設定

Cloud Pub/Subの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class PubSubConfig:
    """Pub/Sub設定"""
    project_id: str = ""
    topic_name: str = "darwin-topic"
    subscription_name: str = "darwin-subscription"
    region: str = "asia-northeast1"
    message_retention_duration: int = 7  # 日数
    ack_deadline_seconds: int = 600
    max_delivery_attempts: int = 5
    enable_message_ordering: bool = False
    
    def __post_init__(self):
        """初期化後の処理"""
        import os
        
        if not self.project_id:
            self.project_id = os.getenv("GCP_PROJECT_ID", "")
        
        if not self.topic_name:
            self.topic_name = os.getenv("PUBSUB_TOPIC_NAME", "darwin-topic")
        
        if not self.subscription_name:
            self.subscription_name = os.getenv("PUBSUB_SUBSCRIPTION_NAME", "darwin-subscription")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'project_id': self.project_id,
            'topic_name': self.topic_name,
            'subscription_name': self.subscription_name,
            'region': self.region,
            'message_retention_duration': self.message_retention_duration,
            'ack_deadline_seconds': self.ack_deadline_seconds,
            'max_delivery_attempts': self.max_delivery_attempts,
            'enable_message_ordering': self.enable_message_ordering
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PubSubConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def get_topic_path(self) -> str:
        """トピックパスを取得"""
        return f"projects/{self.project_id}/topics/{self.topic_name}"
    
    def get_subscription_path(self) -> str:
        """サブスクリプションパスを取得"""
        return f"projects/{self.project_id}/subscriptions/{self.subscription_name}"
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # プロジェクトIDの検証
        if not self.project_id:
            return False
        
        # トピック名の検証
        if not self.topic_name:
            return False
        
        # サブスクリプション名の検証
        if not self.subscription_name:
            return False
        
        # メッセージ保持期間の検証
        if self.message_retention_duration < 1 or self.message_retention_duration > 31:
            return False
        
        # ACKデッドラインの検証
        if self.ack_deadline_seconds < 10 or self.ack_deadline_seconds > 600:
            return False
        
        # 最大配信試行回数の検証
        if self.max_delivery_attempts < 1 or self.max_delivery_attempts > 10:
            return False
        
        return True
