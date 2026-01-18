from pydantic import BaseModel, Field
from typing import List, Optional


class AccentPhrase(BaseModel):
    """アクセント句の拡張情報"""
    moras: List[dict]
    accent: int
    pause_mora: Optional[dict] = None
    is_interrogative: bool = False


class ExtendedDictEntry(BaseModel):
    """拡張辞書エントリ"""
    word: str = Field(..., min_length=1, description="単語")
    pronunciation: str = Field(..., min_length=1, description="発音（カタカナ）")
    accent_type: int = Field(..., description="アクセント型")
    mora_count: Optional[int] = Field(None, description="モーラ数")
    accent_phrases: Optional[List[AccentPhrase]] = Field(None, description="アクセント句情報")
    pitch_values: Optional[List[float]] = Field(None, description="ピッチ値のリスト")
    length_values: Optional[List[float]] = Field(None, description="長さ値のリスト")
    speaker_id: Optional[int] = Field(None, description="話者ID")


class DictionaryResponse(BaseModel):
    """辞書レスポンス"""
    entries: List[ExtendedDictEntry]
    total: int
