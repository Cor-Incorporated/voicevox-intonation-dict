"""
拡張合成APIルーター

拡張辞書を適用した音声合成エンドポイントを提供します。
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
import json
from pathlib import Path
import logging

from app.models.extended_dict import ExtendedDictEntry
from app.services.voicevox_client import VoicevoxClient
from app.services.audio_query_service import AudioQueryService
from app.services.matcher import DictionaryMatcher
from app.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# ログレベルを DEBUG に設定
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)


class SynthesizeRequest(BaseModel):
    """音声合成リクエスト"""
    text: str = Field(..., description="合成するテキスト", min_length=1, max_length=1000)
    speaker: int = Field(1, description="話者ID", ge=0)


class PreviewRequest(BaseModel):
    """プレビュー合成リクエスト（AudioQuery直接指定）"""
    audio_query: dict = Field(..., description="AudioQuery")
    speaker: int = Field(1, description="話者ID", ge=0)


class ApplyDictionaryRequest(BaseModel):
    """辞書適用リクエスト（AudioQuery変換用）"""
    audio_query: dict = Field(..., description="AudioQuery")
    text: str = Field(..., description="元のテキスト（マッチング用）")
    speaker: int = Field(1, description="話者ID", ge=0)


class ApplyDictionaryResponse(BaseModel):
    """辞書適用レスポンス"""
    audio_query: dict = Field(..., description="辞書適用後のAudioQuery")
    matches_found: int = Field(..., description="マッチした辞書エントリ数")
    applied_entries: list[str] = Field(default_factory=list, description="適用されたエントリのword一覧")


class SynthesizeResponse(BaseModel):
    """音声合成レスポンス（デバッグ用）"""
    message: str
    matches_found: int
    modified_query: dict


def get_dict_path() -> Path:
    """辞書ファイルのパスを取得"""
    return Path(settings.data_dir) / "extended_dict.json"


def load_dictionary() -> list[ExtendedDictEntry]:
    """辞書をロード"""
    dict_path = get_dict_path()
    if not dict_path.exists():
        return []

    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [ExtendedDictEntry(**entry) for entry in data]


@router.post("/synthesize", response_class=Response)
async def synthesize_with_extended_dict(request: SynthesizeRequest) -> Response:
    """
    拡張辞書を適用した音声合成

    1. VOICEVOX Engine で AudioQuery 生成
    2. 拡張辞書で単語マッチング
    3. マッチした箇所の pitch/length を上書き
    4. 上書き後の AudioQuery で音声合成
    5. WAV データを返却

    Args:
        request: 音声合成リクエスト（text, speaker）

    Returns:
        WAV 音声データ

    Raises:
        HTTPException: VOICEVOX Engine 接続エラー (503)
    """
    client = VoicevoxClient()
    matcher = DictionaryMatcher()

    try:
        # 1. VOICEVOX Engine で AudioQuery 生成
        logger.info(f"Generating AudioQuery for: {request.text}")
        audio_query = await client.create_audio_query(request.text, request.speaker)

        # 2. 拡張辞書をロード
        entries = load_dictionary()
        logger.info(f"Loaded {len(entries)} dictionary entries")

        # 3. 単語マッチング（部分一致対応、入力テキストでフィルタリング）
        matches = matcher.find_matches_with_text(audio_query, entries, request.text)
        logger.info(f"Found {len(matches)} matches")

        # 4. マッチした箇所を上書き（部分マッチ対応）
        modified_query = audio_query
        for match in matches:
            logger.info(
                f"Applying {match.entry.word} at phrase {match.accent_phrase_index}, "
                f"moras {match.mora_start_index}-{match.mora_end_index}"
            )
            try:
                modified_query = AudioQueryService.apply_partial_match(
                    modified_query,
                    match.entry,
                    match.accent_phrase_index,
                    match.mora_start_index,
                    match.mora_end_index,
                )
            except ValueError as e:
                logger.warning(f"Failed to apply dict entry {match.entry.word}: {e}")
                # モーラ数不一致などの場合はスキップして続行
                continue

        # 5. 音声合成
        logger.info("Synthesizing audio with modified query")
        audio_data = await client.synthesis(modified_query, request.speaker)

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="synthesis.wav"',
                "X-Matches-Found": str(len(matches)),
            }
        )

    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"VOICEVOX Engine is not available: {str(e)}"
        )
    finally:
        await client.close()


@router.post("/synthesize/debug")
async def synthesize_debug(request: SynthesizeRequest) -> SynthesizeResponse:
    """
    拡張辞書適用のデバッグ用エンドポイント

    音声合成は行わず、AudioQuery の変更内容を返却します。
    """
    client = VoicevoxClient()
    matcher = DictionaryMatcher()

    try:
        # AudioQuery 生成
        audio_query = await client.create_audio_query(request.text, request.speaker)

        # 辞書ロード
        entries = load_dictionary()

        # マッチング（部分一致対応）
        matches = matcher.find_matches_with_text(audio_query, entries, request.text)

        # 上書き（部分マッチ対応）
        modified_query = audio_query
        for match in matches:
            try:
                modified_query = AudioQueryService.apply_partial_match(
                    modified_query,
                    match.entry,
                    match.accent_phrase_index,
                    match.mora_start_index,
                    match.mora_end_index,
                )
            except ValueError:
                continue

        return SynthesizeResponse(
            message="Debug: Query processed",
            matches_found=len(matches),
            modified_query=modified_query,
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"VOICEVOX Engine is not available: {str(e)}"
        )
    finally:
        await client.close()


@router.post("/synthesize/preview", response_class=Response)
async def synthesize_preview(request: PreviewRequest) -> Response:
    """
    プレビュー用音声合成（AudioQueryを直接指定）

    辞書を参照せず、渡されたAudioQueryをそのまま使って音声合成します。
    スライダー調整中のリアルタイムプレビューに使用。

    Args:
        request: プレビューリクエスト（audio_query, speaker）

    Returns:
        WAV 音声データ
    """
    client = VoicevoxClient()

    try:
        logger.info("Preview synthesis with custom AudioQuery")
        audio_data = await client.synthesis(request.audio_query, request.speaker)

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="preview.wav"',
            }
        )

    except Exception as e:
        logger.error(f"Preview synthesis error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"VOICEVOX Engine is not available: {str(e)}"
        )
    finally:
        await client.close()


@router.post("/synthesize/apply")
async def apply_dictionary(request: ApplyDictionaryRequest) -> ApplyDictionaryResponse:
    """
    AudioQueryに拡張辞書を適用して返す（音声合成は行わない）

    Editor のメイン合成フローから呼び出され、AudioQueryのピッチ・長さを
    辞書に基づいて上書きします。

    Args:
        request: AudioQuery, 元のテキスト, 話者ID

    Returns:
        辞書適用後のAudioQueryと適用情報

    Note:
        - 拡張辞書サーバーが落ちていてもEditorは動作します（フォールバック）
        - マッチしなかった場合は元のAudioQueryがそのまま返されます
    """
    matcher = DictionaryMatcher()

    try:
        # 辞書ロード
        entries = load_dictionary()
        logger.info(f"Loaded {len(entries)} dictionary entries for apply")

        if not entries:
            return ApplyDictionaryResponse(
                audio_query=request.audio_query,
                matches_found=0,
                applied_entries=[],
            )

        # マッチング（部分一致対応、入力テキストでフィルタリング）
        matches = matcher.find_matches_with_text(
            request.audio_query, entries, request.text
        )
        logger.info(f"Found {len(matches)} matches for text: {request.text}")

        # 上書き（部分マッチ対応）
        modified_query = request.audio_query
        applied_entries: list[str] = []

        for match in matches:
            logger.info(
                f"Applying {match.entry.word} at phrase {match.accent_phrase_index}, "
                f"moras {match.mora_start_index}-{match.mora_end_index}"
            )
            try:
                modified_query = AudioQueryService.apply_partial_match(
                    modified_query,
                    match.entry,
                    match.accent_phrase_index,
                    match.mora_start_index,
                    match.mora_end_index,
                )
                applied_entries.append(match.entry.word)
            except ValueError as e:
                logger.warning(f"Failed to apply dict entry {match.entry.word}: {e}")
                continue

        return ApplyDictionaryResponse(
            audio_query=modified_query,
            matches_found=len(matches),
            applied_entries=applied_entries,
        )

    except Exception as e:
        logger.error(f"Apply dictionary error: {e}")
        # エラー時は元のAudioQueryを返す（Editorは動き続ける）
        return ApplyDictionaryResponse(
            audio_query=request.audio_query,
            matches_found=0,
            applied_entries=[],
        )


@router.get("/health")
async def synthesis_health():
    """合成サービスのヘルスチェック"""
    client = VoicevoxClient()
    try:
        version = await client.get_version()
        return {
            "status": "healthy",
            "voicevox_version": version,
            "dictionary_entries": len(load_dictionary()),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
    finally:
        await client.close()
