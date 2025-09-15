"""
Whisperアダプター

Whisper音声認識エンジンとの連携を実装します。
"""

import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from faster_whisper import WhisperModel

from ...core.interfaces.audio_processor import AudioProcessor
from ...core.interfaces.transcriber import Transcriber, TranscriptionConfig
from ...core.models.audio_data import AudioData
from ...core.models.transcription_data import TranscriptionData, TranscriptionSegment
from ...utils.logging import get_logger

logger = get_logger(__name__)


class WhisperAdapter(AudioProcessor, Transcriber):
    """Whisperアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Whisperアダプターを初期化
        
        Args:
            config: Whisper設定
        """
        self.config = config or {}
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Whisperモデルを読み込み"""
        try:
            model_size = self.config.get('model_size', 'large-v3')
            device = self.config.get('device', 'auto')
            compute_type = self.config.get('compute_type', 'auto')
            
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    # AudioProcessor インターフェースの実装
    
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
            sample_rate: サンプルレート
            channels: チャンネル数
            
        Returns:
            AudioData: 抽出された音声データ
        """
        try:
            import ffmpeg
            
            # FFmpegを使用して音声を抽出
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path, 
                    ac=channels,           # チャンネル数
                    ar=sample_rate,        # サンプルレート
                    vn=None,               # 動画を無効化
                    y=None,                # 上書き確認を無効化
                    af="highpass=f=80,lowpass=f=8000,volume=1.2",  # 音声フィルタ
                    acodec='pcm_s16le'     # 16bit PCM
                )
                .run(quiet=True, overwrite_output=True)
            )
            
            # 音声データを作成
            audio_data = AudioData(
                file_path=output_path,
                file_size=Path(output_path).stat().st_size,
                duration=0.0,  # 後で更新
                sample_rate=sample_rate,
                channels=channels,
                bit_depth=16,
                format='wav',
                created_at=None,
                metadata={}
            )
            
            logger.info(f"Audio extracted: {input_path} -> {output_path}")
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise
    
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
        # 現在は基本的な前処理のみ実装
        # 実際の実装では、より詳細な音声処理を行う
        logger.info("Audio preprocessing completed")
        return audio_data
    
    def validate_audio(self, audio_data: AudioData) -> bool:
        """
        音声データの妥当性を検証する
        
        Args:
            audio_data: 検証する音声データ
            
        Returns:
            bool: 妥当性の結果
        """
        try:
            # 基本的な妥当性チェック
            if not Path(audio_data.file_path).exists():
                return False
            
            if audio_data.duration < 0.1:  # 0.1秒未満
                return False
            
            if audio_data.sample_rate < 8000:  # サンプルレートが低すぎる
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return False
    
    def get_audio_info(self, audio_data: AudioData) -> Dict[str, Any]:
        """
        音声データの情報を取得する
        
        Args:
            audio_data: 音声データ
            
        Returns:
            Dict[str, Any]: 音声情報
        """
        return {
            'file_path': audio_data.file_path,
            'file_size': audio_data.file_size,
            'duration': audio_data.duration,
            'sample_rate': audio_data.sample_rate,
            'channels': audio_data.channels,
            'bit_depth': audio_data.bit_depth,
            'format': audio_data.format
        }
    
    # Transcriber インターフェースの実装
    
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
        if config is None:
            config = TranscriptionConfig()
        
        try:
            # Whisperで文字起こし
            segments, info = self.model.transcribe(
                audio_data.file_path,
                language=config.language,
                beam_size=config.beam_size,
                best_of=config.best_of,
                temperature=config.temperature,
                vad_filter=config.vad_filter,
                vad_parameters=config.vad_parameters,
                word_timestamps=config.word_timestamps,
                condition_on_previous_text=config.condition_on_previous_text,
                initial_prompt=config.initial_prompt,
                compression_ratio_threshold=config.compression_ratio_threshold,
                log_prob_threshold=config.log_prob_threshold,
                no_speech_threshold=config.no_speech_threshold,
            )
            
            # セグメントを変換
            transcription_segments = []
            full_text_parts = []
            
            for segment in segments:
                start_time = segment.start if segment.start else 0.0
                end_time = segment.end if segment.end else start_time
                text = (segment.text or "").strip()
                
                if text:
                    transcription_segment = TranscriptionSegment(
                        start_time=start_time,
                        end_time=end_time,
                        text=text,
                        confidence=getattr(segment, 'avg_logprob', None),
                        language=config.language
                    )
                    transcription_segments.append(transcription_segment)
                    full_text_parts.append(text)
            
            # 文字起こしデータを作成
            transcription_data = TranscriptionData(
                segments=transcription_segments,
                full_text="\n".join(full_text_parts),
                language=config.language,
                model_used=self.config.get('model_size', 'unknown'),
                processing_time=0.0,  # 後で設定
                created_at=None,
                metadata={
                    'whisper_info': {
                        'language': info.language,
                        'language_probability': info.language_probability,
                        'duration': info.duration,
                        'all_language_probs': info.all_language_probs
                    }
                }
            )
            
            logger.info(f"Transcription completed: {len(transcription_segments)} segments")
            return transcription_data
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
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
        # 基本的には transcribe と同じ実装
        # タイムスタンプは既に含まれている
        return self.transcribe(audio_data, config)
    
    def get_available_models(self) -> List[str]:
        """
        利用可能なモデル一覧を取得する
        
        Returns:
            List[str]: モデル名のリスト
        """
        return [
            "tiny", "tiny.en", "base", "base.en", "small", "small.en",
            "medium", "medium.en", "large-v1", "large-v2", "large-v3"
        ]
    
    def validate_config(self, config: TranscriptionConfig) -> bool:
        """
        文字起こし設定の妥当性を検証する
        
        Args:
            config: 検証する設定
            
        Returns:
            bool: 妥当性の結果
        """
        try:
            # 基本的な妥当性チェック
            if config.beam_size < 1 or config.beam_size > 20:
                return False
            
            if config.best_of < 1 or config.best_of > 20:
                return False
            
            if config.language not in ["ja", "en", "auto"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False
