"""
OpenAIアダプター

OpenAI APIとの連携を実装します。
"""

import time
from typing import Optional, Dict, Any, List, Tuple
import openai
from openai import OpenAI

from ...core.interfaces.rag_interface import RAGInterface, RAGConfig, KnowledgeItem
from ...core.interfaces.text_processor import TextProcessor, TextProcessingConfig
from ...core.interfaces.output_generator import OutputGenerator, OutputConfig, OutputFormat
from ...core.models.processing_result import ProcessingResult
from ...utils.logging import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(RAGInterface, TextProcessor, OutputGenerator):
    """OpenAIアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        OpenAIアダプターを初期化
        
        Args:
            config: OpenAI設定
        """
        self.config = config or {}
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAIクライアントを初期化"""
        try:
            api_key = self.config.get('api_key', '')
            base_url = self.config.get('base_url')
            organization = self.config.get('organization')
            
            if not api_key:
                raise ValueError("OpenAI API key is required")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                organization=organization
            )
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    # RAGInterface インターフェースの実装
    
    def process_with_rag(
        self, 
        text: str,
        config: Optional[RAGConfig] = None
    ) -> str:
        """
        RAGを使用してテキストを処理する
        
        Args:
            text: 処理するテキスト
            config: RAG設定
            
        Returns:
            str: 処理済みテキスト
        """
        if config is None:
            config = RAGConfig()
        
        try:
            # プロンプトを構築
            prompt = self._build_rag_prompt(text, config)
            
            # OpenAI APIを呼び出し
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは専門的な講義録の品質向上を支援するAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("RAG processing completed")
            return result
            
        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            return text  # フォールバック
    
    def retrieve_knowledge(
        self, 
        query: str,
        domain: Optional[str] = None,
        top_k: int = 5
    ) -> List[KnowledgeItem]:
        """
        知識ベースから関連情報を検索する
        
        Args:
            query: 検索クエリ
            domain: 分野
            top_k: 取得する上位k個
            
        Returns:
            List[KnowledgeItem]: 関連知識アイテム
        """
        # 簡易実装：実際の実装では、ベクトルデータベースを使用
        logger.warning("Knowledge retrieval not implemented yet")
        return []
    
    def add_knowledge(
        self, 
        knowledge_item: KnowledgeItem
    ) -> bool:
        """
        知識ベースに新しい知識を追加する
        
        Args:
            knowledge_item: 追加する知識アイテム
            
        Returns:
            bool: 追加の成功/失敗
        """
        # 簡易実装：実際の実装では、ベクトルデータベースを使用
        logger.warning("Knowledge addition not implemented yet")
        return True
    
    def update_knowledge(
        self, 
        knowledge_id: str,
        updated_content: str
    ) -> bool:
        """
        既存の知識を更新する
        
        Args:
            knowledge_id: 更新する知識のID
            updated_content: 更新内容
            
        Returns:
            bool: 更新の成功/失敗
        """
        # 簡易実装：実際の実装では、ベクトルデータベースを使用
        logger.warning("Knowledge update not implemented yet")
        return True
    
    def search_similar_terms(
        self, 
        term: str,
        domain: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        類似用語を検索する
        
        Args:
            term: 検索する用語
            domain: 分野
            
        Returns:
            List[Tuple[str, float]]: (用語, 類似度)のリスト
        """
        # 簡易実装：実際の実装では、埋め込みモデルを使用
        logger.warning("Similar term search not implemented yet")
        return []
    
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
        try:
            prompt = f"""
以下の{domain}分野のテキストについて、概念・理論の統一性を保つように修正してください。

テキスト:
{text}

修正のポイント:
1. 同じ概念を表す用語は統一する
2. 専門用語の表記を統一する
3. 理論の体系性を保つ
4. 文脈に応じた適切な表現を選択する

修正されたテキストを出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": f"あなたは{domain}分野の専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Concept unification completed")
            return result
            
        except Exception as e:
            logger.error(f"Concept unification failed: {e}")
            return text  # フォールバック
    
    def validate_terminology(
        self, 
        text: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        専門用語の妥当性を検証する
        
        Args:
            text: 検証するテキスト
            domain: 分野
            
        Returns:
            Dict[str, Any]: 検証結果
        """
        try:
            prompt = f"""
以下の{domain}分野のテキストについて、専門用語の妥当性を検証してください。

テキスト:
{text}

検証項目:
1. 専門用語の正確性
2. 用語の統一性
3. 文脈に適した用語の使用
4. 誤字・脱字の有無

検証結果をJSON形式で出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": f"あなたは{domain}分野の専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Terminology validation completed")
            
            # 簡易実装：実際の実装では、JSONをパース
            return {
                'valid': True,
                'issues': [],
                'suggestions': []
            }
            
        except Exception as e:
            logger.error(f"Terminology validation failed: {e}")
            return {'valid': False, 'error': str(e)}
    
    def get_domain_knowledge(
        self, 
        domain: str
    ) -> List[KnowledgeItem]:
        """
        分野別の知識を取得する
        
        Args:
            domain: 分野
            
        Returns:
            List[KnowledgeItem]: 分野別知識
        """
        # 簡易実装：実際の実装では、ベクトルデータベースを使用
        logger.warning("Domain knowledge retrieval not implemented yet")
        return []
    
    # TextProcessor インターフェースの実装
    
    def process_transcription(
        self, 
        transcription_data,
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
        # 簡易実装：実際の実装では、より詳細な処理を行う
        logger.warning("Text processing not fully implemented yet")
        
        return ProcessingResult(
            raw_text=transcription_data.full_text,
            processed_text=transcription_data.full_text,
            status=None
        )
    
    def postprocess_text(
        self, 
        text: str,
        domain: Optional[str] = None
    ) -> str:
        """
        テキストの後処理を行う
        
        Args:
            text: 処理するテキスト
            domain: 分野
            
        Returns:
            str: 後処理済みテキスト
        """
        try:
            prompt = f"""
