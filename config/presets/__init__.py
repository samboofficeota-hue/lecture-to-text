"""
プリセット管理

分野別の設定プリセットを管理します。
"""

from .preset_manager import PresetManager
from .domain_presets import (
    DomainPreset,
    DOMAIN_PRESETS,
    get_domain_preset,
    list_available_domains
)

__all__ = [
    'PresetManager',
    'DomainPreset',
    'DOMAIN_PRESETS',
    'get_domain_preset',
    'list_available_domains'
]
