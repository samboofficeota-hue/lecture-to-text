"""
プリセット管理

分野別の設定プリセットを管理します。
"""

from .preset_manager import PresetManager
from .domain_presets import (
    AccountingFinancePreset,
    TechnicalPreset,
    EconomicsPreset,
    BusinessPreset
)

__all__ = [
    'PresetManager',
    'AccountingFinancePreset',
    'TechnicalPreset',
    'EconomicsPreset',
    'BusinessPreset'
]
