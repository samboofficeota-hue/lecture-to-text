"""
音声処理サービス

音声ファイルの処理に関するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any
from pathlib import Path

from ..interfaces.audio_processor import AudioProcessor
from ..models.audio_data import AudioData


class AudioService:
    """音声処理サービス"""
    
    def __init__(self, audio_processor: AudioProcessor):
        """
        音声処理サービスを初期化
        
        Args:
            audio_processor: 音声処理アダプター
        """
        self.audio_processor = audio_processor
    
    def process_audio_file(
        self, 
        input_path: str, 
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1,
        filters: Optional[Dict[str, Any]] = None
    ) -> AudioData:
        """
        音声ファイルを処理する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            sample_rate: サンプルレート
            channels: チャンネル数
            filters: 適用するフィルタ
            
        Returns:
            AudioData: 処理済み音声データ
        """
        # 音声抽出
        audio_data = self.audio_processor.extract_audio(
            input_path, output_path, sample_rate, channels
        )
        
        # 前処理
        if filters:
            audio_data = self.audio_processor.preprocess_audio(audio_data, filters)
        
        # 妥当性検証
        if not self.audio_processor.validate_audio(audio_data):
            raise ValueError("Invalid audio data")
        
        return audio_data
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        音声ファイルの妥当性を検証する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 妥当性の結果
        """
        if not Path(file_path).exists():
            return False
        
        try:
            # 一時的な音声データを作成して検証
            temp_audio = AudioData(
                file_path=file_path,
                file_size=0,
                duration=0,
                sample_rate=0,
                channels=0,
                bit_depth=0,
                format="",
                created_at=None,
                metadata={}
            )
            return self.audio_processor.validate_audio(temp_audio)
        except Exception:
            return False
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        音声ファイルの情報を取得する
        
        Args:
            file_path: ファイルパス
            
        Returns:
            Dict[str, Any]: 音声情報
        """
        if not self.validate_audio_file(file_path):
            raise ValueError("Invalid audio file")
        
        # 音声データを作成
        audio_data = AudioData(
            file_path=file_path,
            file_size=Path(file_path).stat().st_size,
            duration=0,
            sample_rate=0,
            channels=0,
            bit_depth=0,
            format=Path(file_path).suffix,
            created_at=None,
            metadata={}
        )
        
        return self.audio_processor.get_audio_info(audio_data)
    
    def optimize_for_transcription(
        self, 
        input_path: str, 
        output_path: str
    ) -> AudioData:
        """
        文字起こし用に音声を最適化する
        
        Args:
            input_path: 入力ファイルパス
            output_path: 出力ファイルパス
            
        Returns:
            AudioData: 最適化済み音声データ
        """
        # 文字起こし用の最適化設定
        filters = {
            'highpass': 80,
            'lowpass': 8000,
            'volume': 1.2,
            'noise_reduction': True
        }
        
        return self.process_audio_file(
            input_path, 
            output_path, 
            sample_rate=16000, 
            channels=1, 
            filters=filters
        )
