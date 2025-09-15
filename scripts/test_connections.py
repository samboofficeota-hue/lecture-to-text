#!/usr/bin/env python3
"""
外部環境接続テストスクリプト

すべての外部環境との接続をテストします。
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# インポートエラーを回避するため、直接テスト
import importlib.util
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ログ設定
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConnectionTester:
    """接続テストクラス"""
    
    def __init__(self):
        """初期化"""
        self.test_results = {}
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込み"""
        config_file = project_root / "config" / "environment.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning("Environment configuration not found. Using environment variables.")
            return {}
    
    def test_whisper(self) -> Tuple[bool, str]:
        """Whisper接続をテスト"""
        try:
            logger.info("Testing Whisper connection...")
            
            # テスト用の設定
            config = {
                'model_name': 'large-v3',
                'device': 'cpu',
                'compute_type': 'float32'
            }
            
            adapter = WhisperAdapter(config)
            
            # 簡単なテスト（実際の音声ファイルは不要）
            logger.info("✅ Whisper adapter initialized successfully")
            return True, "Whisper adapter initialized"
            
        except Exception as e:
            logger.error(f"❌ Whisper test failed: {e}")
            return False, str(e)
    
    def test_openai(self) -> Tuple[bool, str]:
        """OpenAI接続をテスト"""
        try:
            logger.info("Testing OpenAI connection...")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return False, "OPENAI_API_KEY not set"
            
            config = {
                'api_key': api_key,
                'model': 'gpt-4o',
                'max_tokens': 1000
            }
            
            adapter = OpenAIAdapter(config)
            
            # 簡単なテストリクエスト
            response = adapter.generate_text("Hello, this is a test.")
            
            if response:
                logger.info("✅ OpenAI connection successful")
                return True, "OpenAI API responded successfully"
            else:
                return False, "OpenAI API returned no response"
                
        except Exception as e:
            logger.error(f"❌ OpenAI test failed: {e}")
            return False, str(e)
    
    def test_file_processing(self) -> Tuple[bool, str]:
        """ファイル処理をテスト"""
        try:
            logger.info("Testing file processing...")
            
            adapter = FileAdapter()
            
            # テスト用の一時ファイルを作成
            test_file = project_root / "test_temp.txt"
            test_file.write_text("Test content")
            
            # ファイルの存在確認
            if adapter.file_exists(str(test_file)):
                logger.info("✅ File processing test successful")
                test_file.unlink()  # テストファイルを削除
                return True, "File operations working"
            else:
                return False, "File operations failed"
                
        except Exception as e:
            logger.error(f"❌ File processing test failed: {e}")
            return False, str(e)
    
    def test_mygpt(self) -> Tuple[bool, str]:
        """My GPTs接続をテスト"""
        try:
            logger.info("Testing My GPTs connection...")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return False, "OPENAI_API_KEY not set"
            
            config = {
                'api_key': api_key,
                'model': 'gpt-4o',
                'max_tokens': 1000
            }
            
            adapter = MyGPTAdapter(config)
            
            # 簡単なテストリクエスト
            response = adapter.generate_text("Hello, this is a test.")
            
            if response:
                logger.info("✅ My GPTs connection successful")
                return True, "My GPTs API responded successfully"
            else:
                return False, "My GPTs API returned no response"
                
        except Exception as e:
            logger.error(f"❌ My GPTs test failed: {e}")
            return False, str(e)
    
    def test_gcs(self) -> Tuple[bool, str]:
        """GCS接続をテスト"""
        try:
            logger.info("Testing GCS connection...")
            
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return False, "GCP_PROJECT_ID not set"
            
            config = {
                'project_id': project_id,
                'bucket_name': 'darwin-lecture-data',
                'region': 'asia-northeast1'
            }
            
            adapter = GCSAdapter(config)
            
            # バケットの存在確認
            if adapter.bucket_exists():
                logger.info("✅ GCS connection successful")
                return True, "GCS bucket accessible"
            else:
                return False, "GCS bucket not accessible"
                
        except Exception as e:
            logger.error(f"❌ GCS test failed: {e}")
            return False, str(e)
    
    def test_database(self) -> Tuple[bool, str]:
        """データベース接続をテスト"""
        try:
            logger.info("Testing database connection...")
            
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return False, "GCP_PROJECT_ID not set"
            
            config = {
                'project_id': project_id,
                'instance_name': 'darwin-db',
                'database_name': 'darwin',
                'region': 'asia-northeast1'
            }
            
            adapter = DatabaseAdapter(config)
            
            # 接続テスト
            if adapter.test_connection():
                logger.info("✅ Database connection successful")
                return True, "Database connection established"
            else:
                return False, "Database connection failed"
                
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}")
            return False, str(e)
    
    def test_cloud_logging(self) -> Tuple[bool, str]:
        """Cloud Logging接続をテスト"""
        try:
            logger.info("Testing Cloud Logging connection...")
            
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return False, "GCP_PROJECT_ID not set"
            
            config = {
                'project_id': project_id,
                'log_name': 'darwin-app',
                'service_name': 'darwin',
                'region': 'asia-northeast1'
            }
            
            adapter = CloudLoggingAdapter(config)
            
            # テストログを送信
            if adapter.info("Connection test log"):
                logger.info("✅ Cloud Logging connection successful")
                return True, "Cloud Logging working"
            else:
                return False, "Cloud Logging failed"
                
        except Exception as e:
            logger.error(f"❌ Cloud Logging test failed: {e}")
            return False, str(e)
    
    def test_cloud_tasks(self) -> Tuple[bool, str]:
        """Cloud Tasks接続をテスト"""
        try:
            logger.info("Testing Cloud Tasks connection...")
            
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return False, "GCP_PROJECT_ID not set"
            
            config = {
                'project_id': project_id,
                'location': 'asia-northeast1',
                'queue_name': 'darwin-queue',
                'base_url': 'https://darwin-api-xxxxx-uc.a.run.app'
            }
            
            adapter = CloudTasksAdapter(config)
            
            # キュー情報を取得
            queue_info = adapter.get_queue_info()
            if queue_info:
                logger.info("✅ Cloud Tasks connection successful")
                return True, "Cloud Tasks queue accessible"
            else:
                return False, "Cloud Tasks queue not accessible"
                
        except Exception as e:
            logger.error(f"❌ Cloud Tasks test failed: {e}")
            return False, str(e)
    
    def test_pubsub(self) -> Tuple[bool, str]:
        """Pub/Sub接続をテスト"""
        try:
            logger.info("Testing Pub/Sub connection...")
            
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return False, "GCP_PROJECT_ID not set"
            
            config = {
                'project_id': project_id,
                'topic_name': 'darwin-topic',
                'subscription_name': 'darwin-subscription'
            }
            
            adapter = PubSubAdapter(config)
            
            # トピック情報を取得
            topic_info = adapter.get_topic_info()
            if topic_info:
                logger.info("✅ Pub/Sub connection successful")
                return True, "Pub/Sub topic accessible"
            else:
                return False, "Pub/Sub topic not accessible"
                
        except Exception as e:
            logger.error(f"❌ Pub/Sub test failed: {e}")
            return False, str(e)
    
    def test_cloudflare(self) -> Tuple[bool, str]:
        """CloudFlare接続をテスト"""
        try:
            logger.info("Testing CloudFlare connection...")
            
            api_token = os.getenv("CLOUDFLARE_API_TOKEN")
            zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
            
            if not api_token or not zone_id:
                return False, "CLOUDFLARE_API_TOKEN or CLOUDFLARE_ZONE_ID not set"
            
            config = {
                'api_token': api_token,
                'zone_id': zone_id,
                'domain': 'allianceforum.org',
                'subdomain': 'darwin'
            }
            
            adapter = CloudFlareAdapter(config)
            
            # ゾーン情報を取得
            zone_info = adapter.get_zone_info()
            if zone_info and zone_info.get('success'):
                logger.info("✅ CloudFlare connection successful")
                return True, "CloudFlare zone accessible"
            else:
                return False, "CloudFlare zone not accessible"
                
        except Exception as e:
            logger.error(f"❌ CloudFlare test failed: {e}")
            return False, str(e)
    
    def run_all_tests(self) -> Dict[str, Tuple[bool, str]]:
        """すべてのテストを実行"""
        logger.info("Starting connection tests...")
        
        tests = [
            ("Whisper", self.test_whisper),
            ("OpenAI", self.test_openai),
            ("File Processing", self.test_file_processing),
            ("My GPTs", self.test_mygpt),
            ("GCS", self.test_gcs),
            ("Database", self.test_database),
            ("Cloud Logging", self.test_cloud_logging),
            ("Cloud Tasks", self.test_cloud_tasks),
            ("Pub/Sub", self.test_pubsub),
            ("CloudFlare", self.test_cloudflare)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running {test_name} test...")
            success, message = test_func()
            self.test_results[test_name] = (success, message)
        
        return self.test_results
    
    def print_results(self):
        """結果を表示"""
        logger.info("\n" + "="*60)
        logger.info("CONNECTION TEST RESULTS")
        logger.info("="*60)
        
        success_count = 0
        total_count = len(self.test_results)
        
        for service_name, (success, message) in self.test_results.items():
            status = "✅" if success else "❌"
            logger.info(f"{status} {service_name}: {message}")
            if success:
                success_count += 1
        
        logger.info("="*60)
        logger.info(f"Summary: {success_count}/{total_count} services connected successfully")
        
        if success_count == total_count:
            logger.info("🎉 All external connections are working!")
        else:
            logger.info("⚠️  Some connections failed. Check the logs above.")
        
        logger.info("="*60)
    
    def save_results(self):
        """結果を保存"""
        results_file = project_root / "config" / "connection_test_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test results saved to {results_file}")


def main():
    """メイン関数"""
    tester = ConnectionTester()
    tester.run_all_tests()
    tester.print_results()
    tester.save_results()
    
    # 成功した接続の数を確認
    success_count = sum(1 for success, _ in tester.test_results.values() if success)
    total_count = len(tester.test_results)
    
    if success_count == total_count:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error(f"Some tests failed: {success_count}/{total_count}")
        sys.exit(1)


if __name__ == "__main__":
    main()