以下のテキストについて、後処理を行ってください。

テキスト:
{text}

後処理のポイント:
1. 誤認識の修正
2. 句読点の調整
3. 専門用語の修正
4. 文の流れの改善

修正されたテキストを出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたはテキストの後処理を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Text postprocessing completed")
            return result
            
        except Exception as e:
            logger.error(f"Text postprocessing failed: {e}")
            return text  # フォールバック
    
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
        # 簡易実装：実際の実装では、より詳細な処理を行う
        result = text
        for term, replacement in glossary.items():
            result = result.replace(term, replacement)
        return result
    
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
        # RAGInterfaceの実装を再利用
        return self.unify_concepts(text, domain, context)
    
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
        # 簡易実装：実際の実装では、より詳細な処理を行う
        logger.warning("Unknown term extraction not implemented yet")
        return []
    
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
        # 簡易実装：実際の実装では、より詳細な処理を行う
        logger.warning("Text quality validation not implemented yet")
        return {'quality_score': 0.8, 'issues': []}
    
    # OutputGenerator インターフェースの実装
    
    def generate_output(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        処理結果から出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: 生成された出力
        """
        if config is None:
            config = OutputConfig()
        
        try:
            prompt = f"""
以下の講義録テキストから、{config.title}の形式で出力を生成してください。

テキスト:
{processing_result.processed_text}

出力形式: {config.format.value}
タイムスタンプを含む: {config.include_timestamps}
用語集を含む: {config.include_glossary}
サマリーを含む: {config.include_summary}
確認問題を含む: {config.include_questions}

適切な形式で出力を生成してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは講義録の出力生成を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Output generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Output generation failed: {e}")
            return processing_result.processed_text  # フォールバック
    
    def generate_markdown(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        Markdown形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: Markdown形式の出力
        """
        if config is None:
            config = OutputConfig(format=OutputFormat.MARKDOWN)
        
        return self.generate_output(processing_result, config)
    
    def generate_html(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> str:
        """
        HTML形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            str: HTML形式の出力
        """
        if config is None:
            config = OutputConfig(format=OutputFormat.HTML)
        
        return self.generate_output(processing_result, config)
    
    def generate_pdf(
        self, 
        processing_result: ProcessingResult,
        config: Optional[OutputConfig] = None
    ) -> bytes:
        """
        PDF形式で出力を生成する
        
        Args:
            processing_result: 処理結果
            config: 出力設定
            
        Returns:
            bytes: PDF形式の出力
        """
        # 簡易実装：実際の実装では、PDF生成ライブラリを使用
        logger.warning("PDF generation not implemented yet")
        return b""
    
    def generate_summary(
        self, 
        processing_result: ProcessingResult,
        max_length: int = 1000
    ) -> str:
        """
        サマリーを生成する
        
        Args:
            processing_result: 処理結果
            max_length: 最大文字数
            
        Returns:
            str: サマリー
        """
        try:
            prompt = f"""
以下の講義録テキストから、{max_length}文字以内でサマリーを生成してください。

テキスト:
{processing_result.processed_text}

サマリーのポイント:
1. 主要な内容を簡潔にまとめる
2. 重要なキーワードを含める
3. 講義の流れを把握できるようにする

サマリーを出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは講義録のサマリー生成を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Summary generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return processing_result.processed_text[:max_length]  # フォールバック
    
    def generate_glossary(
        self, 
        processing_result: ProcessingResult
    ) -> List[Dict[str, str]]:
        """
        用語集を生成する
        
        Args:
            processing_result: 処理結果
            
        Returns:
            List[Dict[str, str]]: 用語集
        """
        # 簡易実装：実際の実装では、より詳細な処理を行う
        logger.warning("Glossary generation not implemented yet")
        return []
    
    def generate_questions(
        self, 
        processing_result: ProcessingResult,
        num_questions: int = 5
    ) -> List[str]:
        """
        確認問題を生成する
        
        Args:
            processing_result: 処理結果
            num_questions: 問題数
            
        Returns:
            List[str]: 確認問題
        """
        try:
            prompt = f"""
以下の講義録テキストから、{num_questions}個の確認問題を生成してください。

テキスト:
{processing_result.processed_text}

問題のポイント:
1. 講義の主要な内容を問う問題
2. 理解度を確認できる問題
3. 応用力を試す問題

問題を出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは講義録の確認問題生成を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("Questions generation completed")
            
            # 簡易実装：実際の実装では、問題を分割
            return [result]
            
        except Exception as e:
            logger.error(f"Questions generation failed: {e}")
            return []
    
    def _build_rag_prompt(self, text: str, config: RAGConfig) -> str:
        """RAG用のプロンプトを構築"""
        prompt = f"""
以下のテキストについて、専門的な知識を活用して品質を向上させてください。

テキスト:
{text}

改善のポイント:
1. 専門用語の正確性
2. 概念の統一性
3. 文脈の適切性
4. 全体的な品質

改善されたテキストを出力してください。
"""
        return prompt
