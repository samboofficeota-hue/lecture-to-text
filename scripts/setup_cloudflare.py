#!/usr/bin/env python3
"""
CloudFlare設定スクリプト

CloudFlareのDNS設定とセキュリティ設定を行います。
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adapters.cloudflare.cloudflare_adapter import CloudFlareAdapter
from adapters.cloudflare.cloudflare_config import CloudFlareConfig
from utils.logging import get_logger

logger = get_logger(__name__)


class CloudFlareSetup:
    """CloudFlare設定クラス"""
    
    def __init__(self):
        """初期化"""
        self.config = self._load_config()
        self.adapter = None
        self._initialize_adapter()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込み"""
        config_file = project_root / "config" / "environment.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error("Environment configuration not found. Please run setup_environment.py first.")
            sys.exit(1)
    
    def _initialize_adapter(self):
        """アダプターを初期化"""
        try:
            cf_config = CloudFlareConfig(
                api_token=self.config["cloudflare"]["api_token"],
                zone_id=self.config["cloudflare"]["zone_id"],
                domain=self.config["cloudflare"]["domain"],
                subdomain=self.config["cloudflare"]["subdomain"]
            )
            
            self.adapter = CloudFlareAdapter(cf_config.to_dict())
            logger.info("CloudFlare adapter initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize CloudFlare adapter: {e}")
            sys.exit(1)
    
    def setup_dns_records(self) -> bool:
        """DNSレコードを設定"""
        try:
            logger.info("Setting up DNS records...")
            
            # 既存のレコードを取得
            existing_records = self.adapter.get_dns_records()
            if not existing_records:
                logger.error("Failed to get existing DNS records")
                return False
            
            # 必要なレコードを定義
            required_records = [
                {
                    "type": "CNAME",
                    "name": f"{self.config['cloudflare']['subdomain']}.{self.config['cloudflare']['domain']}",
                    "content": "cname.vercel-dns.com",
                    "proxied": True
                },
                {
                    "type": "TXT",
                    "name": f"_vercel.{self.config['cloudflare']['subdomain']}.{self.config['cloudflare']['domain']}",
                    "content": "vc-domain-verify=your-verification-code",  # 実際のコードに置き換え
                    "proxied": False
                }
            ]
            
            success_count = 0
            
            for record in required_records:
                # 既存のレコードをチェック
                existing = None
                for existing_record in existing_records:
                    if (existing_record.get('type') == record['type'] and 
                        existing_record.get('name') == record['name']):
                        existing = existing_record
                        break
                
                if existing:
                    # 既存レコードを更新
                    result = self.adapter.update_dns_record(
                        record_id=existing['id'],
                        record_type=record['type'],
                        name=record['name'],
                        content=record['content'],
                        ttl=1,
                        proxied=record['proxied']
                    )
                else:
                    # 新規レコードを作成
                    result = self.adapter.create_dns_record(
                        record_type=record['type'],
                        name=record['name'],
                        content=record['content'],
                        ttl=1,
                        proxied=record['proxied']
                    )
                
                if result and result.get('success'):
                    logger.info(f"✅ DNS record configured: {record['name']}")
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to configure DNS record: {record['name']}")
            
            return success_count == len(required_records)
            
        except Exception as e:
            logger.error(f"Failed to setup DNS records: {e}")
            return False
    
    def setup_security_settings(self) -> bool:
        """セキュリティ設定を設定"""
        try:
            logger.info("Setting up security settings...")
            
            # セキュリティ設定を更新
            success = self.adapter.update_security_settings(
                ssl_mode="full",
                cache_level="aggressive",
                development_mode=False
            )
            
            if success:
                logger.info("✅ Security settings configured")
                return True
            else:
                logger.error("❌ Failed to configure security settings")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup security settings: {e}")
            return False
    
    def setup_firewall_rules(self) -> bool:
        """ファイアウォールルールを設定"""
        try:
            logger.info("Setting up firewall rules...")
            
            # 基本的なファイアウォールルールを定義
            firewall_rules = [
                {
                    "expression": "(http.request.uri.path contains \"/api/\" and http.request.method eq \"POST\" and not cf.connecting_ip in {\"127.0.0.1\"})",
                    "action": "challenge",
                    "description": "API endpoint protection"
                },
                {
                    "expression": "(http.request.uri.path contains \"/admin/\" and not cf.connecting_ip in {\"127.0.0.1\"})",
                    "action": "block",
                    "description": "Admin endpoint protection"
                },
                {
                    "expression": "(http.user_agent contains \"bot\" and not http.user_agent contains \"Googlebot\")",
                    "action": "challenge",
                    "description": "Bot protection"
                }
            ]
            
            success_count = 0
            
            for rule in firewall_rules:
                result = self.adapter.create_firewall_rule(
                    expression=rule['expression'],
                    action=rule['action'],
                    description=rule['description']
                )
                
                if result and result.get('success'):
                    logger.info(f"✅ Firewall rule created: {rule['description']}")
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to create firewall rule: {rule['description']}")
            
            return success_count == len(firewall_rules)
            
        except Exception as e:
            logger.error(f"Failed to setup firewall rules: {e}")
            return False
    
    def setup_page_rules(self) -> bool:
        """ページルールを設定"""
        try:
            logger.info("Setting up page rules...")
            
            # ページルールを定義
            page_rules = [
                {
                    "url": f"https://{self.config['cloudflare']['subdomain']}.{self.config['cloudflare']['domain']}/api/*",
                    "settings": {
                        "cache_level": "bypass",
                        "security_level": "high"
                    }
                },
                {
                    "url": f"https://{self.config['cloudflare']['subdomain']}.{self.config['cloudflare']['domain']}/static/*",
                    "settings": {
                        "cache_level": "aggressive",
                        "browser_cache_ttl": 31536000
                    }
                }
            ]
            
            # ページルールの設定は手動で行う必要があります
            logger.info("Page rules need to be configured manually in CloudFlare dashboard:")
            for rule in page_rules:
                logger.info(f"  - URL: {rule['url']}")
                logger.info(f"    Settings: {rule['settings']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup page rules: {e}")
            return False
    
    def run_setup(self) -> bool:
        """全体のセットアップを実行"""
        logger.info("Starting CloudFlare setup...")
        
        # 各設定を実行
        setup_tasks = [
            ("DNS Records", self.setup_dns_records),
            ("Security Settings", self.setup_security_settings),
            ("Firewall Rules", self.setup_firewall_rules),
            ("Page Rules", self.setup_page_rules)
        ]
        
        success_count = 0
        total_count = len(setup_tasks)
        
        for task_name, setup_func in setup_tasks:
            logger.info(f"Setting up {task_name}...")
            if setup_func():
                success_count += 1
                logger.info(f"✅ {task_name} setup completed")
            else:
                logger.error(f"❌ {task_name} setup failed")
        
        # 結果を表示
        logger.info(f"\nCloudFlare Setup Results: {success_count}/{total_count} tasks completed successfully")
        
        if success_count == total_count:
            logger.info("🎉 CloudFlare setup completed successfully!")
            return True
        else:
            logger.error("❌ Some CloudFlare setup tasks failed")
            return False


def main():
    """メイン関数"""
    setup = CloudFlareSetup()
    success = setup.run_setup()
    
    if success:
        logger.info("CloudFlare configuration completed successfully!")
        sys.exit(0)
    else:
        logger.error("CloudFlare configuration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
