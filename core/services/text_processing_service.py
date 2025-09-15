"""
テキスト処理サービス

文字起こしテキストの処理に関するビジネスロジックを実装します。
"""

from typing import Optional, Dict, Any, List, Tuple
import time

from ..interfaces.text_processor import TextProcessor, TextProcessingConfig
from ..interfaces.rag_interface import RAGInterface, RAGConfig
from ..models.transcription_data import TranscriptionData
from ..models.processing_result import ProcessingResult, ProcessingStatus


class TextProcessingService:
    """テキスト処理サービス"""
    
    def __init__(
        self, 
        text_processor: TextProcessor,
        rag_interface: Optional[RAGInterface] = None
    ):
        """
        テキスト処理サービスを初期化
        
        Args:
            text_processor: テキスト処理アダプター
            rag_interface: RAGインターフェース（オプション）
        """
        self.text_processor = text_processor
        self.rag_interface = rag_interface
    
    def process_transcription(
        self, 
        transcription_data: TranscriptionData,
        config: Optional[TextProcessingConfig] = None
    ) -> ProcessingResult:
        """
        文字起こしテキストを処理する
        
        Args:
            transcription_data: 文字起こしデータ
            config: 処理設定
            
        Returns:
            ProcessingResult: 処理結果
        """
        if config is None:
            config = TextProcessingConfig()
        
        start_time = time.time()
        
        try:
            # ステータスを処理中に更新
            result = ProcessingResult(
                raw_text=transcription_data.full_text,
                processed_text="",
                status=ProcessingStatus.PROCESSING
            )
            
            # 基本的なテキスト処理
            processed_text = transcription_data.full_text
            
            # 後処理
            if config.enable_postprocessing:
                processed_text = self.text_processor.postprocess_text(
                    processed_text, config.domain
                )
            
            # 辞書適用
            if config.enable_glossary_application and config.glossary_path:
                # 辞書を読み込み（簡易版）
                glossary = self._load_glossary(config.glossary_path)
                processed_text = self.text_processor.apply_glossary(
                    processed_text, glossary
                )
            
            # 概念統一
            if config.enable_concept_unification and config.domain:
                processed_text = self.text_processor.unify_concepts(
                    processed_text, config.domain
                )
            
            # RAG処理
            if config.enable_rag_correction and self.rag_interface:
                rag_config = RAGConfig(
                    domain=config.domain,
                    **config.rag_config or {}
                )
                processed_text = self.rag_interface.process_with_rag(
                    processed_text, rag_config
                )
            
            # 結果を設定
            result.processed_text = processed_text
            result.status = ProcessingStatus.COMPLETED
            result.processing_time = time.time() - start_time
            
            # メタデータを追加
            result.add_metadata('domain', config.domain)
            result.add_metadata('processing_config', config.__dict__)
            
            return result
            
        except Exception as e:
            # エラー処理
            result = ProcessingResult(
                raw_text=transcription_data.full_text,
                processed_text="",
                status=ProcessingStatus.FAILED
            )
            result.add_metadata('error', str(e))
            result.processing_time = time.time() - start_time
            return result
    
    def extract_unknown_terms(
        self, 
        text: str,
        known_terms: List[str],
        top_k: int = 200
    ) -> List[Tuple[str, int]]:
        """
        未知語候補を抽出する
        
        Args:
            text: 処理するテキスト
            known_terms: 既知の用語リスト
            top_k: 抽出する上位k個
            
        Returns:
            List[Tuple[str, int]]: (用語, 頻度)のリスト
        """
        return self.text_processor.extract_unknown_terms(
            text, known_terms, top_k
        )
    
    def validate_text_quality(
        self, 
        text: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        テキスト品質を検証する
        
        Args:
            text: 検証するテキスト
            domain: 分野
            
        Returns:
            Dict[str, Any]: 品質評価結果
        """
        return self.text_processor.validate_text_quality(text, domain)
    
    def process_with_rag(
        self, 
        text: str,
        domain: str,
        rag_config: Optional[RAGConfig] = None
    ) -> str:
        """
        RAGを使用してテキストを処理する
        
        Args:
            text: 処理するテキスト
            domain: 分野
            rag_config: RAG設定
            
        Returns:
            str: 処理済みテキスト
        """
        if not self.rag_interface:
            raise ValueError("RAG interface not available")
        
        if rag_config is None:
            rag_config = RAGConfig(domain=domain)
        
        return self.rag_interface.process_with_rag(text, rag_config)
    
    def _load_glossary(self, glossary_path: str) -> Dict[str, str]:
        """
        辞書を読み込む（簡易版）
        
        Args:
            glossary_path: 辞書ファイルパス
            
        Returns:
            Dict[str, str]: 辞書
        """
        # 簡易実装（実際は適切な辞書読み込み処理を実装）
        return {}
