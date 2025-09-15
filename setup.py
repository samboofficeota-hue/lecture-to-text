"""
Darwin Lecture-to-Text パッケージ設定

このファイルにより、プロジェクトがPythonパッケージとして正しく認識されます。
"""

from setuptools import setup, find_packages

setup(
    name="darwin-lecture-to-text",
    version="1.0.0",
    description="AI-powered lecture transcription and analysis system",
    author="Darwin Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.0.0",
        "faster-whisper>=0.10.0",
        "google-cloud-storage>=3.0.0",
        "google-cloud-pubsub>=2.0.0",
        "google-cloud-tasks>=2.0.0",
        "google-cloud-logging>=3.0.0",
        "requests>=2.25.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "darwin=main:main",
        ],
    },
)
