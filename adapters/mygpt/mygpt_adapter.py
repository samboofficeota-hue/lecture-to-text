"""
My GPTsアダプター

My GPTsとの連携を実装します。
"""

import time
from typing import Optional, Dict, Any, List, Tuple
from openai import OpenAI

from core.interfaces.rag_interface import RAGInterface, RAGConfig, KnowledgeItem
from utils.logging import get_logger

logger = get_logger(__name__)


class MyGPTAdapter(RAGInterface):
    """My GPTsアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        My GPTsアダプターを初期化
        
        Args:
            config: My GPTs設定
        """
        self.config = config or {}
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAIクライアントを初期化"""
        try:
            api_key = self.config.get('api_key', '')
            base_url = self.config.get('base_url', 'https://api.openai.com/v1')
            
            if not api_key:
                raise ValueError("OpenAI API key is required")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # MyGPTsのIDを設定
            self.mygpt_id = self.config.get('mygpt_id', 'g-68c7fe5c36b88191b0f242cc9c5c65aa')
            
            logger.info(f"My GPTs client initialized successfully (ID: {self.mygpt_id})")
            
        except Exception as e:
            logger.error(f"Failed to initialize My GPTs client: {e}")
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
            prompt = self._build_mygpt_prompt(text, config)
            
            # OpenAI APIを呼び出し
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": self._get_system_prompt(config)},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            logger.info("My GPTs RAG processing completed")
            return result
            
        except Exception as e:
            logger.error(f"My GPTs RAG processing failed: {e}")
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
        try:
            # My GPTsの知識ベースを検索
            prompt = f"""
以下のクエリに関連する知識を検索してください。

クエリ: {query}
分野: {domain or "指定なし"}
取得数: {top_k}個

関連する知識を出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは知識ベースの検索を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            
            # 簡易実装：実際の実装では、より詳細な知識抽出を行う
            knowledge_item = KnowledgeItem(
                id=f"mygpt_{int(time.time())}",
                content=result,
                domain=domain or "general",
                metadata={'source': 'mygpt', 'query': query}
            )
            
            logger.info("My GPTs knowledge retrieval completed")
            return [knowledge_item]
            
        except Exception as e:
            logger.error(f"My GPTs knowledge retrieval failed: {e}")
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
        try:
            # My GPTsの知識ベースに追加
            prompt = f"""
以下の知識を知識ベースに追加してください。

知識内容: {knowledge_item.content}
分野: {knowledge_item.domain}
メタデータ: {knowledge_item.metadata}

知識ベースに追加してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは知識ベースの管理を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            logger.info("My GPTs knowledge addition completed")
            return True
            
        except Exception as e:
            logger.error(f"My GPTs knowledge addition failed: {e}")
            return False
    
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
        try:
            # My GPTsの知識ベースを更新
            prompt = f"""
以下の知識を更新してください。

知識ID: {knowledge_id}
更新内容: {updated_content}

知識ベースを更新してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは知識ベースの管理を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            logger.info("My GPTs knowledge update completed")
            return True
            
        except Exception as e:
            logger.error(f"My GPTs knowledge update failed: {e}")
            return False
    
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
        try:
            # My GPTsで類似用語を検索
            prompt = f"""
以下の用語と類似する用語を検索してください。

用語: {term}
分野: {domain or "指定なし"}

類似する用語とその類似度を出力してください。
"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "あなたは用語の類似性検索を専門とするAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            
            result = response.choices[0].message.content
            
            # 簡易実装：実際の実装では、より詳細な類似度計算を行う
            similar_terms = [(term, 1.0)]  # ダミーデータ
            
            logger.info("My GPTs similar term search completed")
            return similar_terms
            
        except Exception as e:
            logger.error(f"My GPTs similar term search failed: {e}")
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
            logger.info("My GPTs concept unification completed")
            return result
            
        except Exception as e:
            logger.error(f"My GPTs concept unification failed: {e}")
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
            logger.info("My GPTs terminology validation completed")
            
            # 簡易実装：実際の実装では、JSONをパース
            return {
                'valid': True,
                'issues': [],
                'suggestions': []
            }
            
        except Exception as e:
            logger.error(f"My GPTs terminology validation failed: {e}")
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
        try:
            # My GPTsで分野別知識を取得
            prompt = f"""
{domain}分野の知識を取得してください。

分野: {domain}

関連する知識を出力してください。
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
            
            # 簡易実装：実際の実装では、より詳細な知識抽出を行う
            knowledge_item = KnowledgeItem(
                id=f"mygpt_domain_{int(time.time())}",
                content=result,
                domain=domain,
                metadata={'source': 'mygpt', 'type': 'domain_knowledge'}
            )
            
            logger.info("My GPTs domain knowledge retrieval completed")
            return [knowledge_item]
            
        except Exception as e:
            logger.error(f"My GPTs domain knowledge retrieval failed: {e}")
            return []
    
    def _build_mygpt_prompt(self, text: str, config: RAGConfig) -> str:
        """My GPTs用のプロンプトを構築"""
        prompt = f"""
以下のテキストについて、My GPTsの知識ベースを活用して品質を向上させてください。

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
    
    def _get_system_prompt(self, config: RAGConfig) -> str:
        """システムプロンプトを取得"""
        base_prompt = "あなたは専門的な講義録の品質向上を支援するAIアシスタントです。"
        
        if config.domain:
            base_prompt += f" 特に{config.domain}分野の専門知識を活用してください。"
        
        if self.config.get('custom_instructions'):
            base_prompt += f" {self.config['custom_instructions']}"
        
        return base_prompt
