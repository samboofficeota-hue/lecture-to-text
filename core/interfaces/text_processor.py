"""
テキスト処理インターフェース

文字起こしテキストの後処理、修正、統一を行う抽象インターフェースを定義します。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..models.transcription_data import TranscriptionData
from ..models.processing_result import ProcessingResult


@dataclass
class TextProcessingConfig:
    """テキスト処理設定"""
    enable_postprocessing: bool = True
    enable_glossary_application: bool = True
    enable_rag_correction: bool = True
    enable_concept_unification: bool = True
    domain: Optional[str] = None
    glossary_path: Optional[str] = None
    rag_config: Optional[Dict[str, Any]] = None


class TextProcessor(ABC):
    """テキスト処理の抽象インターフェース"""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def postprocess_text(
        self, 
        text: str,
        domain: Optional[str] = None
    ) -> str:
        """
        テキストの後処理を行う
        
        Args:
            text: 処理するテキスト
            domain: 分野（会計、技術等）
            
        Returns:
            str: 後処理済みテキスト
        """
        pass
    
    @abstractmethod
    def apply_glossary(
        self, 
        text: str,
        glossary: Dict[str, str]
    ) -> str:
        """
        用語辞書を適用する
        
        Args:
            text: 処理するテキスト
            glossary: 用語辞書
            
        Returns:
            str: 辞書適用済みテキスト
        """
        pass
    
    @abstractmethod
    def unify_concepts(
        self, 
        text: str,
        domain: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        概念・理論の統一性を保つ
        
        Args:
            text: 処理するテキスト
            domain: 分野
            context: 文脈情報
            
        Returns:
            str: 概念統一済みテキスト
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
