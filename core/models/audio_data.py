"""
音声データモデル

音声ファイルの情報とメタデータを管理するデータモデルを定義します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime


@dataclass
class AudioData:
    """音声データ"""
    file_path: str
    file_size: int
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    format: str
    created_at: datetime
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        """初期化後の処理"""
        if not Path(self.file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")
    
    @property
    def file_name(self) -> str:
        """ファイル名を取得"""
        return Path(self.file_path).name
    
    @property
    def file_extension(self) -> str:
        """ファイル拡張子を取得"""
        return Path(self.file_path).suffix.lower()
    
    @property
    def duration_formatted(self) -> str:
        """フォーマットされた再生時間を取得"""
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration': self.duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bit_depth': self.bit_depth,
            'format': self.format,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioData':
        """辞書からインスタンスを作成"""
        return cls(
            file_path=data['file_path'],
            file_size=data['file_size'],
            duration=data['duration'],
            sample_rate=data['sample_rate'],
            channels=data['channels'],
            bit_depth=data['bit_depth'],
            format=data['format'],
            created_at=datetime.fromisoformat(data['created_at']),
            metadata=data['metadata']
        )
