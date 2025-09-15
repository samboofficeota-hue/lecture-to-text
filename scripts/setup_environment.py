#!/usr/bin/env python3
"""
環境設定スクリプト

外部環境との接続を自動設定します。
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adapters.cloudflare.cloudflare_adapter import CloudFlareAdapter
from adapters.cloudflare.cloudflare_config import CloudFlareConfig
from adapters.gcs.gcs_adapter import GCSAdapter
from adapters.gcs.gcs_config import GCSConfig
from adapters.database.database_adapter import DatabaseAdapter
from adapters.database.database_config import DatabaseConfig
from adapters.pubsub.pubsub_adapter import PubSubAdapter
from adapters.pubsub.pubsub_config import PubSubConfig
from adapters.tasks.cloud_tasks_adapter import CloudTasksAdapter
from adapters.tasks.tasks_config import TasksConfig
from adapters.logging.cloud_logging_adapter import CloudLoggingAdapter
from adapters.logging.logging_config import LoggingConfig
from utils.logging import get_logger

logger = get_logger(__name__)


class EnvironmentSetup:
    """環境設定クラス"""
    
    def __init__(self):
        """初期化"""
        self.config = self._load_config()
        self.setup_results = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込み"""
        config_file = project_root / "config" / "environment.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を作成"""
        config = {
            "gcp": {
                "project_id": os.getenv("GCP_PROJECT_ID", ""),
                "region": "asia-northeast1"
            },
            "cloudflare": {
                "api_token": os.getenv("CLOUDFLARE_API_TOKEN", ""),
                "zone_id": os.getenv("CLOUDFLARE_ZONE_ID", ""),
                "domain": "allianceforum.org",
                "subdomain": "darwin"
            },
            "vercel": {
                "org_id": os.getenv("VERCEL_ORG_ID", ""),
                "project_id": os.getenv("VERCEL_PROJECT_ID", ""),
                "token": os.getenv("VERCEL_TOKEN", "")
            }
        }
        
        # 設定ファイルを保存
        config_file = project_root / "config" / "environment.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config
    
    def setup_gcs(self) -> bool:
        """GCSを設定"""
        try:
            logger.info("Setting up Google Cloud Storage...")
            
            config = GCSConfig(
                project_id=self.config["gcp"]["project_id"],
                bucket_name="darwin-lecture-data",
                region=self.config["gcp"]["region"]
            )
            
            adapter = GCSAdapter(config.to_dict())
            
            # バケットを作成
            if adapter.create_bucket():
                logger.info("GCS bucket created successfully")
                self.setup_results["gcs"] = True
                return True
            else:
                logger.error("Failed to create GCS bucket")
                self.setup_results["gcs"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup GCS: {e}")
            self.setup_results["gcs"] = False
            return False
    
    def setup_cloud_sql(self) -> bool:
        """Cloud SQLを設定"""
        try:
            logger.info("Setting up Cloud SQL...")
            
            config = DatabaseConfig(
                project_id=self.config["gcp"]["project_id"],
                instance_name="darwin-db",
                database_name="darwin",
                region=self.config["gcp"]["region"]
            )
            
            adapter = DatabaseAdapter(config.to_dict())
            
            # データベース接続をテスト
            if adapter.test_connection():
                logger.info("Cloud SQL connection successful")
                self.setup_results["cloud_sql"] = True
                return True
            else:
                logger.error("Failed to connect to Cloud SQL")
                self.setup_results["cloud_sql"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Cloud SQL: {e}")
            self.setup_results["cloud_sql"] = False
            return False
    
    def setup_pubsub(self) -> bool:
        """Pub/Subを設定"""
        try:
            logger.info("Setting up Pub/Sub...")
            
            config = PubSubConfig(
                project_id=self.config["gcp"]["project_id"],
                topic_name="darwin-topic",
                subscription_name="darwin-subscription"
            )
            
            adapter = PubSubAdapter(config.to_dict())
            
            # トピックとサブスクリプションを作成
            if adapter.create_topic() and adapter.create_subscription():
                logger.info("Pub/Sub setup successful")
                self.setup_results["pubsub"] = True
                return True
            else:
                logger.error("Failed to setup Pub/Sub")
                self.setup_results["pubsub"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Pub/Sub: {e}")
            self.setup_results["pubsub"] = False
            return False
    
    def setup_cloud_tasks(self) -> bool:
        """Cloud Tasksを設定"""
        try:
            logger.info("Setting up Cloud Tasks...")
            
            config = TasksConfig(
                project_id=self.config["gcp"]["project_id"],
                location=self.config["gcp"]["region"],
                queue_name="darwin-queue",
                base_url="https://darwin-api-xxxxx-uc.a.run.app"  # 実際のURLに置き換え
            )
            
            adapter = CloudTasksAdapter(config.to_dict())
            
            # キュー情報を取得（キューが存在するかチェック）
            queue_info = adapter.get_queue_info()
            if queue_info:
                logger.info("Cloud Tasks queue exists")
                self.setup_results["cloud_tasks"] = True
                return True
            else:
                logger.warning("Cloud Tasks queue not found - manual setup required")
                self.setup_results["cloud_tasks"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Cloud Tasks: {e}")
            self.setup_results["cloud_tasks"] = False
            return False
    
    def setup_cloud_logging(self) -> bool:
        """Cloud Loggingを設定"""
        try:
            logger.info("Setting up Cloud Logging...")
            
            config = LoggingConfig(
                project_id=self.config["gcp"]["project_id"],
                log_name="darwin-app",
                service_name="darwin",
                region=self.config["gcp"]["region"]
            )
            
            adapter = CloudLoggingAdapter(config.to_dict())
            
            # テストログを送信
            if adapter.info("Environment setup test log"):
                logger.info("Cloud Logging setup successful")
                self.setup_results["cloud_logging"] = True
                return True
            else:
                logger.error("Failed to setup Cloud Logging")
                self.setup_results["cloud_logging"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Cloud Logging: {e}")
            self.setup_results["cloud_logging"] = False
            return False
    
    def setup_cloudflare(self) -> bool:
        """CloudFlareを設定"""
        try:
            logger.info("Setting up CloudFlare...")
            
            config = CloudFlareConfig(
                api_token=self.config["cloudflare"]["api_token"],
                zone_id=self.config["cloudflare"]["zone_id"],
                domain=self.config["cloudflare"]["domain"],
                subdomain=self.config["cloudflare"]["subdomain"]
            )
            
            adapter = CloudFlareAdapter(config.to_dict())
            
            # ゾーン情報を取得
            zone_info = adapter.get_zone_info()
            if zone_info and zone_info.get('success'):
                logger.info("CloudFlare zone access successful")
                
                # Vercelサブドメインを設定
                vercel_cname = "cname.vercel-dns.com"
                if adapter.setup_vercel_subdomain(vercel_cname):
                    logger.info("CloudFlare DNS configured for Vercel")
                    self.setup_results["cloudflare"] = True
                    return True
                else:
                    logger.error("Failed to configure CloudFlare DNS")
                    self.setup_results["cloudflare"] = False
                    return False
            else:
                logger.error("Failed to access CloudFlare zone")
                self.setup_results["cloudflare"] = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup CloudFlare: {e}")
            self.setup_results["cloudflare"] = False
            return False
    
    def setup_vercel(self) -> bool:
        """Vercelを設定"""
        try:
            logger.info("Setting up Vercel...")
            
            # Vercel CLIがインストールされているかチェック
            try:
                subprocess.run(["vercel", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Vercel CLI not found. Please install it first.")
                self.setup_results["vercel"] = False
                return False
            
            # プロジェクトをリンク
            env_vars = {
                "VERCEL_ORG_ID": self.config["vercel"]["org_id"],
                "VERCEL_PROJECT_ID": self.config["vercel"]["project_id"]
            }
            
            for key, value in env_vars.items():
                if not value:
                    logger.error(f"Missing {key} environment variable")
                    self.setup_results["vercel"] = False
                    return False
            
            logger.info("Vercel configuration validated")
            self.setup_results["vercel"] = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Vercel: {e}")
            self.setup_results["vercel"] = False
            return False
    
    def run_setup(self) -> bool:
        """全体のセットアップを実行"""
        logger.info("Starting environment setup...")
        
        # 各サービスのセットアップを実行
        services = [
            ("GCS", self.setup_gcs),
            ("Cloud SQL", self.setup_cloud_sql),
            ("Pub/Sub", self.setup_pubsub),
            ("Cloud Tasks", self.setup_cloud_tasks),
            ("Cloud Logging", self.setup_cloud_logging),
            ("CloudFlare", self.setup_cloudflare),
            ("Vercel", self.setup_vercel)
        ]
        
        success_count = 0
        total_count = len(services)
        
        for service_name, setup_func in services:
            logger.info(f"Setting up {service_name}...")
            if setup_func():
                success_count += 1
                logger.info(f"✅ {service_name} setup completed")
            else:
                logger.error(f"❌ {service_name} setup failed")
        
        # 結果を表示
        logger.info(f"\nSetup Results: {success_count}/{total_count} services configured successfully")
        
        for service_name, result in self.setup_results.items():
            status = "✅" if result else "❌"
            logger.info(f"{status} {service_name}: {'Success' if result else 'Failed'}")
        
        # 設定ファイルを更新
        self._save_setup_results()
        
        return success_count == total_count
    
    def _save_setup_results(self):
        """セットアップ結果を保存"""
        results_file = project_root / "config" / "setup_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.setup_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Setup results saved to {results_file}")


def main():
    """メイン関数"""
    setup = EnvironmentSetup()
    success = setup.run_setup()
    
    if success:
        logger.info("🎉 All services configured successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some services failed to configure")
        sys.exit(1)


if __name__ == "__main__":
    main()
