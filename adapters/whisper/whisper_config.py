"""
Whisper設定

Whisperの設定を管理します。
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class WhisperConfig:
    """Whisper設定"""
    model_size: str = "large-v3"
    device: str = "auto"
    compute_type: str = "auto"
    language: str = "ja"
    beam_size: int = 5
    best_of: int = 5
    temperature: List[float] = None
    vad_filter: bool = True
    vad_parameters: Optional[Dict[str, Any]] = None
    word_timestamps: bool = True
    condition_on_previous_text: bool = True
    initial_prompt: Optional[str] = None
    compression_ratio_threshold: float = 2.4
    log_prob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.temperature is None:
            self.temperature = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        
        if self.vad_parameters is None:
            self.vad_parameters = {
                'min_silence_duration_ms': 500,
                'speech_pad_ms': 400,
                'min_speech_duration_ms': 250,
                'max_speech_duration_s': 30.0
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'language': self.language,
            'beam_size': self.beam_size,
            'best_of': self.best_of,
            'temperature': self.temperature,
            'vad_filter': self.vad_filter,
            'vad_parameters': self.vad_parameters,
            'word_timestamps': self.word_timestamps,
            'condition_on_previous_text': self.condition_on_previous_text,
            'initial_prompt': self.initial_prompt,
            'compression_ratio_threshold': self.compression_ratio_threshold,
            'log_prob_threshold': self.log_prob_threshold,
            'no_speech_threshold': self.no_speech_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhisperConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        return [
            "tiny", "tiny.en", "base", "base.en", "small", "small.en",
            "medium", "medium.en", "large-v1", "large-v2", "large-v3"
        ]
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # モデルサイズの検証
        if self.model_size not in self.get_available_models():
            return False
        
        # デバイスの検証
        if self.device not in ["auto", "cpu", "cuda"]:
            return False
        
        # 計算タイプの検証
        if self.compute_type not in ["auto", "float16", "int8", "int8_float16"]:
            return False
        
        # 言語の検証
        if self.language not in ["ja", "en", "auto"]:
            return False
        
        # 数値パラメータの検証
        if self.beam_size < 1 or self.beam_size > 20:
            return False
        
        if self.best_of < 1 or self.best_of > 20:
            return False
        
        if not (0.0 <= self.compression_ratio_threshold <= 10.0):
            return False
        
        if not (-2.0 <= self.log_prob_threshold <= 1.0):
            return False
        
        if not (0.0 <= self.no_speech_threshold <= 1.0):
            return False
        
        return True
