"""
統合テスト: 拡張合成APIエンドポイント

VOICEVOX Engine をモックして、合成APIの動作を検証します。
"""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path
import tempfile
import os

from app.main import app
from app.models.extended_dict import ExtendedDictEntry


@pytest.fixture
def client():
    """テスト用 FastAPI クライアント"""
    return TestClient(app)


@pytest.fixture
def mock_audio_query():
    """VOICEVOX Engine が返す AudioQuery のモック"""
    return {
        "accent_phrases": [
            {
                "moras": [
                    {"text": "コ", "consonant": "k", "consonant_length": 0.05, "vowel": "o", "vowel_length": 0.12, "pitch": 5.0},
                    {"text": "ン", "consonant": None, "consonant_length": None, "vowel": "N", "vowel_length": 0.08, "pitch": 5.1},
                    {"text": "ニ", "consonant": "n", "consonant_length": 0.05, "vowel": "i", "vowel_length": 0.10, "pitch": 5.2},
                    {"text": "チ", "consonant": "ch", "consonant_length": 0.06, "vowel": "i", "vowel_length": 0.10, "pitch": 5.3},
                    {"text": "ワ", "consonant": "w", "consonant_length": 0.04, "vowel": "a", "vowel_length": 0.15, "pitch": 5.4},
                ],
                "accent": 3,
                "pause_mora": None,
                "is_interrogative": False,
            },
            {
                "moras": [
                    {"text": "ズ", "consonant": "z", "consonant_length": 0.05, "vowel": "u", "vowel_length": 0.12, "pitch": 5.5},
                    {"text": "ン", "consonant": None, "consonant_length": None, "vowel": "N", "vowel_length": 0.08, "pitch": 5.6},
                    {"text": "ダ", "consonant": "d", "consonant_length": 0.05, "vowel": "a", "vowel_length": 0.12, "pitch": 5.7},
                    {"text": "モ", "consonant": "m", "consonant_length": 0.05, "vowel": "o", "vowel_length": 0.12, "pitch": 5.8},
                    {"text": "ン", "consonant": None, "consonant_length": None, "vowel": "N", "vowel_length": 0.10, "pitch": 5.9},
                ],
                "accent": 1,
                "pause_mora": None,
                "is_interrogative": False,
            },
            {
                "moras": [
                    {"text": "デ", "consonant": "d", "consonant_length": 0.05, "vowel": "e", "vowel_length": 0.12, "pitch": 5.0},
                    {"text": "ス", "consonant": "s", "consonant_length": 0.05, "vowel": "u", "vowel_length": 0.10, "pitch": 4.8},
                ],
                "accent": 1,
                "pause_mora": None,
                "is_interrogative": False,
            },
        ],
        "speedScale": 1.0,
        "pitchScale": 0.0,
        "intonationScale": 1.0,
        "volumeScale": 1.0,
        "prePhonemeLength": 0.1,
        "postPhonemeLength": 0.1,
        "outputSamplingRate": 24000,
        "outputStereo": False,
    }


@pytest.fixture
def temp_dict_file(tmp_path):
    """一時的な辞書ファイルを作成"""
    dict_file = tmp_path / "extended_dict.json"
    entries = [
        {
            "word": "ずんだもん",
            "pronunciation": "ズンダモン",
            "accent_type": 1,
            "mora_count": 5,
            "pitch_values": [6.0, 6.1, 6.2, 6.3, 6.4],
            "length_values": [0.15, 0.10, 0.15, 0.15, 0.12],
            "speaker_id": None,
            "accent_phrases": None,
        }
    ]
    dict_file.write_text(json.dumps(entries, ensure_ascii=False))
    return dict_file


