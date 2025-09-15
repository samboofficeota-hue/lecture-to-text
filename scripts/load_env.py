#!/usr/bin/env python3
"""
環境変数読み込みスクリプト

.envファイルから環境変数を読み込みます。
"""

import os
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

if __name__ == "__main__":
    load_env_file()
