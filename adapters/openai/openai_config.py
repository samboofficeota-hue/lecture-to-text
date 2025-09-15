"""
OpenAI設定

OpenAI APIの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class OpenAIConfig:
    """OpenAI設定"""
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000
    timeout: int = 30
    base_url: Optional[str] = None
    organization: Optional[str] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if not self.api_key:
            import os
            self.api_key = os.getenv("OPENAI_API_KEY", "")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'api_key': self.api_key,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'base_url': self.base_url,
            'organization': self.organization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenAIConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def get_available_models(self) -> List[str]:
        """利用可能なモデル一覧を取得"""
        return [
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
            "gpt-4o", "gpt-4o-mini"
        ]
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # APIキーの検証
        if not self.api_key:
            return False
        
        # モデルの検証
        if self.model not in self.get_available_models():
            return False
        
        # 数値パラメータの検証
        if not (0.0 <= self.temperature <= 2.0):
            return False
        
        if not (1 <= self.max_tokens <= 32000):
            return False
        
        if not (1 <= self.timeout <= 300):
            return False
        
        return True
