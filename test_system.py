#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
システムテスト用スクリプト
"""

import os
import sys
from pathlib import Path

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("=== インポートテスト ===")
    
    try:
        import faster_whisper
        print("✓ faster-whisper")
    except ImportError as e:
        print(f"✗ faster-whisper: {e}")
        return False
    
    try:
        import ffmpeg
        print("✓ ffmpeg-python")
    except ImportError as e:
        print(f"✗ ffmpeg-python: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
    
    try:
        import openai
        print("✓ openai")
    except ImportError as e:
        print(f"✗ openai: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    return True

def test_config():
    """設定ファイルのテスト"""
    print("\n=== 設定テスト ===")
    
    try:
        from config import OPENAI_API_KEY, CHATGPT_MODEL
        print(f"✓ 設定ファイル読み込み成功")
        print(f"  - ChatGPTモデル: {CHATGPT_MODEL}")
        
        if OPENAI_API_KEY:
            print(f"  - APIキー: {OPENAI_API_KEY[:10]}...")
        else:
            print("  - ⚠️ APIキーが設定されていません")
            print("    .envファイルにOPENAI_API_KEYを設定してください")
        
        return True
    except Exception as e:
        print(f"✗ 設定ファイルエラー: {e}")
        return False

def test_text_enhancer():
    """TextEnhancerクラスのテスト"""
    print("\n=== TextEnhancerテスト ===")
    
    try:
        from text_enhancer import TextEnhancer
        print("✓ TextEnhancerクラス読み込み成功")
        
        # APIキーが設定されている場合のみテスト
        from config import OPENAI_API_KEY
        if OPENAI_API_KEY:
            try:
                enhancer = TextEnhancer()
                print("✓ TextEnhancer初期化成功")
                return True
            except Exception as e:
                print(f"✗ TextEnhancer初期化エラー: {e}")
                return False
        else:
            print("⚠️ APIキーが設定されていないため、TextEnhancerテストをスキップ")
            return True
            
    except Exception as e:
        print(f"✗ TextEnhancerクラスエラー: {e}")
        return False

def test_lecture_pipeline():
    """lecture_pipelineモジュールのテスト"""
    print("\n=== lecture_pipelineテスト ===")
    
    try:
        import lecture_pipeline
        print("✓ lecture_pipelineモジュール読み込み成功")
        return True
    except Exception as e:
        print(f"✗ lecture_pipelineモジュールエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("講義動画から教材自動生成システム - テスト実行")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_text_enhancer,
        test_lecture_pipeline
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== テスト結果 ===")
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("✓ すべてのテストが通過しました！")
        print("\n使用方法:")
        print("python lecture_pipeline.py --input your_video.mp4 --use-chatgpt --title '講義タイトル'")
    else:
        print("✗ 一部のテストが失敗しました。")
        print("エラーメッセージを確認して、必要な依存関係をインストールしてください。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
