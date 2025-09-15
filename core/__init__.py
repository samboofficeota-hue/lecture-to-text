"""
Darwin プロジェクト - コア機能層

このパッケージは、講義録作成システムのコア機能を提供します。
関心の分離の原則に基づいて、以下の層に分かれています：

- interfaces: 抽象インターフェース定義
- services: ビジネスロジック実装
- models: データモデル定義
"""

from .interfaces import (
    AudioProcessor,
    Transcriber,
    TextProcessor,
    OutputGenerator,
    RAGInterface,
    PDFProcessor
)

from .services import (
    AudioService,
    TranscriptionService,
    TextProcessingService,
    OutputService,
    RAGService,
    PDFAnalysisService
)

from .models import (
    AudioData,
    TranscriptionData,
    ProcessingResult,
    LectureRecord,
    MasterText
)

__all__ = [
    # Interfaces
    'AudioProcessor',
    'Transcriber',
    'TextProcessor',
    'OutputGenerator',
    'RAGInterface',
    'PDFProcessor',
    
    # Services
    'AudioService',
    'TranscriptionService',
    'TextProcessingService',
    'OutputService',
    'RAGService',
    'PDFAnalysisService',
    
    # Models
    'AudioData',
    'TranscriptionData',
    'ProcessingResult',
    'LectureRecord',
    'MasterText'
]
