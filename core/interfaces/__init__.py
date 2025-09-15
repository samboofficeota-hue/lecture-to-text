"""
抽象インターフェース定義

各機能の抽象インターフェースを定義し、依存性の逆転を実現します。
具体的な実装は adapters/ 層で提供されます。
"""

from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .text_processor import TextProcessor
from .output_generator import OutputGenerator
from .rag_interface import RAGInterface
from .pdf_processor import PDFProcessor

__all__ = [
    'AudioProcessor',
    'Transcriber',
    'TextProcessor',
    'OutputGenerator',
    'RAGInterface',
    'PDFProcessor'
]
