"""
文字起こしサービス

音声データの文字起こしに関するビジネスロジックを実装します。
"""

from typing import Optional, List, Dict, Any
import time

from ..interfaces.transcriber import Transcriber, TranscriptionConfig
from ..models.audio_data import AudioData
from ..models.transcription_data import TranscriptionData


class TranscriptionService:
    """文字起こしサービス"""
    
    def __init__(self, transcriber: Transcriber):
        """
        文字起こしサービスを初期化
        
        Args:
            transcriber: 文字起こしアダプター
        """
        self.transcriber = transcriber
    
    def transcribe_audio(
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
        if config is None:
            config = TranscriptionConfig()
        
        # 設定の妥当性を検証
        if not self.transcriber.validate_config(config):
            raise ValueError("Invalid transcription config")
        
        # 文字起こし実行
        start_time = time.time()
        result = self.transcriber.transcribe(audio_data, config)
        processing_time = time.time() - start_time
        
        # 処理時間を設定
        result.processing_time = processing_time
        
        return result
    
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
        if config is None:
            config = TranscriptionConfig()
        
        # 設定の妥当性を検証
        if not self.transcriber.validate_config(config):
            raise ValueError("Invalid transcription config")
        
        # タイムスタンプ付き文字起こし実行
        start_time = time.time()
        result = self.transcriber.transcribe_with_timestamps(audio_data, config)
        processing_time = time.time() - start_time
        
        # 処理時間を設定
        result.processing_time = processing_time
        
        return result
    
    def get_available_models(self) -> List[str]:
        """
        利用可能なモデル一覧を取得する
        
        Returns:
            List[str]: モデル名のリスト
        """
        return self.transcriber.get_available_models()
    
    def create_optimized_config(
        self, 
        domain: str,
        language: str = "ja"
    ) -> TranscriptionConfig:
        """
        分野に最適化された設定を作成する
        
        Args:
            domain: 分野
            language: 言語
            
        Returns:
            TranscriptionConfig: 最適化された設定
        """
        # 分野別の最適化設定
        domain_configs = {
            "会計・財務": {
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "initial_prompt": "これは会計・財務の講義です。専門用語が多く含まれています。"
            },
            "技術・工学": {
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "initial_prompt": "これは技術・工学の講義です。専門用語が多く含まれています。"
            },
            "経済学": {
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "initial_prompt": "これは経済学の講義です。専門用語が多く含まれています。"
            }
        }
        
        config_dict = domain_configs.get(domain, domain_configs["会計・財務"])
        config_dict["language"] = language
        
        return TranscriptionConfig(**config_dict)
    
    def validate_audio_for_transcription(self, audio_data: AudioData) -> bool:
        """
        文字起こし用の音声データの妥当性を検証する
        
        Args:
            audio_data: 音声データ
            
        Returns:
            bool: 妥当性の結果
        """
        # 基本的な妥当性チェック
        if audio_data.duration < 1.0:  # 1秒未満
            return False
        
        if audio_data.sample_rate < 8000:  # サンプルレートが低すぎる
            return False
        
        if audio_data.channels > 2:  # ステレオ以上
            return False
        
        return True
