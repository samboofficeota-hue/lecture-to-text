#!/usr/bin/env python3
"""
CloudFlare DNS設定修正スクリプト

Cloud RunのURLを使用するようにDNS設定を修正します。
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

class CloudFlareDNSManager:
    def __init__(self):
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.domain = 'sambo-office.com'
        self.subdomain = 'darwin'
        self.full_subdomain = f'{self.subdomain}.{self.domain}'
        self.cloud_run_url = 'lecture-to-text-api-1088729528504.asia-northeast1.run.app'
        
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
                return data['result']
            else:
                logger.error(f"Failed to get DNS records: {data['errors']}")
                return None
        else:
            logger.error(f"Failed to get DNS records: {response.status_code} - {response.text}")
            return None
    
    def delete_dns_record(self, record_id):
        """DNSレコードを削除"""
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}'
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                logger.info(f"✅ DNS record deleted: {record_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete DNS record: {result['errors']}")
                return False
        else:
            logger.error(f"❌ Failed to delete DNS record: {response.status_code} - {response.text}")
            return False
    
    def create_cname_record(self, name, content):
        """CNAMEレコードを作成"""
        url = f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records'
        data = {
            'name': name,
            'content': content,
            'type': 'CNAME',
            'ttl': 1
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                logger.info(f"✅ CNAME record created: {name} -> {content}")
                return True
            else:
                logger.error(f"❌ Failed to create CNAME record: {result['errors']}")
                return False
        else:
            logger.error(f"❌ Failed to create CNAME record: {response.status_code} - {response.text}")
            return False
    
    def fix_dns_settings(self):
        """DNS設定を修正"""
        logger.info(f"Fixing DNS settings for domain: {self.domain}")
        
        # 1. 現在のDNSレコードを取得
        existing_records = self.get_dns_records()
        if not existing_records:
            logger.error("Failed to get existing DNS records")
            return False
        
        # 2. 既存のAレコードを削除
        for record in existing_records:
            if record['name'] == self.full_subdomain and record['type'] == 'A':
                logger.info(f"Deleting A record: {record['name']} -> {record['content']}")
                self.delete_dns_record(record['id'])
        
        # 3. CNAMEレコードを作成
        self.create_cname_record(self.full_subdomain, self.cloud_run_url)
        
        # 4. wwwサブドメインのCNAMEレコードも更新
        self.create_cname_record(f'www.{self.full_subdomain}', self.full_subdomain)
        
        logger.info("🎉 DNS settings fixed!")
        return True

def main():
    try:
        manager = CloudFlareDNSManager()
        manager.fix_dns_settings()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
