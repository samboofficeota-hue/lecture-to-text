"""
文字起こしインターフェース

音声データからテキストへの変換を行う抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..models.audio_data import AudioData
from ..models.transcription_data import TranscriptionData


@dataclass
class TranscriptionConfig:
    """文字起こし設定"""
    model_size: str = "large-v3"
    device: str = "auto"
    compute_type: str = "auto"
    language: str = "ja"
    beam_size: int = 5
    best_of: int = 5
    temperature: List[float] = None
    vad_filter: bool = True
    word_timestamps: bool = True
    initial_prompt: Optional[str] = None
    
    def __post_init__(self):
        if self.temperature is None:
            self.temperature = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]


class Transcriber(ABC):
    """文字起こしの抽象インターフェース"""
    
    @abstractmethod
    def transcribe(
        self, 
        audio_data: AudioData,
        config: Optional[TranscriptionConfig] = None
    ) -> TranscriptionData:
        """
        音声データを文字起こしする
        
        Args:
            audio_data: 音声データ
            config: 文字起こし設定
            
        Returns:
            TranscriptionData: 文字起こし結果
        """
        pass
    
    @abstractmethod
    def transcribe_with_timestamps(
        self, 
        audio_data: AudioData,
        config: Optional[TranscriptionConfig] = None
    ) -> TranscriptionData:
        """
        タイムスタンプ付きで文字起こしする
        
        Args:
            audio_data: 音声データ
            config: 文字起こし設定
            
        Returns:
            TranscriptionData: タイムスタンプ付き文字起こし結果
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        利用可能なモデル一覧を取得する
        
        Returns:
            List[str]: モデル名のリスト
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: TranscriptionConfig) -> bool:
        """
        文字起こし設定の妥当性を検証する
        
        Args:
            config: 検証する設定
            
        Returns:
            bool: 妥当性の結果
        """
        pass
