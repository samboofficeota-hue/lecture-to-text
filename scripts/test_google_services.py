#!/usr/bin/env python3
"""
Google関連サービスの接続テスト

Cloud Run、GCS、Pub/Sub、Cloud Tasks、Cloud SQLの接続をテストします。
"""

import os
import sys
import json
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


def test_gcs():
    """GCS接続テスト"""
    try:
        from google.cloud import storage
        
        client = storage.Client(project='lecture-to-text-472009')
        bucket = client.bucket('darwin-lecture-data-472009')
        
        # バケットの存在確認
        if bucket.exists():
            logger.info("✅ GCS: バケットにアクセス成功")
            return True
        else:
            logger.error("❌ GCS: バケットが見つかりません")
            return False
            
    except Exception as e:
        logger.error(f"❌ GCS: エラー - {e}")
        return False


def test_pubsub():
    """Pub/Sub接続テスト"""
    try:
        from google.cloud import pubsub_v1
        
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path('lecture-to-text-472009', 'darwin-topic')
        
        # トピックの存在確認
        try:
            publisher.get_topic(topic=topic_path)
            logger.info("✅ Pub/Sub: トピックにアクセス成功")
            return True
        except Exception as e:
            logger.error(f"❌ Pub/Sub: トピックが見つかりません - {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pub/Sub: エラー - {e}")
        return False


def test_cloud_tasks():
    """Cloud Tasks接続テスト"""
    try:
        from google.cloud import tasks_v2
        
        client = tasks_v2.CloudTasksClient()
        queue_path = client.queue_path('lecture-to-text-472009', 'asia-northeast1', 'darwin-queue')
        
        # キューの存在確認
        try:
            client.get_queue(name=queue_path)
            logger.info("✅ Cloud Tasks: キューにアクセス成功")
            return True
        except Exception as e:
            logger.error(f"❌ Cloud Tasks: キューが見つかりません - {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cloud Tasks: エラー - {e}")
        return False


def test_cloud_sql():
    """Cloud SQL接続テスト"""
    try:
        from google.cloud.sql.connector import Connector
        import pg8000
        
        connector = Connector()
        
        # 接続情報
        instance_connection_name = "lecture-to-text-472009:asia-northeast1:darwin-db"
        db_user = "postgres"
        db_pass = "darwin123"
        db_name = "darwin"
        
        # 接続テスト
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        
        conn.close()
        logger.info("✅ Cloud SQL: データベース接続成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cloud SQL: エラー - {e}")
        return False


def test_cloud_run():
    """Cloud Run接続テスト"""
    try:
        import requests
        
        # 既存のCloud Runサービス
        url = "https://lecture-to-text-api-1088729528504.asia-northeast1.run.app/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Cloud Run: 既存サービス接続成功")
            return True
        else:
            logger.error(f"❌ Cloud Run: 既存サービス接続失敗 - {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cloud Run: エラー - {e}")
        return False


def main():
    """メイン関数"""
    logger.info("Google関連サービスの接続テストを開始...")
    
    tests = [
        ("Cloud Run", test_cloud_run),
        ("GCS", test_gcs),
        ("Pub/Sub", test_pubsub),
        ("Cloud Tasks", test_cloud_tasks),
        ("Cloud SQL", test_cloud_sql)
    ]
    
    results = {}
    success_count = 0
    
    for service_name, test_func in tests:
        logger.info(f"テスト中: {service_name}")
        success = test_func()
        results[service_name] = success
        if success:
            success_count += 1
    
    # 結果を表示
    logger.info("\n" + "="*50)
    logger.info("Google関連サービス接続テスト結果")
    logger.info("="*50)
    
    for service_name, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"{status} {service_name}")
    
    logger.info("="*50)
    logger.info(f"成功: {success_count}/{len(tests)} サービス")
    
    if success_count == len(tests):
        logger.info("🎉 すべてのGoogle関連サービスに接続成功！")
    else:
        logger.info("⚠️ 一部のサービスで接続に問題があります")
    
    return success_count == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
