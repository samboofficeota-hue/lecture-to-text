"""
ログ管理設定

Cloud Loggingの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class LoggingConfig:
    """ログ管理設定"""
    project_id: str = ""
    log_name: str = "darwin-app"
    log_level: str = "INFO"
    service_name: str = "darwin"
    version: str = "1.0.0"
    region: str = "asia-northeast1"
    labels: Optional[Dict[str, str]] = None
    resource_type: str = "cloud_run_revision"
    
    def __post_init__(self):
        """初期化後の処理"""
        import os
        
        if not self.project_id:
            self.project_id = os.getenv("GCP_PROJECT_ID", "")
        
        if not self.log_name:
            self.log_name = os.getenv("LOG_NAME", "darwin-app")
        
        if not self.labels:
            self.labels = {
                "service": self.service_name,
                "version": self.version,
                "region": self.region
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'project_id': self.project_id,
            'log_name': self.log_name,
            'log_level': self.log_level,
            'service_name': self.service_name,
            'version': self.version,
            'region': self.region,
            'labels': self.labels,
            'resource_type': self.resource_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggingConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # プロジェクトIDの検証
        if not self.project_id:
            return False
        
        # ログレベルの検証
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            return False
        
        # リソースタイプの検証
        valid_resource_types = [
            "cloud_run_revision", "cloud_function", "gce_instance",
            "k8s_container", "global"
        ]
        if self.resource_type not in valid_resource_types:
            return False
        
        return True
