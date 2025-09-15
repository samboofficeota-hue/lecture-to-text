"""
文字起こしデータモデル

文字起こし結果とセグメント情報を管理するデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class TranscriptionSegment:
    """文字起こしセグメント"""
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None
    language: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """セグメントの長さを取得"""
        return self.end_time - self.start_time
    
    @property
    def start_time_formatted(self) -> str:
        """フォーマットされた開始時間を取得"""
        return self._format_time(self.start_time)
    
    @property
    def end_time_formatted(self) -> str:
        """フォーマットされた終了時間を取得"""
        return self._format_time(self.end_time)
    
    def _format_time(self, seconds: float) -> str:
        """時間をフォーマット"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text,
            'confidence': self.confidence,
            'speaker': self.speaker,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionSegment':
        """辞書からインスタンスを作成"""
        return cls(
            start_time=data['start_time'],
            end_time=data['end_time'],
            text=data['text'],
            confidence=data.get('confidence'),
            speaker=data.get('speaker'),
            language=data.get('language')
        )


@dataclass
class TranscriptionData:
    """文字起こしデータ"""
    segments: List[TranscriptionSegment]
    full_text: str
    language: str
    model_used: str
    processing_time: float
    created_at: datetime
    metadata: Dict[str, Any]
    
    @property
    def total_duration(self) -> float:
        """総再生時間を取得"""
        if not self.segments:
            return 0.0
        return max(segment.end_time for segment in self.segments)
    
    @property
    def word_count(self) -> int:
        """単語数を取得"""
        return len(self.full_text.split())
    
    @property
    def segment_count(self) -> int:
        """セグメント数を取得"""
        return len(self.segments)
    
    def get_segments_by_time_range(
        self, 
        start_time: float, 
        end_time: float
    ) -> List[TranscriptionSegment]:
        """指定時間範囲のセグメントを取得"""
        return [
            segment for segment in self.segments
            if segment.start_time >= start_time and segment.end_time <= end_time
        ]
    
    def get_text_by_time_range(
        self, 
        start_time: float, 
        end_time: float
    ) -> str:
        """指定時間範囲のテキストを取得"""
        segments = self.get_segments_by_time_range(start_time, end_time)
        return " ".join(segment.text for segment in segments)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'segments': [segment.to_dict() for segment in self.segments],
            'full_text': self.full_text,
            'language': self.language,
            'model_used': self.model_used,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptionData':
        """辞書からインスタンスを作成"""
        return cls(
            segments=[TranscriptionSegment.from_dict(seg) for seg in data['segments']],
            full_text=data['full_text'],
            language=data['language'],
            model_used=data['model_used'],
            processing_time=data['processing_time'],
            created_at=datetime.fromisoformat(data['created_at']),
            metadata=data['metadata']
        )
