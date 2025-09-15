#!/usr/bin/env python3
"""
環境変数読み込み付き実行スクリプト

.envファイルを読み込んでからPythonスクリプトを実行します。
"""

import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """環境変数ファイルを読み込み"""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ 環境変数を読み込みました: {env_file}")
    else:
        print(f"❌ 環境変数ファイルが見つかりません: {env_file}")

def run_script(script_path):
    """スクリプトを実行"""
    project_root = Path(__file__).parent.parent
    
    # PYTHONPATHを設定
    pythonpath = str(project_root)
    if 'PYTHONPATH' in os.environ:
        os.environ['PYTHONPATH'] = f"{pythonpath}:{os.environ['PYTHONPATH']}"
    else:
        os.environ['PYTHONPATH'] = pythonpath
    
    # スクリプトを実行
    cmd = [sys.executable, str(script_path)]
    print(f"実行中: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ スクリプト実行エラー: {e}")
        return e.returncode

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 scripts/run_with_env.py <スクリプトパス>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    
    # 環境変数を読み込み
    load_env_file()
    
    # スクリプトを実行
    exit_code = run_script(script_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
