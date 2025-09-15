"""
音声処理インターフェース

音声ファイルの前処理、変換、最適化を行う抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from ..models.audio_data import AudioData


class AudioProcessor(ABC):
    """音声処理の抽象インターフェース"""
    
    @abstractmethod
    def extract_audio(
        self, 
        input_path: str, 
        output_path: str, 
        sample_rate: int = 16000,
        channels: int = 1
    ) -> AudioData:
        """
        音声ファイルから音声データを抽出する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            sample_rate: サンプルレート（デフォルト: 16000Hz）
            channels: チャンネル数（デフォルト: 1=モノラル）
            
        Returns:
            AudioData: 抽出された音声データ
        """
        pass
    
    @abstractmethod
    def preprocess_audio(
        self, 
        audio_data: AudioData,
        filters: Optional[Dict[str, Any]] = None
    ) -> AudioData:
        """
        音声データの前処理を行う
        
        Args:
            audio_data: 音声データ
            filters: 適用するフィルタ設定
            
        Returns:
            AudioData: 前処理済み音声データ
        """
        pass
    
    @abstractmethod
    def validate_audio(self, audio_data: AudioData) -> bool:
        """
        音声データの妥当性を検証する
        
        Args:
            audio_data: 検証する音声データ
            
        Returns:
            bool: 妥当性の結果
        """
        pass
    
    @abstractmethod
    def get_audio_info(self, audio_data: AudioData) -> Dict[str, Any]:
        """
        音声データの情報を取得する
        
        Args:
            audio_data: 音声データ
            
        Returns:
            Dict[str, Any]: 音声情報（長さ、サンプルレート等）
        """
        pass
