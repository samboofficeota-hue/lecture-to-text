#!/usr/bin/env python3
"""
インポート修正スクリプト

相対インポートを絶対インポートに修正します。
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """ファイル内の相対インポートを修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 相対インポートを絶対インポートに変換
    patterns = [
        (r'from \.\.\.core\.', 'from core.'),
        (r'from \.\.\.utils\.', 'from utils.'),
        (r'from \.\.\.learning\.', 'from learning.'),
        (r'from \.\.\.config\.', 'from config.'),
    ]
    
    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed imports in: {file_path}")
        return True
    else:
        print(f"⏭️  No changes needed: {file_path}")
        return False

def main():
    """メイン関数"""
    project_root = Path(__file__).parent.parent
    
    # 修正対象のファイルを検索
    adapter_files = list(project_root.glob("adapters/**/*.py"))
    
    fixed_count = 0
    total_count = len(adapter_files)
    
    print(f"Found {total_count} adapter files to check...")
    
    for file_path in adapter_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count}/{total_count} files")
    
    if fixed_count > 0:
        print("✅ Import fixes completed!")
    else:
        print("ℹ️  No import fixes were needed.")

if __name__ == "__main__":
    main()
