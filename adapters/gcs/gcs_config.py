"""
Google Cloud Storage設定

GCSの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class GCSConfig:
    """Google Cloud Storage設定"""
    project_id: str = ""
    bucket_name: str = ""
    credentials_path: Optional[str] = None
    region: str = "asia-northeast1"
    storage_class: str = "STANDARD"
    lifecycle_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if not self.project_id:
            import os
            self.project_id = os.getenv("GCS_PROJECT_ID", "")
        
        if not self.bucket_name:
            import os
            self.bucket_name = os.getenv("GCS_BUCKET_NAME", "")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'project_id': self.project_id,
            'bucket_name': self.bucket_name,
            'credentials_path': self.credentials_path,
            'region': self.region,
            'storage_class': self.storage_class,
            'lifecycle_rules': self.lifecycle_rules
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GCSConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # プロジェクトIDの検証
        if not self.project_id:
            return False
        
        # バケット名の検証
        if not self.bucket_name:
            return False
        
        # リージョンの検証
        valid_regions = [
            "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "us-central1", "us-east1", "us-west1", "us-west2",
            "europe-west1", "europe-west2", "europe-west3"
        ]
        if self.region not in valid_regions:
            return False
        
        # ストレージクラスの検証
        valid_storage_classes = [
            "STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"
        ]
        if self.storage_class not in valid_storage_classes:
            return False
        
        return True