class TestSynthesizeEndpoint:
    """拡張合成エンドポイントのテスト"""

    @patch("app.routers.synthesis.VoicevoxClient")
    @patch("app.routers.synthesis.get_settings")
    def test_synthesize_success(
        self, mock_settings, mock_client_class, client, mock_audio_query, tmp_path
    ):
        """正常系: 音声合成成功"""
        # 辞書ファイルを設定
        dict_file = tmp_path / "extended_dict.json"
        dict_file.write_text("[]")

        mock_settings_instance = MagicMock()
        mock_settings_instance.data_dir = str(tmp_path)
        mock_settings.return_value = mock_settings_instance

        # VOICEVOX クライアントをモック
        mock_client = AsyncMock()
        mock_client.create_audio_query = AsyncMock(return_value=mock_audio_query)
        mock_client.synthesis = AsyncMock(return_value=b"RIFF....WAV_DATA")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize",
            json={"text": "こんにちは、ずんだもんです", "speaker": 1}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert b"RIFF" in response.content

    @patch("app.routers.synthesis.VoicevoxClient")
    @patch("app.routers.synthesis.load_dictionary")
    def test_synthesize_with_dictionary_match(
        self, mock_load_dict, mock_client_class, client, mock_audio_query
    ):
        """正常系: 辞書マッチして上書き適用"""
        # 辞書をモック（「ズンダモン」を含む）
        mock_load_dict.return_value = [
            ExtendedDictEntry(
                word="ずんだもん",
                pronunciation="ズンダモン",
                accent_type=1,
                mora_count=5,
                pitch_values=[6.0, 6.1, 6.2, 6.3, 6.4],
                length_values=[0.15, 0.10, 0.15, 0.15, 0.12],
            )
        ]

        mock_client = AsyncMock()
        mock_client.create_audio_query = AsyncMock(return_value=mock_audio_query)
        mock_client.synthesis = AsyncMock(return_value=b"RIFF....WAV_DATA")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize",
            json={"text": "こんにちは、ずんだもんです", "speaker": 1}
        )

        assert response.status_code == 200
        # ヘッダーでマッチ数を確認
        assert "x-matches-found" in response.headers
        assert int(response.headers["x-matches-found"]) == 1

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_synthesize_voicevox_error(self, mock_client_class, client):
        """異常系: VOICEVOX Engine 接続エラー"""
        mock_client = AsyncMock()
        mock_client.create_audio_query = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize",
            json={"text": "テスト", "speaker": 1}
        )

        assert response.status_code == 503
        assert "VOICEVOX Engine is not available" in response.json()["detail"]

    def test_synthesize_invalid_request_empty_text(self, client):
        """異常系: 空のテキスト"""
        response = client.post(
            "/api/v1/synthesize",
            json={"text": "", "speaker": 1}
        )

        assert response.status_code == 422  # Validation error

    def test_synthesize_invalid_request_negative_speaker(self, client):
        """異常系: 負の話者ID"""
        response = client.post(
            "/api/v1/synthesize",
            json={"text": "テスト", "speaker": -1}
        )

        assert response.status_code == 422  # Validation error


class TestSynthesizeDebugEndpoint:
    """デバッグ用エンドポイントのテスト"""

    @patch("app.routers.synthesis.VoicevoxClient")
    @patch("app.routers.synthesis.get_settings")
    def test_synthesize_debug_returns_query(
        self, mock_settings, mock_client_class, client, mock_audio_query, tmp_path
    ):
        """正常系: デバッグエンドポイントが修正後のQueryを返す"""
        dict_file = tmp_path / "extended_dict.json"
        dict_file.write_text("[]")

        mock_settings_instance = MagicMock()
        mock_settings_instance.data_dir = str(tmp_path)
        mock_settings.return_value = mock_settings_instance

        mock_client = AsyncMock()
        mock_client.create_audio_query = AsyncMock(return_value=mock_audio_query)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize/debug",
            json={"text": "こんにちは", "speaker": 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "matches_found" in data
        assert "modified_query" in data
        assert data["modified_query"]["accent_phrases"] is not None


class TestSynthesisHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    @patch("app.routers.synthesis.VoicevoxClient")
    @patch("app.routers.synthesis.get_settings")
    def test_health_healthy(
        self, mock_settings, mock_client_class, client, tmp_path
    ):
        """正常系: ヘルスチェック成功"""
        dict_file = tmp_path / "extended_dict.json"
        dict_file.write_text("[]")

        mock_settings_instance = MagicMock()
        mock_settings_instance.data_dir = str(tmp_path)
        mock_settings.return_value = mock_settings_instance

        mock_client = AsyncMock()
        mock_client.get_version = AsyncMock(return_value="0.15.0")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["voicevox_version"] == "0.15.0"

    @patch("app.routers.synthesis.VoicevoxClient")
    @patch("app.routers.synthesis.get_settings")
    def test_health_unhealthy(
        self, mock_settings, mock_client_class, client, tmp_path
    ):
        """異常系: VOICEVOX Engine 接続失敗"""
        dict_file = tmp_path / "extended_dict.json"
        dict_file.write_text("[]")

        mock_settings_instance = MagicMock()
        mock_settings_instance.data_dir = str(tmp_path)
        mock_settings.return_value = mock_settings_instance

        mock_client = AsyncMock()
        mock_client.get_version = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.get("/api/v1/health")

        assert response.status_code == 200  # ヘルスチェックは常に200を返す
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data
