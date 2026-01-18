from fastapi import APIRouter, HTTPException, Depends
from typing import List
import json
import os
from pathlib import Path

from app.models import ExtendedDictEntry, DictionaryResponse
from app.services import VoicevoxClient, AudioQueryService
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def get_dict_path() -> Path:
    """辞書ファイルのパスを取得"""
    return Path(settings.data_dir) / "extended_dict.json"


def load_dictionary() -> List[ExtendedDictEntry]:
    """辞書をロード"""
    dict_path = get_dict_path()
    if not dict_path.exists():
        return []
    
    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [ExtendedDictEntry(**entry) for entry in data]


def save_dictionary(entries: List[ExtendedDictEntry]):
    """辞書を保存"""
    dict_path = get_dict_path()
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dict_path, "w", encoding="utf-8") as f:
        data = [entry.model_dump() for entry in entries]
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("/", response_model=DictionaryResponse)
async def get_dictionary():
    """辞書全体を取得"""
    entries = load_dictionary()
    return DictionaryResponse(entries=entries, total=len(entries))


@router.post("/", response_model=ExtendedDictEntry)
async def add_entry(entry: ExtendedDictEntry):
    """辞書エントリを追加または更新（upsert）

    同じwordが存在する場合は上書き、存在しない場合は追加します。
    """
    entries = load_dictionary()

    # 同じwordのエントリを探して上書き、なければ追加
    updated = False
    for i, existing in enumerate(entries):
        if existing.word == entry.word:
            entries[i] = entry
            updated = True
            break

    if not updated:
        entries.append(entry)

    save_dictionary(entries)
    return entry


@router.get("/search")
async def search_dictionary(word: str):
    """単語で検索"""
    entries = load_dictionary()
    results = [e for e in entries if e.word == word]
    return {"entries": results, "total": len(results)}


@router.delete("/{word}")
async def delete_entry(word: str):
    """辞書エントリを削除"""
    entries = load_dictionary()
    original_count = len(entries)
    entries = [e for e in entries if e.word != word]
    
    if len(entries) == original_count:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    save_dictionary(entries)
    return {"message": f"Deleted entries for word: {word}"}


@router.get("/voicevox/version")
async def get_voicevox_version():
    """VOICEVOX Engineのバージョンを取得"""
    client = VoicevoxClient()
    try:
        version = await client.get_version()
        return {"version": version}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"VOICEVOX Engine error: {str(e)}")
    finally:
        await client.close()


@router.get("/voicevox/speakers")
async def get_voicevox_speakers():
    """VOICEVOX Engineの話者一覧を取得"""
    client = VoicevoxClient()
    try:
        speakers = await client.get_speakers()
        return speakers
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"VOICEVOX Engine error: {str(e)}")
    finally:
        await client.close()
