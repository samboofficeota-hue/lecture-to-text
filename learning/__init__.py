"""
学習・適応機能層

Darwin プロジェクトの学習・適応機能を提供します。
"""

from .glossary.glossary_manager import GlossaryManager
from .correction.correction_learner import CorrectionLearner
from .domain.domain_detector import DomainDetector
from .rag.rag_manager import RAGManager

__all__ = [
    'GlossaryManager',
    'CorrectionLearner',
    'DomainDetector',
    'RAGManager'
]
