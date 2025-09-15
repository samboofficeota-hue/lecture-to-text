"""
設定バリデーター

設定値の検証を行います。
"""

import os
from typing import Dict, Any, List, Optional


class ConfigValidator:
    """設定値の検証クラス"""
    
    def __init__(self):
        self.required_vars = [
            'OPENAI_API_KEY',
            'GCP_PROJECT_ID',
            'GCP_REGION'
        ]
        
        self.optional_vars = [
            'CLOUDFLARE_API_TOKEN',
            'CLOUDFLARE_ZONE_ID',
            'VERCEL_ORG_ID',
            'VERCEL_PROJECT_ID'
        ]
    
    def validate_required_vars(self) -> List[str]:
        """必須環境変数の検証"""
        missing_vars = []
        for var in self.required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        return missing_vars
    
    def validate_optional_vars(self) -> List[str]:
        """オプション環境変数の検証"""
        missing_vars = []
        for var in self.optional_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        return missing_vars
    
    def validate_all(self) -> Dict[str, Any]:
        """全設定値の検証"""
        required_missing = self.validate_required_vars()
        optional_missing = self.validate_optional_vars()
        
        return {
            'required_missing': required_missing,
            'optional_missing': optional_missing,
            'is_valid': len(required_missing) == 0
        }
    
    def validate_cloudflare_config(self) -> bool:
        """CloudFlare設定の検証"""
        api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        domain = os.getenv('CLOUDFLARE_DOMAIN')
        
        return bool(api_token and zone_id and domain)
    
    def validate_gcp_config(self) -> bool:
        """GCP設定の検証"""
        project_id = os.getenv('GCP_PROJECT_ID')
        region = os.getenv('GCP_REGION')
        
        return bool(project_id and region)
