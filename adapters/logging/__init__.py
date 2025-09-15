"""
ログ管理アダプター

Cloud Loggingとの連携を行います。
"""

from .cloud_logging_adapter import CloudLoggingAdapter
from .logging_config import LoggingConfig

__all__ = [
    'CloudLoggingAdapter',
    'LoggingConfig'
]
