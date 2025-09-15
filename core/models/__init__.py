"""
データモデル定義

講義録作成システムで使用するデータモデルを定義します。
"""

from .audio_data import AudioData
from .transcription_data import TranscriptionData, TranscriptionSegment
from .processing_result import ProcessingResult
from .lecture_record import LectureRecord, LectureMetadata
from .master_text import MasterText, MasterTextVersion

__all__ = [
    'AudioData',
    'TranscriptionData',
    'TranscriptionSegment',
    'ProcessingResult',
    'LectureRecord',
    'LectureMetadata',
    'MasterText',
    'MasterTextVersion'
]
