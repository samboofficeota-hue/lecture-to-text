#!/usr/bin/env python3
"""
MyGPTs作成テストスクリプト

MyGPTsの作成と動作確認を行います。
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

def test_mygpt_config():
    """MyGPTs設定をテスト"""
    print("\n=== MyGPTs設定テスト ===")
    
    # 設定を作成
    config = MyGPTConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4000,
        mygpt_id="g-68c7fe5c36b88191b0f242cc9c5c65aa"
    )
    
    print(f"API Key: {config.api_key[:10]}..." if config.api_key else "❌ API Key not set")
    print(f"Model: {config.model}")
    print(f"Temperature: {config.temperature}")
    print(f"Max Tokens: {config.max_tokens}")
    
    # 設定の妥当性を検証
    if config.validate():
        print("✅ 設定は有効です")
        return config
    else:
        print("❌ 設定が無効です")
        return None

def test_mygpt_adapter(config):
    """MyGPTsアダプターをテスト"""
    print("\n=== MyGPTsアダプターテスト ===")
    
    try:
        # アダプターを初期化
        adapter = MyGPTAdapter(config.to_dict())
        print("✅ MyGPTsアダプターの初期化に成功")
        
        # 簡単なテスト
        test_text = "経済学の講義で、需要と供給の関係について説明します。"
        print(f"\nテストテキスト: {test_text}")
        
        # RAG処理をテスト
        result = adapter.process_with_rag(test_text)
        print(f"✅ RAG処理結果: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MyGPTsアダプターのテストに失敗: {e}")
        return False

def create_mygpt_instructions():
    """MyGPTs用の指示文を作成"""
    print("\n=== MyGPTs指示文作成 ===")
    
    instructions = """
あなたは講義の文字起こしと専門用語の統一を支援するAIアシスタントです。

主な役割:
1. 講義の文字起こしテキストの品質向上
2. 専門用語の統一と表記揺れの修正
3. 経済学・会計学・コーポレートガバナンス分野の専門知識提供
4. 用語の一貫性と概念の統一性を保つ

専門分野:
- 経済学（ミクロ・マクロ経済学）
- 会計学・財務
- コーポレートガバナンス
- 企業法・金融商品取引法

対応言語: 日本語

出力形式:
- 修正されたテキスト
- 用語の統一表
- 概念の説明
- 改善提案

注意事項:
- 専門用語は正確性を重視
- 表記揺れを統一
- 文脈に応じた適切な用語選択
- 概念の一貫性を保つ
"""
    
    # 指示文をファイルに保存
    instructions_file = project_root / "mygpt_instructions.txt"
    with open(instructions_file, "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"✅ MyGPTs指示文を作成しました: {instructions_file}")
    return instructions

def create_knowledge_base_files():
    """知識ベース用ファイルを作成"""
    print("\n=== 知識ベースファイル作成 ===")
    
    # 用語集ファイルを確認
    glossary_file = project_root / "glossaries" / "accounting_finance.csv"
    if glossary_file.exists():
        print(f"✅ 用語集ファイルが見つかりました: {glossary_file}")
        
        # 用語集の内容を確認
        with open(glossary_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"   用語数: {len(lines)}")
            print(f"   最初の5行: {lines[:5]}")
    else:
        print(f"❌ 用語集ファイルが見つかりません: {glossary_file}")
    
    # 経済学用語集を作成
    economics_glossary = project_root / "glossaries" / "economics.csv"
    if not economics_glossary.exists():
        economics_terms = [
            "需要,demand,経済学の基本概念",
            "供給,supply,経済学の基本概念",
            "価格,price,市場での取引価格",
            "GDP,国内総生産,Gross Domestic Product",
            "インフレ,インフレーション,物価の上昇",
            "デフレ,デフレーション,物価の下落",
            "市場,market,取引が行われる場",
            "競争,competition,市場での競争",
            "独占,monopoly,市場の独占",
            "寡占,oligopoly,少数企業による市場支配"
        ]
        
        with open(economics_glossary, "w", encoding="utf-8") as f:
            f.write("用語,英語,説明\n")
            for term in economics_terms:
                f.write(f"{term}\n")
        
        print(f"✅ 経済学用語集を作成しました: {economics_glossary}")

def main():
    """メイン処理"""
    print("=== MyGPTs作成テスト開始 ===")
    
    # 環境変数を読み込み
    load_environment()
    
    # 設定をテスト
    config = test_mygpt_config()
    if not config:
        print("❌ 設定テストに失敗しました")
        return
    
    # アダプターをテスト
    if not test_mygpt_adapter(config):
        print("❌ アダプターテストに失敗しました")
        return
    
    # MyGPTs指示文を作成
    create_mygpt_instructions()
    
    # 知識ベースファイルを作成
    create_knowledge_base_files()
    
    print("\n=== MyGPTs作成準備完了 ===")
    print("\n次のステップ:")
    print("1. ChatGPTでMyGPTsを作成")
    print("2. 作成した指示文をコピー&ペースト")
    print("3. 用語集ファイルをアップロード")
    print("4. テストを実行")

if __name__ == "__main__":
    main()
