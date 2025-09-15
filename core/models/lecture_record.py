"""
講義記録データモデル

講義の記録とメタデータを管理するデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path


class LectureStatus(Enum):
    """講義ステータス"""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class LectureMetadata:
    """講義メタデータ"""
    title: str
    instructor: str
    date: datetime
    duration: float
    domain: str
    description: Optional[str] = None
    tags: List[str] = None
    language: str = "ja"
    quality_score: Optional[float] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.tags is None:
            self.tags = []
    
    def add_tag(self, tag: str) -> None:
        """タグを追加"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """タグを削除"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'title': self.title,
            'instructor': self.instructor,
            'date': self.date.isoformat(),
            'duration': self.duration,
            'domain': self.domain,
            'description': self.description,
            'tags': self.tags,
            'language': self.language,
            'quality_score': self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LectureMetadata':
        """辞書からインスタンスを作成"""
        return cls(
            title=data['title'],
            instructor=data['instructor'],
            date=datetime.fromisoformat(data['date']),
            duration=data['duration'],
            domain=data['domain'],
            description=data.get('description'),
            tags=data.get('tags', []),
            language=data.get('language', 'ja'),
            quality_score=data.get('quality_score')
        )


@dataclass
class LectureRecord:
    """講義記録"""
    id: str
    metadata: LectureMetadata
    audio_file_path: str
    pdf_file_path: Optional[str] = None
    raw_transcript_path: Optional[str] = None
    processed_transcript_path: Optional[str] = None
    final_transcript_path: Optional[str] = None
    status: LectureStatus = LectureStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    processing_log: List[Dict[str, Any]] = None
    custom_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.processing_log is None:
            self.processing_log = []
        if self.custom_metadata is None:
            self.custom_metadata = {}
    
    @property
    def audio_file_exists(self) -> bool:
        """音声ファイルの存在確認"""
        return Path(self.audio_file_path).exists()
    
    @property
    def pdf_file_exists(self) -> bool:
        """PDFファイルの存在確認"""
        return self.pdf_file_path and Path(self.pdf_file_path).exists()
    
    @property
    def is_processing_complete(self) -> bool:
        """処理完了の確認"""
        return self.status in [LectureStatus.COMPLETED, LectureStatus.PUBLISHED]
    
    def add_processing_log(self, step: str, status: str, details: Dict[str, Any] = None) -> None:
        """処理ログを追加"""
        log_entry = {
            'step': step,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.processing_log.append(log_entry)
        self.updated_at = datetime.now()
    
    def update_status(self, status: LectureStatus) -> None:
        """ステータスを更新"""
        self.status = status
        self.updated_at = datetime.now()
    
    def get_file_paths(self) -> Dict[str, str]:
        """ファイルパスの辞書を取得"""
        return {
            'audio': self.audio_file_path,
            'pdf': self.pdf_file_path,
            'raw_transcript': self.raw_transcript_path,
            'processed_transcript': self.processed_transcript_path,
            'final_transcript': self.final_transcript_path
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'metadata': self.metadata.to_dict(),
            'audio_file_path': self.audio_file_path,
            'pdf_file_path': self.pdf_file_path,
            'raw_transcript_path': self.raw_transcript_path,
            'processed_transcript_path': self.processed_transcript_path,
            'final_transcript_path': self.final_transcript_path,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'processing_log': self.processing_log,
            'custom_metadata': self.custom_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LectureRecord':
        """辞書からインスタンスを作成"""
        return cls(
            id=data['id'],
            metadata=LectureMetadata.from_dict(data['metadata']),
            audio_file_path=data['audio_file_path'],
            pdf_file_path=data.get('pdf_file_path'),
            raw_transcript_path=data.get('raw_transcript_path'),
            processed_transcript_path=data.get('processed_transcript_path'),
            final_transcript_path=data.get('final_transcript_path'),
            status=LectureStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            processing_log=data.get('processing_log', []),
            custom_metadata=data.get('custom_metadata', {})
        )
