#!/usr/bin/env python3
"""
強制DNS設定修正スクリプト

既存のAレコードを強制削除してCNAMEレコードを作成します。
"""

import os
import requests
import json
from dotenv import load_dotenv

def load_environment():
    """環境変数を読み込み"""
    load_dotenv()
    return {
        'api_token': os.getenv('CLOUDFLARE_API_TOKEN'),
        'zone_id': '25372a96627ee63e566afe0d064f965b',  # 直接指定
        'domain': 'sambo-office.com',
        'subdomain': 'darwin'
    }

def get_dns_records(api_token, zone_id):
    """既存のDNSレコードを取得"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['result']
    return []

def delete_dns_record(api_token, zone_id, record_id):
    """DNSレコードを削除"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(url, headers=headers)
    return response.status_code == 200

def create_cname_record(api_token, zone_id, name, target):
    """CNAMEレコードを作成"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "CNAME",
        "name": name,
        "content": target,
        "proxied": True,
        "ttl": 1  # Auto TTL
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200, response.json()

def main():
    """メイン処理"""
    print("=== CloudFlare DNS設定強制修正 ===")
    
    # 環境変数を読み込み
    env = load_environment()
    
    if not env['api_token']:
        print("❌ CLOUDFLARE_API_TOKEN が設定されていません")
        return
    
    # 既存のDNSレコードを取得
    records = get_dns_records(env['api_token'], env['zone_id'])
    print(f"既存のDNSレコード数: {len(records)}")
    
    # darwinサブドメインのすべてのレコードを削除
    darwin_records = [r for r in records if r['name'] == 'darwin.sambo-office.com']
    
    print(f"削除対象のレコード数: {len(darwin_records)}")
    
    for record in darwin_records:
        print(f"削除中: {record['name']} ({record['type']}) -> {record['content']}")
        if delete_dns_record(env['api_token'], env['zone_id'], record['id']):
            print("✅ 削除成功")
        else:
            print("❌ 削除失敗")
    
    # 少し待ってからCNAMEレコードを作成
    import time
    print("3秒待機中...")
    time.sleep(3)
    
    # CNAMEレコードを作成
    cloud_run_url = "darwin-lecture-api-1088729528504.asia-northeast1.run.app"
    success, result = create_cname_record(
        env['api_token'], 
        env['zone_id'], 
        "darwin", 
        cloud_run_url
    )
    
    if success:
        print(f"✅ CNAMEレコード作成成功: darwin -> {cloud_run_url}")
    else:
        print(f"❌ CNAMEレコード作成失敗: {result}")
    
    print("\n=== 設定完了 ===")
    print("DNS設定の反映には5-10分かかる場合があります。")
    print("確認コマンド:")
    print("  nslookup darwin.sambo-office.com")
    print("  curl -s https://darwin.sambo-office.com")

if __name__ == "__main__":
    main()
