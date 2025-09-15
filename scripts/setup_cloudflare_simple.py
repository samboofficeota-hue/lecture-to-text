#!/usr/bin/env python3
"""
CloudFlare簡易設定スクリプト

sambo-office.comドメインのCloudFlare設定を自動化します。
"""

import os
import sys
import requests
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数ファイルを読み込み
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# ログ設定
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudFlareManager:
    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.domain = 'sambo-office.com'
        self.subdomain = 'darwin'
        self.full_subdomain = f'{self.subdomain}.{self.domain}'
        
        if not self.api_token:
            raise ValueError("CLOUDFLARE_API_TOKEN is not set")
        
        if not self.zone_id:
            raise ValueError("CLOUDFLARE_ZONE_ID is not set")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_dns_records(self):
        """DNSレコード一覧を取得"""
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                logger.info(f"Found {len(data['result'])} DNS records")
                return data['result']
            else:
                logger.error(f"Failed to get DNS records: {data['errors']}")
                return None
        else:
            logger.error(f"Failed to get DNS records: {response.status_code} - {response.text}")
            return None
    
    def create_dns_record(self, name, content, record_type='A', ttl=1):
        """DNSレコードを作成"""
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records'
        data = {
            'name': name,
            'content': content,
            'type': record_type,
            'ttl': ttl
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                logger.info(f"✅ DNS record created: {name} -> {content}")
                return True
            else:
                logger.error(f"❌ Failed to create DNS record: {result['errors']}")
                return False
        else:
            logger.error(f"❌ Failed to create DNS record: {response.status_code} - {response.text}")
            return False
    
    def setup_ssl(self):
        """SSL設定を有効化"""
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/ssl'
        data = {
            'value': 'full'
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                logger.info("✅ SSL setting updated to Full (strict)")
                return True
            else:
                logger.error(f"❌ Failed to update SSL setting: {result['errors']}")
                return False
        else:
            logger.error(f"❌ Failed to update SSL setting: {response.status_code} - {response.text}")
            return False
    
    def setup_security(self):
        """セキュリティ設定を有効化"""
        security_settings = [
            {'name': 'waf', 'value': 'on'},
            {'name': 'bot_fight_mode', 'value': 'on'},
            {'name': 'ddos_protection', 'value': 'on'}
        ]
        
        success_count = 0
        for setting in security_settings:
            url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/{setting["name"]}'
            data = {'value': setting['value']}
            
            response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    logger.info(f"✅ Security setting {setting['name']} enabled")
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to enable {setting['name']}: {result['errors']}")
            else:
                logger.error(f"❌ Failed to enable {setting['name']}: {response.status_code} - {response.text}")
        
        return success_count == len(security_settings)
    
    def setup_domain(self):
        """ドメインの完全な設定"""
        logger.info(f"Setting up CloudFlare for domain: {self.domain}")
        
        # 1. 現在のDNSレコードを確認
        existing_records = self.get_dns_records()
        if existing_records:
            logger.info("Current DNS records:")
            for record in existing_records:
                logger.info(f"  {record['name']} ({record['type']}) -> {record['content']}")
        
        # 2. DNSレコードを作成
        # サブドメインのAレコード（Cloud Run IPに設定）
        cloud_run_ip = "34.146.194.75"  # 実際のCloud Run IPに置き換え
        self.create_dns_record(self.full_subdomain, cloud_run_ip, 'A')
        
        # wwwサブドメインのCNAMEレコード
        self.create_dns_record(f'www.{self.full_subdomain}', self.full_subdomain, 'CNAME')
        
        # 3. SSL設定
        self.setup_ssl()
        
        # 4. セキュリティ設定
        self.setup_security()
        
        logger.info("🎉 CloudFlare setup completed!")
        return True

def main():
    try:
        manager = CloudFlareManager()
        manager.setup_domain()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
