#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Darwin プロジェクト - メインエントリーポイント

講義録作成システムのメインエントリーポイントです。
"""

import argparse
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.services.lecture_processing_service import LectureProcessingService
from config.settings import get_settings
from config.presets import PresetManager
from utils.logging import setup_logging, get_logger

# アダプターのインポート
from adapters.whisper.whisper_adapter import WhisperAdapter
from adapters.openai.openai_adapter import OpenAIAdapter
from adapters.file.file_adapter import FileAdapter
from adapters.mygpt.mygpt_adapter import MyGPTAdapter


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Darwin - 講義録作成システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使用
  python main.py --input lecture.mp4 --domain "会計・財務"
  
  # PDF資料付きで処理
  python main.py --input lecture.mp4 --pdf materials.pdf --domain "会計・財務"
  
  # 出力ディレクトリを指定
  python main.py --input lecture.mp4 --output ./results --domain "会計・財務"
  
  # プリセット一覧を表示
  python main.py --list-presets
        """
    )
    
    # 引数の定義
    parser.add_argument(
        "--input", 
        help="入力ファイル（動画 mp4 / 音声 wav, mp3 など）"
    )
    parser.add_argument(
        "--pdf", 
        help="講義資料（PDFファイル）"
    )
    parser.add_argument(
        "--output", 
        default="./output",
        help="出力ディレクトリ（デフォルト: ./output）"
    )
    parser.add_argument(
        "--domain", 
        default="会計・財務",
        help="分野（デフォルト: 会計・財務）"
    )
    parser.add_argument(
        "--title", 
        default="講義録",
        help="講義タイトル（デフォルト: 講義録）"
    )
    parser.add_argument(
        "--model", 
        default="large-v3",
        help="Whisperモデル（デフォルト: large-v3）"
    )
    parser.add_argument(
        "--device", 
        default="auto",
        help="デバイス（auto/cpu/cuda）"
    )
    parser.add_argument(
        "--use-rag", 
        action="store_true",
        help="RAGを使用してテキストを改善"
    )
    parser.add_argument(
        "--skip-rag", 
        action="store_true",
        help="RAGをスキップして従来の処理のみ実行"
    )
    parser.add_argument(
        "--list-presets", 
        action="store_true",
        help="利用可能なプリセット一覧を表示"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="デバッグモード"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="ログレベル"
    )
    
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(level=args.log_level)
    logger = get_logger(__name__)
    
    # プリセット一覧を表示
    if args.list_presets:
        preset_manager = PresetManager()
        presets = preset_manager.list_presets()
        print("利用可能なプリセット:")
        for preset in presets:
            print(f"  - {preset}")
        return
    
    # 入力ファイルの確認
    if not args.input:
        logger.error("--input を指定してください")
        sys.exit(1)
    
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"入力ファイルが見つかりません: {args.input}")
        sys.exit(1)
    
    # PDFファイルの確認
    pdf_path = None
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            logger.error(f"PDFファイルが見つかりません: {args.pdf}")
            sys.exit(1)
        pdf_path = str(pdf_path)
    
    try:
        # 設定を読み込み
        settings = get_settings()
        
        # プリセットを適用
        preset_manager = PresetManager()
        settings = preset_manager.apply_preset(settings, args.domain)
        
        # デバッグモードの設定
        if args.debug:
            settings.debug = True
        
        # アダプターを作成
        audio_processor = FileAdapter()
        transcriber = WhisperAdapter(settings.get_whisper_config())
        text_processor = OpenAIAdapter(settings.get_openai_config())
        output_generator = OpenAIAdapter(settings.get_openai_config())
        rag_interface = MyGPTAdapter(settings.get_rag_config()) if args.use_rag and not args.skip_rag else None
        pdf_processor = FileAdapter() if pdf_path else None
        
        # 講義処理サービスを作成
        lecture_service = LectureProcessingService(
            audio_processor=audio_processor,
            transcriber=transcriber,
            text_processor=text_processor,
            output_generator=output_generator,
            rag_interface=rag_interface,
            pdf_processor=pdf_processor
        )
        
        # 講義を処理
        logger.info(f"講義処理を開始: {args.input}")
        logger.info(f"分野: {args.domain}")
        logger.info(f"出力先: {args.output}")
        
        # 実際の処理
        lecture_record = lecture_service.process_lecture(
            audio_file_path=str(input_path),
            pdf_file_path=pdf_path,
            title=args.title,
            domain=args.domain,
            output_dir=args.output,
            use_rag=args.use_rag and not args.skip_rag
        )
        
        logger.info(f"講義処理が完了しました: {lecture_record.id}")
        logger.info(f"出力ファイル: {lecture_record.final_transcript_path}")
        
    except Exception as e:
        logger.error(f"講義処理中にエラーが発生しました: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
