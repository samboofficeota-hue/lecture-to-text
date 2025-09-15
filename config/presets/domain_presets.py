"""
ドメイン別プリセット定義

各分野（経済学、会計学等）の設定プリセットを定義します。
"""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class DomainPreset:
    """ドメイン別プリセット"""
    name: str
    description: str
    whisper_model: str
    openai_model: str
    temperature: float
    max_tokens: int
    glossary_files: List[str]
    rag_sources: List[str]
    domain_keywords: List[str]


# ドメイン別プリセット定義
DOMAIN_PRESETS = {
    "general": DomainPreset(
        name="general",
        description="一般的な講義",
        whisper_model="large-v3",
        openai_model="gpt-4o",
        temperature=0.3,
        max_tokens=4000,
        glossary_files=["general.csv"],
        rag_sources=["general_knowledge"],
        domain_keywords=["講義", "説明", "内容"]
    ),
    
    "economics": DomainPreset(
        name="economics",
        description="経済学講義",
        whisper_model="large-v3",
        openai_model="gpt-4o",
        temperature=0.2,
        max_tokens=4000,
        glossary_files=["economics.csv", "accounting_finance.csv"],
        rag_sources=["economics_knowledge", "company_data"],
        domain_keywords=["経済", "市場", "需要", "供給", "価格", "GDP", "インフレ"]
    ),
    
    "accounting": DomainPreset(
        name="accounting",
        description="会計学講義",
        whisper_model="large-v3",
        openai_model="gpt-4o",
        temperature=0.2,
        max_tokens=4000,
        glossary_files=["accounting_finance.csv"],
        rag_sources=["accounting_standards", "company_data"],
        domain_keywords=["会計", "財務", "貸借対照表", "損益計算書", "キャッシュフロー"]
    ),
    
    "corporate_governance": DomainPreset(
        name="corporate_governance",
        description="コーポレートガバナンス講義",
        whisper_model="large-v3",
        openai_model="gpt-4o",
        temperature=0.2,
        max_tokens=4000,
        glossary_files=["corporate_governance.csv"],
        rag_sources=["corporate_law", "governance_code"],
        domain_keywords=["ガバナンス", "取締役", "監査", "コンプライアンス", "ステークホルダー"]
    )
}


def get_domain_preset(domain: str) -> DomainPreset:
    """ドメイン別プリセットを取得"""
    return DOMAIN_PRESETS.get(domain, DOMAIN_PRESETS["general"])


def list_available_domains() -> List[str]:
    """利用可能なドメイン一覧を取得"""
    return list(DOMAIN_PRESETS.keys())
