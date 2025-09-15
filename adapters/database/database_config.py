"""
データベース設定

Cloud SQLの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DatabaseConfig:
    """データベース設定"""
    host: str = ""
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    ssl_mode: str = "require"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    def __post_init__(self):
        """初期化後の処理"""
        import os
        
        if not self.host:
            self.host = os.getenv("DATABASE_HOST", "")
        
        if not self.database:
            self.database = os.getenv("DATABASE_NAME", "")
        
        if not self.username:
            self.username = os.getenv("DATABASE_USER", "")
        
        if not self.password:
            self.password = os.getenv("DATABASE_PASSWORD", "")
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
            'ssl_mode': self.ssl_mode,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def get_connection_string(self) -> str:
        """接続文字列を取得"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # 必須項目の検証
        if not all([self.host, self.database, self.username, self.password]):
            return False
        
        # ポート番号の検証
        if not (1 <= self.port <= 65535):
            return False
        
        # SSLモードの検証
        valid_ssl_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if self.ssl_mode not in valid_ssl_modes:
            return False
        
        # プール設定の検証
        if self.pool_size < 1 or self.max_overflow < 0:
            return False
        
        return True
