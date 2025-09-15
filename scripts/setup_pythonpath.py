#!/usr/bin/env python3
"""
Pythonパス設定スクリプト

プロジェクトルートをPYTHONPATHに追加して、相対インポートを正しく動作させます。
"""

import os
import sys
from pathlib import Path

def setup_pythonpath():
    """Pythonパスを設定"""
    project_root = Path(__file__).parent.parent
    project_root_str = str(project_root)
    
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        print(f"✅ Added to PYTHONPATH: {project_root_str}")
    else:
        print(f"ℹ️  Already in PYTHONPATH: {project_root_str}")

if __name__ == "__main__":
    setup_pythonpath()
