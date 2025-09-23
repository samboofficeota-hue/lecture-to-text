"""
処理結果データモデル

テキスト処理の結果とメタデータを管理するデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """処理ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingResult:
    """処理結果"""
    raw_text: str
    processed_text: str
    enhanced_text: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    processing_time: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None
    # 追加属性
    audio_duration: float = 0.0
    transcription: Optional[Any] = None
    technical_terms: List[str] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.technical_terms is None:
            self.technical_terms = []
    
    @property
    def word_count(self) -> int:
        """単語数を取得"""
        return len(self.processed_text.split())
    
    @property
    def character_count(self) -> int:
        """文字数を取得"""
        return len(self.processed_text)
    
    @property
    def processing_duration(self) -> float:
        """処理時間を取得"""
        return self.processing_time
    
    def get_quality_score(self) -> float:
        """品質スコアを取得"""
        # 基本的な品質指標を計算
        if not self.processed_text:
            return 0.0
        
        # 文字数ベースの品質スコア（簡易版）
        char_count = self.character_count
        if char_count < 100:
            return 0.5
        elif char_count < 500:
            return 0.7
        elif char_count < 1000:
            return 0.8
        else:
            return 0.9
    
    def get_unknown_terms(self) -> List[str]:
        """未知語を取得"""
        return self.metadata.get('unknown_terms', [])
    
    def get_applied_glossary(self) -> Dict[str, str]:
        """適用された辞書を取得"""
        return self.metadata.get('applied_glossary', {})
    
    def get_rag_corrections(self) -> List[Dict[str, Any]]:
        """RAG修正を取得"""
        return self.metadata.get('rag_corrections', [])
    
    def add_metadata(self, key: str, value: Any) -> None:
        """メタデータを追加"""
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def update_status(self, status: ProcessingStatus) -> None:
        """ステータスを更新"""
        self.status = status
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'raw_text': self.raw_text,
            'processed_text': self.processed_text,
            'enhanced_text': self.enhanced_text,
            'status': self.status.value,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
            'audio_duration': self.audio_duration,
            'transcription': self.transcription.to_dict() if self.transcription else None,
            'technical_terms': self.technical_terms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingResult':
        """辞書からインスタンスを作成"""
        return cls(
            raw_text=data['raw_text'],
            processed_text=data['processed_text'],
            enhanced_text=data.get('enhanced_text'),
            status=ProcessingStatus(data['status']),
            processing_time=data['processing_time'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {}),
            audio_duration=data.get('audio_duration', 0.0),
            transcription=data.get('transcription'),
            technical_terms=data.get('technical_terms', [])
        )
