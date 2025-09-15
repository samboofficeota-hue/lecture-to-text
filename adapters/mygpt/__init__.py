"""
My GPTs関連アダプター

My GPTsとの連携を行います。
"""

from .mygpt_adapter import MyGPTAdapter
from .mygpt_config import MyGPTConfig

__all__ = [
    'MyGPTAdapter',
    'MyGPTConfig'
]
