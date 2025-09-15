"""
外部サービス連携層

外部サービスとの連携を行うアダプター層を提供します。
"""

from .whisper.whisper_adapter import WhisperAdapter
from .openai.openai_adapter import OpenAIAdapter
from .file.file_adapter import FileAdapter
from .mygpt.mygpt_adapter import MyGPTAdapter
from .gcs.gcs_adapter import GCSAdapter
from .database.database_adapter import DatabaseAdapter
from .logging.cloud_logging_adapter import CloudLoggingAdapter
from .tasks.cloud_tasks_adapter import CloudTasksAdapter
from .pubsub.pubsub_adapter import PubSubAdapter
from .cloudflare.cloudflare_adapter import CloudFlareAdapter

__all__ = [
    'WhisperAdapter',
    'OpenAIAdapter',
    'FileAdapter',
    'MyGPTAdapter',
    'GCSAdapter',
    'DatabaseAdapter',
    'CloudLoggingAdapter',
    'CloudTasksAdapter',
    'PubSubAdapter',
    'CloudFlareAdapter'
]
