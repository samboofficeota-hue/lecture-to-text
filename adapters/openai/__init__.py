"""
OpenAI関連アダプター

OpenAI APIとの連携を行います。
"""

from .openai_adapter import OpenAIAdapter
from .openai_config import OpenAIConfig

__all__ = [
    'OpenAIAdapter',
    'OpenAIConfig'
]
