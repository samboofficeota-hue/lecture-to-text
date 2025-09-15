"""
マスターテキストデータモデル

講義録のマスターテキストとバージョン管理を管理するデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path


class MasterTextStatus(Enum):
    """マスターテキストステータス"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class MasterTextVersion:
    """マスターテキストバージョン"""
    version: str
    content: str
    created_at: datetime
    created_by: str
    change_summary: str
    quality_score: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def word_count(self) -> int:
        """単語数を取得"""
        return len(self.content.split())
    
    @property
    def character_count(self) -> int:
        """文字数を取得"""
        return len(self.content)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'version': self.version,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'change_summary': self.change_summary,
            'quality_score': self.quality_score,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MasterTextVersion':
        """辞書からインスタンスを作成"""
        return cls(
            version=data['version'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            created_by=data['created_by'],
            change_summary=data['change_summary'],
            quality_score=data.get('quality_score'),
            metadata=data.get('metadata', {})
        )


@dataclass
class MasterText:
    """マスターテキスト"""
    id: str
    lecture_id: str
    title: str
    current_version: str
    versions: List[MasterTextVersion]
    status: MasterTextStatus = MasterTextStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def current_content(self) -> str:
        """現在の内容を取得"""
        for version in self.versions:
            if version.version == self.current_version:
                return version.content
        return ""
    
    @property
    def version_count(self) -> int:
        """バージョン数を取得"""
        return len(self.versions)
    
    @property
    def latest_version(self) -> Optional[MasterTextVersion]:
        """最新バージョンを取得"""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.created_at)
    
    def add_version(
        self, 
        content: str, 
        created_by: str, 
        change_summary: str,
        quality_score: Optional[float] = None
    ) -> str:
        """新しいバージョンを追加"""
        # バージョン番号を生成（簡易版）
        version_number = len(self.versions) + 1
        version = f"v{version_number}"
        
        new_version = MasterTextVersion(
            version=version,
            content=content,
            created_at=datetime.now(),
            created_by=created_by,
            change_summary=change_summary,
            quality_score=quality_score
        )
        
        self.versions.append(new_version)
        self.current_version = version
        self.updated_at = datetime.now()
        
        return version
    
    def get_version(self, version: str) -> Optional[MasterTextVersion]:
        """指定バージョンを取得"""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_version_history(self) -> List[MasterTextVersion]:
        """バージョン履歴を取得（作成日時順）"""
        return sorted(self.versions, key=lambda v: v.created_at)
    
    def update_status(self, status: MasterTextStatus) -> None:
        """ステータスを更新"""
        self.status = status
        self.updated_at = datetime.now()
    
    def get_quality_trend(self) -> List[float]:
        """品質スコアの推移を取得"""
        return [v.quality_score for v in self.versions if v.quality_score is not None]
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'lecture_id': self.lecture_id,
            'title': self.title,
            'current_version': self.current_version,
            'versions': [v.to_dict() for v in self.versions],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MasterText':
        """辞書からインスタンスを作成"""
        return cls(
            id=data['id'],
            lecture_id=data['lecture_id'],
            title=data['title'],
            current_version=data['current_version'],
            versions=[MasterTextVersion.from_dict(v) for v in data['versions']],
            status=MasterTextStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {})
        )
