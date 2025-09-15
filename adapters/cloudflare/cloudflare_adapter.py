"""
CloudFlareアダプター

CloudFlareとの連携を実装します。
"""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from utils.logging import get_logger

logger = get_logger(__name__)


class CloudFlareAdapter:
    """CloudFlareアダプター"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        CloudFlareアダプターを初期化
        
        Args:
            config: CloudFlare設定
        """
        self.config = config or {}
        self.api_token = self.config.get('api_token', '')
        self.zone_id = self.config.get('zone_id', '')
        self.domain = self.config.get('domain', '')
        self.subdomain = self.config.get('subdomain', '')
        self.full_domain = self.config.get('full_domain', '')
        
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        CloudFlare APIにリクエストを送信
        
        Args:
            method: HTTPメソッド
            endpoint: エンドポイント
            data: リクエストデータ
            
        Returns:
            Optional[Dict[str, Any]]: レスポンスデータ
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CloudFlare API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in CloudFlare API request: {e}")
            return None
    
    def get_zone_info(self) -> Optional[Dict[str, Any]]:
        """
        ゾーン情報を取得
        
        Returns:
            Optional[Dict[str, Any]]: ゾーン情報
        """
        endpoint = f"/zones/{self.zone_id}"
        return self._make_request('GET', endpoint)
    
    def get_dns_records(self) -> Optional[List[Dict[str, Any]]]:
        """
        DNSレコード一覧を取得
        
        Returns:
            Optional[List[Dict[str, Any]]]: DNSレコード一覧
        """
        endpoint = f"/zones/{self.zone_id}/dns_records"
        response = self._make_request('GET', endpoint)
        
        if response and 'result' in response:
            return response['result']
        return None
    
    def create_dns_record(
        self, 
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        DNSレコードを作成
        
        Args:
            record_type: レコードタイプ（A, CNAME, TXT等）
            name: レコード名
            content: レコード内容
            ttl: TTL値
            proxied: CloudFlareプロキシを使用するか
            
        Returns:
            Optional[Dict[str, Any]]: 作成されたレコード情報
        """
        endpoint = f"/zones/{self.zone_id}/dns_records"
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied
        }
        
        return self._make_request('POST', endpoint, data)
    
    def update_dns_record(
        self, 
        record_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        DNSレコードを更新
        
        Args:
            record_id: レコードID
            record_type: レコードタイプ
            name: レコード名
            content: レコード内容
            ttl: TTL値
            proxied: CloudFlareプロキシを使用するか
            
        Returns:
            Optional[Dict[str, Any]]: 更新されたレコード情報
        """
        endpoint = f"/zones/{self.zone_id}/dns_records/{record_id}"
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied
        }
        
        return self._make_request('PUT', endpoint, data)
    
    def delete_dns_record(self, record_id: str) -> bool:
        """
        DNSレコードを削除
        
        Args:
            record_id: レコードID
            
        Returns:
            bool: 削除の成功/失敗
        """
        endpoint = f"/zones/{self.zone_id}/dns_records/{record_id}"
        response = self._make_request('DELETE', endpoint)
        
        return response is not None and response.get('success', False)
    
    def setup_vercel_subdomain(self, vercel_cname: str) -> bool:
        """
        Vercelサブドメインを設定
        
        Args:
            vercel_cname: VercelのCNAME値
            
        Returns:
            bool: 設定の成功/失敗
        """
        try:
            # 既存のCNAMEレコードを検索
            records = self.get_dns_records()
            if not records:
                return False
            
            # 既存のレコードを更新または新規作成
            existing_record = None
            for record in records:
                if (record.get('type') == 'CNAME' and 
                    record.get('name') == self.full_domain):
                    existing_record = record
                    break
            
            if existing_record:
                # 既存レコードを更新
                result = self.update_dns_record(
                    record_id=existing_record['id'],
                    record_type='CNAME',
                    name=self.full_domain,
                    content=vercel_cname,
                    ttl=1,
                    proxied=True
                )
            else:
                # 新規レコードを作成
                result = self.create_dns_record(
                    record_type='CNAME',
                    name=self.full_domain,
                    content=vercel_cname,
                    ttl=1,
                    proxied=True
                )
            
            if result and result.get('success'):
                logger.info(f"DNS record configured: {self.full_domain} -> {vercel_cname}")
                return True
            else:
                logger.error(f"Failed to configure DNS record: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Vercel subdomain: {e}")
            return False
    
    def purge_cache(self, files: Optional[List[str]] = None) -> bool:
        """
        キャッシュをパージ
        
        Args:
            files: パージするファイルのリスト（Noneの場合は全キャッシュ）
            
        Returns:
            bool: パージの成功/失敗
        """
        try:
            endpoint = f"/zones/{self.zone_id}/purge_cache"
            data = {}
            
            if files:
                data['files'] = files
            else:
                data['purge_everything'] = True
            
            response = self._make_request('POST', endpoint, data)
            
            if response and response.get('success'):
                logger.info("Cache purged successfully")
                return True
            else:
                logger.error(f"Failed to purge cache: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to purge cache: {e}")
            return False
    
    def get_security_settings(self) -> Optional[Dict[str, Any]]:
        """
        セキュリティ設定を取得
        
        Returns:
            Optional[Dict[str, Any]]: セキュリティ設定
        """
        endpoint = f"/zones/{self.zone_id}/settings"
        response = self._make_request('GET', endpoint)
        
        if response and 'result' in response:
            return response['result']
        return None
    
    def update_security_settings(
        self, 
        ssl_mode: str = "full",
        cache_level: str = "aggressive",
        development_mode: bool = False
    ) -> bool:
        """
        セキュリティ設定を更新
        
        Args:
            ssl_mode: SSLモード
            cache_level: キャッシュレベル
            development_mode: 開発モード
            
        Returns:
            bool: 更新の成功/失敗
        """
        try:
            # SSL設定を更新
            ssl_endpoint = f"/zones/{self.zone_id}/settings/ssl"
            ssl_data = {'value': ssl_mode}
            ssl_response = self._make_request('PATCH', ssl_endpoint, ssl_data)
            
            # キャッシュ設定を更新
            cache_endpoint = f"/zones/{self.zone_id}/settings/cache_level"
            cache_data = {'value': cache_level}
            cache_response = self._make_request('PATCH', cache_endpoint, cache_data)
            
            # 開発モード設定を更新
            dev_endpoint = f"/zones/{self.zone_id}/settings/development_mode"
            dev_data = {'value': development_mode}
            dev_response = self._make_request('PATCH', dev_endpoint, dev_data)
            
            success = (ssl_response and ssl_response.get('success') and
                      cache_response and cache_response.get('success') and
                      dev_response and dev_response.get('success'))
            
            if success:
                logger.info("Security settings updated successfully")
            else:
                logger.error("Failed to update security settings")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update security settings: {e}")
            return False
    
    def get_analytics(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        アナリティクスデータを取得
        
        Args:
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
            
        Returns:
            Optional[Dict[str, Any]]: アナリティクスデータ
        """
        try:
            endpoint = f"/zones/{self.zone_id}/analytics/dashboard"
            params = {
                'since': start_date,
                'until': end_date
            }
            
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return None
    
    def get_firewall_rules(self) -> Optional[List[Dict[str, Any]]]:
        """
        ファイアウォールルールを取得
        
        Returns:
            Optional[List[Dict[str, Any]]]: ファイアウォールルール一覧
        """
        endpoint = f"/zones/{self.zone_id}/firewall/rules"
        response = self._make_request('GET', endpoint)
        
        if response and 'result' in response:
            return response['result']
        return None
    
    def create_firewall_rule(
        self, 
        expression: str,
        action: str,
        description: str
    ) -> Optional[Dict[str, Any]]:
        """
        ファイアウォールルールを作成
        
        Args:
            expression: ルール式
            action: アクション（block, challenge, allow等）
            description: 説明
            
        Returns:
            Optional[Dict[str, Any]]: 作成されたルール情報
        """
        endpoint = f"/zones/{self.zone_id}/firewall/rules"
        data = {
            'filter': {
                'expression': expression
            },
            'action': action,
            'description': description
        }
        
        return self._make_request('POST', endpoint, data)
