"""
プリセット管理

分野別の設定プリセットを管理します。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..settings import Settings, WhisperConfig, RAGConfig


@dataclass
class DomainPreset:
    """分野別プリセット"""
    name: str
    domain: str
    description: str
    whisper_config: Dict[str, Any]
    rag_config: Dict[str, Any]
    glossary_terms: List[str]
    initial_prompt: str
    postprocessing_rules: Dict[str, str]


class PresetManager:
    """プリセット管理"""
    
    def __init__(self):
        """プリセット管理を初期化"""
        self.presets: Dict[str, DomainPreset] = {}
        self._load_default_presets()
    
    def _load_default_presets(self):
        """デフォルトプリセットを読み込み"""
        # 会計・財務プリセット
        self.presets["会計・財務"] = DomainPreset(
            name="会計・財務",
            domain="会計・財務",
            description="会計・財務分野の講義用プリセット",
            whisper_config={
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "initial_prompt": "これは会計・財務の講義です。専門用語が多く含まれています。"
            },
            rag_config={
                "use_mygpt": True,
                "use_chatgpt": True,
                "confidence_threshold": 0.8,
                "max_context_length": 4000
            },
            glossary_terms=[
                "財務報告", "純利益", "純資産", "基準", "成果", "投資",
                "事業遂行", "構築", "相対的", "一括管理", "金融投資",
                "確実", "保有者", "サイミュレーション", "定義", "注目",
                "経営", "減損", "利益", "正しい", "確実性", "チャプター",
                "概念フレームワーク", "財務報告", "投資者", "企業価値",
                "開示", "ポジション", "価値", "解釈", "構成要素", "各項目",
                "法規制", "特定期間", "変動", "報告主体", "5年間", "オプション",
                "取引", "リスク", "解放", "期待された", "実際", "確定",
                "キャッシュフロー", "裏付け", "事実", "事業投資", "責任",
                "遂行を通じて", "独立", "資産", "拡大", "事実として",
                "観点", "基づいて", "識別", "事業遂行上", "構成価値",
                "確保", "時価", "変動", "利益", "確実", "投資", "事業目的",
                "構築", "保有者", "値上がり", "期待", "価値", "変動事実",
                "として", "リスク", "解放", "ものとなる", "また", "金融投資",
                "時価", "変動", "基づいて", "相対的", "認識", "ため", "時価",
                "評価", "サイミュレーション", "構成要素", "定義", "注目",
                "項目", "認識", "基礎", "経営", "減損", "少なくとも", "一方",
                "利益", "経営", "定義", "満たした", "項目", "財務諸表情",
                "認識対象", "正しい", "加え", "一定程度", "発生可能性",
                "確実性", "求められる"
            ],
            initial_prompt="これは会計・財務の講義です。専門用語が多く含まれています。",
            postprocessing_rules={
                "罪務": "財務",
                "罪有者": "所有者",
                "創数": "総数",
                "順利益": "純利益",
                "順次": "純資産",
                "基隣": "基準",
                "正化": "成果",
                "通し": "投資",
                "事業水行": "事業遂行",
                "構測": "構築",
                "相影気": "相対的",
                "一区限管": "一括管理",
                "金入通し": "金融投資",
                "確保": "確保",
                "確讆": "確実",
                "通証儒": "投資",
                "保養師": "保有者",
                "調子": "投資",
                "ザイミューショーション": "サイミュレーション",
                "ザイミューショー": "サイミュレーション",
                "提議": "定義",
                "注束": "注目",
                "経役": "経営",
                "減速": "減損",
                "理想": "利益",
                "経験": "経営",
                "正じる": "正しい",
                "格好外全性": "確実性",
                "チャプターさん": "チャプター",
                "概念フレームワーク": "概念フレームワーク",
                "罪務法国": "財務報告",
                "当時者": "投資者",
                "企業性化": "企業価値",
                "企業化地": "企業価値",
                "解除": "開示",
                "ポジション": "ポジション",
                "性化": "価値",
                "解じ": "解釈",
                "構成予測": "構成要素",
                "各個法規": "各項目",
                "法規に刺激": "法規制",
                "特定期間": "特定期間",
                "銅石さん": "投資者",
                "辺道学": "変動",
                "法国主体": "報告主体",
                "5月間": "5年間",
                "オプション": "オプション",
                "とり引き": "取引",
                "リスク": "リスク",
                "開放": "解放",
                "通しの正化": "投資の成果",
                "報告したい": "報告主体",
                "期待された": "期待された",
                "実実": "実際",
                "確定": "確定",
                "キャッシュフロー": "キャッシュフロー",
                "裏付け": "裏付け",
                "事店": "事実",
                "事業通し": "事業投資",
                "先役": "責任",
                "水行通じて": "遂行を通じて",
                "エルコード": "エルコード",
                "リスクに構測": "リスクに構築",
                "どくりつ": "独立",
                "子さん": "資産",
                "拡足": "拡大",
                "事実を思って": "事実として",
                "キャッシュフロー": "キャッシュフロー",
                "角度": "観点",
                "もとついて": "基づいて",
                "相影気": "相対的",
                "しき": "識別",
                "一区限管": "一括管理",
                "金入通し": "金融投資",
                "事業水行上": "事業遂行上",
                "先役": "責任",
                "構成価値": "構成価値",
                "確保": "確保",
                "時間": "時価",
                "変動": "変動",
                "利益": "利益",
                "確讆": "確実",
                "通証儒": "投資",
                "事業目的": "事業目的",
                "構測": "構築",
                "保養師": "保有者",
                "値上がり": "値上がり",
                "期待": "期待",
                "調子": "投資",
                "価値": "価値",
                "変動事実": "変動事実",
                "思って": "として",
                "リスク": "リスク",
                "開放": "解放",
                "ものとなる": "ものとなる",
                "また": "また",
                "金融通締": "金融投資",
                "時間": "時価",
                "変動": "変動",
                "もとついて": "基づいて",
                "相影気": "相対的",
                "認識": "認識",
                "ため": "ため",
                "時間": "時価",
                "評価": "評価",
                "ザイミューショーション": "サイミュレーション",
                "ザイミューショー": "サイミュレーション",
                "構成様子": "構成要素",
                "提議": "定義",
                "注束": "注目",
                "項目": "項目",
                "認識": "認識",
                "きそ": "基礎",
                "経役": "経営",
                "減速": "減損",
                "少なくとも": "少なくとも",
                "一方": "一方",
                "理想": "利益",
                "経験": "経営",
                "提議": "定義",
                "見たした": "満たした",
                "項目": "項目",
                "罪務所表情": "財務諸表情",
                "認識対象": "認識対象",
                "正じる": "正しい",
                "くわえ": "加え",
                "一定程度": "一定程度",
                "発生可能性": "発生可能性",
                "格好外全性": "確実性",
                "求められる": "求められる"
            }
        )
        
        # 技術・工学プリセット
        self.presets["技術・工学"] = DomainPreset(
            name="技術・工学",
            domain="技術・工学",
            description="技術・工学分野の講義用プリセット",
            whisper_config={
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "initial_prompt": "これは技術・工学の講義です。専門用語が多く含まれています。"
            },
            rag_config={
                "use_mygpt": True,
                "use_chatgpt": True,
                "confidence_threshold": 0.8,
                "max_context_length": 4000
            },
            glossary_terms=[
                "アルゴリズム", "データ構造", "プログラミング", "ソフトウェア",
                "ハードウェア", "ネットワーク", "セキュリティ", "データベース",
                "機械学習", "人工知能", "クラウド", "コンテナ", "マイクロサービス"
            ],
            initial_prompt="これは技術・工学の講義です。専門用語が多く含まれています。",
            postprocessing_rules={}
        )
        
        # 経済学プリセット
        self.presets["経済学"] = DomainPreset(
            name="経済学",
            domain="経済学",
            description="経済学分野の講義用プリセット",
            whisper_config={
                "model_size": "large-v3",
                "beam_size": 5,
                "best_of": 5,
                "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "initial_prompt": "これは経済学の講義です。専門用語が多く含まれています。"
            },
            rag_config={
                "use_mygpt": True,
                "use_chatgpt": True,
                "confidence_threshold": 0.8,
                "max_context_length": 4000
            },
            glossary_terms=[
                "需要", "供給", "価格", "市場", "GDP", "インフレ", "失業",
                "財政政策", "金融政策", "経済成長", "ミクロ経済学", "マクロ経済学"
            ],
            initial_prompt="これは経済学の講義です。専門用語が多く含まれています。",
            postprocessing_rules={}
        )
    
    def get_preset(self, domain: str) -> Optional[DomainPreset]:
        """指定分野のプリセットを取得"""
        return self.presets.get(domain)
    
    def list_presets(self) -> List[str]:
        """利用可能なプリセット一覧を取得"""
        return list(self.presets.keys())
    
    def apply_preset(self, settings: Settings, domain: str) -> Settings:
        """プリセットを設定に適用"""
        preset = self.get_preset(domain)
        if not preset:
            raise ValueError(f"Preset not found for domain: {domain}")
        
        # Whisper設定を適用
        for key, value in preset.whisper_config.items():
            if hasattr(settings.whisper, key):
                setattr(settings.whisper, key, value)
        
        # RAG設定を適用
        for key, value in preset.rag_config.items():
            if hasattr(settings.rag, key):
                setattr(settings.rag, key, value)
        
        return settings
    
    def get_glossary_terms(self, domain: str) -> List[str]:
        """分野別の用語リストを取得"""
        preset = self.get_preset(domain)
        if not preset:
            return []
        return preset.glossary_terms
    
    def get_postprocessing_rules(self, domain: str) -> Dict[str, str]:
        """分野別の後処理ルールを取得"""
        preset = self.get_preset(domain)
        if not preset:
            return {}
        return preset.postprocessing_rules
