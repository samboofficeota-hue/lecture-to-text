"""
修正学習

ユーザーの修正から学習します。
"""

from .correction_learner import CorrectionLearner
from .correction_patterns import CorrectionPatterns

__all__ = [
    'CorrectionLearner',
    'CorrectionPatterns'
]
