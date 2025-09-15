#!/usr/bin/env python3
"""
相対インポート復元スクリプト

絶対インポートを相対インポートに戻します。
"""

import os
import re
from pathlib import Path

def restore_imports_in_file(file_path):
    """ファイル内の絶対インポートを相対インポートに戻す"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 絶対インポートを相対インポートに変換
    patterns = [
        (r'from core\.', 'from ...core.'),
        (r'from utils\.', 'from ...utils.'),
        (r'from learning\.', 'from ...learning.'),
        (r'from config\.', 'from ...config.'),
    ]
    
    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Restored relative imports in: {file_path}")
        return True
    else:
        print(f"⏭️  No changes needed: {file_path}")
        return False

def main():
    """メイン関数"""
    project_root = Path(__file__).parent.parent
    
    # 修正対象のファイルを検索
    adapter_files = list(project_root.glob("adapters/**/*.py"))
    utils_files = list(project_root.glob("utils/**/*.py"))
    
    all_files = adapter_files + utils_files
    
    fixed_count = 0
    total_count = len(all_files)
    
    print(f"Found {total_count} files to check...")
    
    for file_path in all_files:
        if restore_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\nRestored {fixed_count}/{total_count} files")
    
    if fixed_count > 0:
        print("✅ Relative imports restored!")
    else:
        print("ℹ️  No changes were needed.")

if __name__ == "__main__":
    main()
