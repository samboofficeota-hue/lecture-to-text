#!/usr/bin/env python3
"""
CloudFlare簡易テストスクリプト

sambo-office.comドメインのCloudFlare接続をテストします。
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

def test_cloudflare_connection():
    """CloudFlare接続テスト"""
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    domain = 'sambo-office.com'
    
    if not api_token:
        logger.error("CLOUDFLARE_API_TOKEN is not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Zone IDを取得
    url = f'https://api.cloudflare.com/client/v4/zones?name={domain}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['result']:
            zone_id = data['result'][0]['id']
            logger.info(f"✅ Zone ID found: {zone_id}")
            logger.info(f"✅ Domain: {domain}")
            logger.info(f"✅ Status: {data['result'][0]['status']}")
            return True
        else:
            logger.error(f"❌ Zone not found for domain: {domain}")
            return False
    else:
        logger.error(f"❌ Failed to get zone ID: {response.status_code} - {response.text}")
        return False

def main():
    logger.info("Testing CloudFlare connection...")
    success = test_cloudflare_connection()
    
    if success:
        logger.info("🎉 CloudFlare connection successful!")
        logger.info("Next steps:")
        logger.info("1. Set CLOUDFLARE_ZONE_ID in .env file")
        logger.info("2. Run setup_cloudflare.py to configure DNS and SSL")
    else:
        logger.error("❌ CloudFlare connection failed!")
        logger.error("Please check your API token and domain settings")

if __name__ == "__main__":
    main()
