"""
CloudFlare設定

CloudFlareの設定を管理します。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class CloudFlareConfig:
    """CloudFlare設定"""
    api_token: str = ""
    zone_id: str = ""
    domain: str = "allianceforum.org"
    subdomain: str = "darwin"
    full_domain: str = "darwin.allianceforum.org"
    ssl_mode: str = "full"
    cache_level: str = "aggressive"
    development_mode: bool = False
    minify_css: bool = True
    minify_js: bool = True
    minify_html: bool = True
    brotli_compression: bool = True
    rocket_loader: bool = True
    auto_minify: bool = True
    
    def __post_init__(self):
        """初期化後の処理"""
        import os
        
        if not self.api_token:
            self.api_token = os.getenv("CLOUDFLARE_API_TOKEN", "")
        
        if not self.zone_id:
            self.zone_id = os.getenv("CLOUDFLARE_ZONE_ID", "")
        
        if not self.domain:
            self.domain = os.getenv("CLOUDFLARE_DOMAIN", "allianceforum.org")
        
        if not self.subdomain:
            self.subdomain = os.getenv("CLOUDFLARE_SUBDOMAIN", "darwin")
        
        if not self.full_domain:
            self.full_domain = f"{self.subdomain}.{self.domain}"
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'api_token': self.api_token,
            'zone_id': self.zone_id,
            'domain': self.domain,
            'subdomain': self.subdomain,
            'full_domain': self.full_domain,
            'ssl_mode': self.ssl_mode,
            'cache_level': self.cache_level,
            'development_mode': self.development_mode,
            'minify_css': self.minify_css,
            'minify_js': self.minify_js,
            'minify_html': self.minify_html,
            'brotli_compression': self.brotli_compression,
            'rocket_loader': self.rocket_loader,
            'auto_minify': self.auto_minify
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CloudFlareConfig':
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    def validate(self) -> bool:
        """設定の妥当性を検証"""
        # APIトークンの検証
        if not self.api_token:
            return False
        
        # ゾーンIDの検証
        if not self.zone_id:
            return False
        
        # ドメインの検証
        if not self.domain or not self.subdomain:
            return False
        
        # SSLモードの検証
        valid_ssl_modes = ["off", "flexible", "full", "strict"]
        if self.ssl_mode not in valid_ssl_modes:
            return False
        
        # キャッシュレベルの検証
        valid_cache_levels = ["basic", "simplified", "aggressive"]
        if self.cache_level not in valid_cache_levels:
            return False
        
        return True
