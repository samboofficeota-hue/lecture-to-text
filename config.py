#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
設定ファイル
"""

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# OpenAI API設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHATGPT_MODEL = os.getenv("CHATGPT_MODEL", "gpt-4")
CHATGPT_TEMPERATURE = float(os.getenv("CHATGPT_TEMPERATURE", "0.3"))
CHATGPT_MAX_TOKENS = int(os.getenv("CHATGPT_MAX_TOKENS", "4000"))

# Whisper設定
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "auto")

# 出力設定
DEFAULT_OUTPUT_DIR = "./output"
DEFAULT_GLOSSARY_FILE = "glossary.csv"
