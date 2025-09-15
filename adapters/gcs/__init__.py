"""
Google Cloud Storage関連アダプター

GCSとの連携を行います。
"""

from .gcs_adapter import GCSAdapter
from .gcs_config import GCSConfig

__all__ = [
    'GCSAdapter',
    'GCSConfig'
]
