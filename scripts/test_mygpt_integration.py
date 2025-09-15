#!/usr/bin/env python3
"""
MyGPTs統合テストスクリプト

実際のMyGPTsとの連携をテストします。
"""

import os
import sys
import json
from pathlib import Path

# プロジェクトルートをPYTHONPATHに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from adapters.mygpt.mygpt_adapter import MyGPTAdapter
from adapters.mygpt.mygpt_config import MyGPTConfig

def load_environment():
    """環境変数を読み込み"""
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 環境変数を読み込みました: {env_file}")
    else:
        print(f"⚠️ 環境変数ファイルが見つかりません: {env_file}")

def test_mygpt_connection():
    """MyGPTs接続をテスト"""
    print("\n=== MyGPTs接続テスト ===")
    
    # 設定を作成（APIキーは自動的にOPENAI_API_KEYから取得）
    config = MyGPTConfig(
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4000,
        mygpt_id="g-68c7fe5c36b88191b0f242cc9c5c65aa"
    )
    
    print(f"MyGPTs ID: {config.mygpt_id}")
    print(f"API Key: {config.api_key[:10]}..." if config.api_key else "❌ API Key not set")
    
    if not config.api_key:
        print("❌ OpenAI API Keyが設定されていません")
        return False
    
    try:
        # アダプターを初期化
        adapter = MyGPTAdapter(config.to_dict())
        print("✅ MyGPTsアダプターの初期化に成功")
        
        # 簡単なテスト
        test_text = "経済学の講義で、需要と供給の関係について説明します。"
        print(f"\nテストテキスト: {test_text}")
        
        # RAG処理をテスト
        result = adapter.process_with_rag(test_text)
        print(f"✅ RAG処理結果: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MyGPTs接続テストに失敗: {e}")
        return False

def test_lecture_processing():
    """講義処理のテスト"""
    print("\n=== 講義処理テスト ===")
    
    # 設定を作成（APIキーは自動的にOPENAI_API_KEYから取得）
    config = MyGPTConfig(
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4000,
        mygpt_id="g-68c7fe5c36b88191b0f242cc9c5c65aa"
    )
    
    try:
        adapter = MyGPTAdapter(config.to_dict())
        
        # 講義テキストのサンプル
        lecture_text = """
        今日は経済学の基礎について説明します。
        まず、需要と供給の関係について見ていきましょう。
        需要は、消費者が商品やサービスを購入したいと思う量のことです。
        供給は、生産者が商品やサービスを提供したいと思う量のことです。
        価格は需要と供給のバランスによって決まります。
        """
        
        print(f"元のテキスト:\n{lecture_text}")
        
        # RAG処理を実行
        enhanced_text = adapter.process_with_rag(lecture_text)
        print(f"\n✅ 改善されたテキスト:\n{enhanced_text}")
        
        # 用語検索をテスト
        print("\n=== 用語検索テスト ===")
        terms = adapter.search_similar_terms("需要", "economics")
        print(f"類似用語: {terms}")
        
        # 知識検索をテスト
        print("\n=== 知識検索テスト ===")
        knowledge = adapter.retrieve_knowledge("経済学の基本概念", "economics")
        print(f"取得した知識: {knowledge[0].content[:200]}..." if knowledge else "知識が見つかりませんでした")
        
        return True
        
    except Exception as e:
        print(f"❌ 講義処理テストに失敗: {e}")
        return False

def test_domain_specific_processing():
    """分野別処理のテスト"""
    print("\n=== 分野別処理テスト ===")
    
    config = MyGPTConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4000,
        mygpt_id="g-68c7fe5c36b88191b0f242cc9c5c65aa"
    )
    
    try:
        adapter = MyGPTAdapter(config.to_dict())
        
        # 会計学のテキスト
        accounting_text = """
        貸借対照表について説明します。
        資産は企業が所有する財産です。
        負債は企業が負っている債務です。
        純資産は資産から負債を引いたものです。
        """
        
        print(f"会計学テキスト:\n{accounting_text}")
        
        # 概念統一をテスト
        unified_text = adapter.unify_concepts(accounting_text, "accounting")
        print(f"\n✅ 概念統一済みテキスト:\n{unified_text}")
        
        # 用語検証をテスト
        validation_result = adapter.validate_terminology(accounting_text, "accounting")
        print(f"\n✅ 用語検証結果: {validation_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分野別処理テストに失敗: {e}")
        return False

def main():
    """メイン処理"""
    print("=== MyGPTs統合テスト開始 ===")
    
    # 環境変数を読み込み
    load_environment()
    
    # 接続テスト
    if not test_mygpt_connection():
        print("❌ 接続テストに失敗しました")
        return
    
    # 講義処理テスト
    if not test_lecture_processing():
        print("❌ 講義処理テストに失敗しました")
        return
    
    # 分野別処理テスト
    if not test_domain_specific_processing():
        print("❌ 分野別処理テストに失敗しました")
        return
    
    print("\n=== すべてのテストが成功しました！ ===")
    print("\nMyGPTs統合が完了しました。")
    print("次のステップ:")
    print("1. 実際の講義データでテスト")
    print("2. 用語集の拡充")
    print("3. プロンプトの最適化")

if __name__ == "__main__":
    main()
