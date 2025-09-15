#!/usr/bin/env python3
"""
簡易版外部環境接続テストスクリプト

環境変数の設定と基本的な接続をテストします。
"""

import os
import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ログ設定
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleConnectionTester:
    """簡易接続テストクラス"""
    
    def __init__(self):
        """初期化"""
        self.test_results = {}
    
    def test_environment_variables(self) -> dict:
        """環境変数の設定をテスト"""
        logger.info("Testing environment variables...")
        
        required_vars = {
            "GCP_PROJECT_ID": "Google Cloud Project ID",
            "OPENAI_API_KEY": "OpenAI API Key",
            "CLOUDFLARE_API_TOKEN": "CloudFlare API Token",
            "CLOUDFLARE_ZONE_ID": "CloudFlare Zone ID",
            "VERCEL_ORG_ID": "Vercel Organization ID",
            "VERCEL_PROJECT_ID": "Vercel Project ID",
            "VERCEL_TOKEN": "Vercel Token"
        }
        
        results = {}
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if value:
                results[var_name] = {"status": "✅", "message": f"{description} is set"}
                logger.info(f"✅ {var_name}: {description} is set")
            else:
                results[var_name] = {"status": "❌", "message": f"{description} is not set"}
                logger.warning(f"❌ {var_name}: {description} is not set")
        
        return results
    
    def test_file_structure(self) -> dict:
        """ファイル構造をテスト"""
        logger.info("Testing file structure...")
        
        required_dirs = [
            "core",
            "adapters",
            "config",
            "utils",
            "learning",
            "scripts",
            "docs"
        ]
        
        results = {}
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                results[dir_name] = {"status": "✅", "message": f"Directory {dir_name} exists"}
                logger.info(f"✅ {dir_name}: Directory exists")
            else:
                results[dir_name] = {"status": "❌", "message": f"Directory {dir_name} not found"}
                logger.error(f"❌ {dir_name}: Directory not found")
        
        return results
    
    def test_config_files(self) -> dict:
        """設定ファイルをテスト"""
        logger.info("Testing configuration files...")
        
        required_files = [
            "config/environment.json",
            "config/settings.py",
            "env.example",
            "requirements.txt",
            "Dockerfile",
            ".github/workflows/deploy.yml"
        ]
        
        results = {}
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists() and file_path.is_file():
                results[file_name] = {"status": "✅", "message": f"File {file_name} exists"}
                logger.info(f"✅ {file_name}: File exists")
            else:
                results[file_name] = {"status": "❌", "message": f"File {file_name} not found"}
                logger.error(f"❌ {file_name}: File not found")
        
        return results
    
    def test_python_imports(self) -> dict:
        """Pythonインポートをテスト"""
        logger.info("Testing Python imports...")
        
        test_imports = [
            ("os", "Standard library"),
            ("json", "Standard library"),
            ("pathlib", "Standard library"),
            ("logging", "Standard library"),
            ("requests", "Third-party library"),
            ("google.cloud", "Google Cloud library"),
            ("openai", "OpenAI library"),
            ("faster_whisper", "Whisper library")
        ]
        
        results = {}
        for module_name, description in test_imports:
            try:
                __import__(module_name)
                results[module_name] = {"status": "✅", "message": f"{description} imported successfully"}
                logger.info(f"✅ {module_name}: {description} imported successfully")
            except ImportError as e:
                results[module_name] = {"status": "❌", "message": f"{description} import failed: {e}"}
                logger.error(f"❌ {module_name}: {description} import failed: {e}")
        
        return results
    
    def test_scripts_executability(self) -> dict:
        """スクリプトの実行可能性をテスト"""
        logger.info("Testing script executability...")
        
        scripts = [
            "scripts/setup_environment.py",
            "scripts/setup_cloudflare.py",
            "scripts/test_connections.py"
        ]
        
        results = {}
        for script_name in scripts:
            script_path = project_root / script_name
            if script_path.exists() and script_path.is_file():
                # 実行権限をチェック
                if os.access(script_path, os.X_OK):
                    results[script_name] = {"status": "✅", "message": f"Script {script_name} is executable"}
                    logger.info(f"✅ {script_name}: Script is executable")
                else:
                    results[script_name] = {"status": "⚠️", "message": f"Script {script_name} exists but not executable"}
                    logger.warning(f"⚠️ {script_name}: Script exists but not executable")
            else:
                results[script_name] = {"status": "❌", "message": f"Script {script_name} not found"}
                logger.error(f"❌ {script_name}: Script not found")
        
        return results
    
    def run_all_tests(self) -> dict:
        """すべてのテストを実行"""
        logger.info("Starting simple connection tests...")
        
        all_results = {
            "environment_variables": self.test_environment_variables(),
            "file_structure": self.test_file_structure(),
            "config_files": self.test_config_files(),
            "python_imports": self.test_python_imports(),
            "scripts_executability": self.test_scripts_executability()
        }
        
        return all_results
    
    def print_summary(self, results: dict):
        """結果のサマリーを表示"""
        logger.info("\n" + "="*60)
        logger.info("SIMPLE CONNECTION TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, category_results in results.items():
            logger.info(f"\n{category.upper().replace('_', ' ')}:")
            logger.info("-" * 40)
            
            for item_name, item_result in category_results.items():
                status = item_result["status"]
                message = item_result["message"]
                logger.info(f"{status} {item_name}: {message}")
                
                total_tests += 1
                if status == "✅":
                    passed_tests += 1
        
        logger.info("\n" + "="*60)
        logger.info(f"OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! Ready for external connection testing.")
        elif passed_tests >= total_tests * 0.8:
            logger.info("⚠️  Most tests passed. Some issues need attention.")
        else:
            logger.info("❌ Many tests failed. Please check the configuration.")
        
        logger.info("="*60)
    
    def save_results(self, results: dict):
        """結果を保存"""
        results_file = project_root / "config" / "simple_test_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test results saved to {results_file}")


def main():
    """メイン関数"""
    tester = SimpleConnectionTester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    tester.save_results(results)
    
    # 成功したテストの数を確認
    total_tests = sum(len(category_results) for category_results in results.values())
    passed_tests = sum(
        sum(1 for item_result in category_results.values() if item_result["status"] == "✅")
        for category_results in results.values()
    )
    
    if passed_tests >= total_tests * 0.8:
        logger.info("Tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("Many tests failed. Please check the configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
