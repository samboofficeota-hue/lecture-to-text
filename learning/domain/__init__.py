"""
分野検出

テキストの分野を自動検出します。
"""

from .domain_detector import DomainDetector
from .domain_classifier import DomainClassifier

__all__ = [
    'DomainDetector',
    'DomainClassifier'
]
