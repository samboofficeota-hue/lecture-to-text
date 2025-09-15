"""
Whisper関連アダプター

Whisper音声認識エンジンとの連携を行います。
"""

from .whisper_adapter import WhisperAdapter
from .whisper_config import WhisperConfig

__all__ = [
    'WhisperAdapter',
    'WhisperConfig'
]
