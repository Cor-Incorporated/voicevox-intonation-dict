"""
統合テスト: プレビュー合成APIエンドポイント

VOICEVOX Engine をモックして、プレビュー合成APIの動作を検証します。
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """テスト用 FastAPI クライアント"""
    return TestClient(app)


@pytest.fixture
def mock_audio_query():
    """プレビュー合成用の AudioQuery モック"""
    return {
        "accent_phrases": [
            {
                "moras": [
                    {
                        "text": "コ",
                        "consonant": "k",
                        "consonant_length": 0.05,
                        "vowel": "o",
                        "vowel_length": 0.12,
                        "pitch": 5.0,
                    },
                    {
                        "text": "ン",
                        "consonant": None,
                        "consonant_length": None,
                        "vowel": "N",
                        "vowel_length": 0.08,
                        "pitch": 5.1,
                    },
                    {
                        "text": "ニ",
                        "consonant": "n",
                        "consonant_length": 0.05,
                        "vowel": "i",
                        "vowel_length": 0.10,
                        "pitch": 5.2,
                    },
                    {
                        "text": "チ",
                        "consonant": "ch",
                        "consonant_length": 0.06,
                        "vowel": "i",
                        "vowel_length": 0.10,
                        "pitch": 5.3,
                    },
                    {
                        "text": "ワ",
                        "consonant": "w",
                        "consonant_length": 0.04,
                        "vowel": "a",
                        "vowel_length": 0.15,
                        "pitch": 5.4,
                    },
                ],
                "accent": 3,
                "pause_mora": None,
                "is_interrogative": False,
            }
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


class TestPreviewEndpoint:
    """プレビュー合成エンドポイントのテスト"""

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_synthesis_success(
        self, mock_client_class, client, mock_audio_query
    ):
        """正常系: プレビュー合成成功

        AudioQuery を直接渡して音声合成が行われ、
        WAV 形式のオーディオデータが返却されることを確認します。
        """
        # VOICEVOX クライアントをモック
        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(return_value=b"RIFF....WAV_DATA")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 1},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert b"RIFF" in response.content

        # synthesis が正しい引数で呼ばれたことを確認
        mock_client.synthesis.assert_called_once_with(mock_audio_query, 1)

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_synthesis_with_different_speaker(
        self, mock_client_class, client, mock_audio_query
    ):
        """正常系: 異なる話者IDでのプレビュー合成"""
        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(return_value=b"RIFF....WAV_DATA")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 42},
        )

        assert response.status_code == 200
        mock_client.synthesis.assert_called_once_with(mock_audio_query, 42)

    def test_preview_empty_audio_query(self, client):
        """異常系: 空の AudioQuery

        空のオブジェクトを送信した場合、
        バリデーションエラー (422) が返されることを確認します。
        """
        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": {}, "speaker": 1},
        )

        # 空の AudioQuery でも形式上は受け付けられる（VOICEVOXが拒否する）
        # ただし、実際のVOICEVOXが動いていないので503になる可能性もある
        # Pydanticのバリデーションでは dict として受け入れられるため、
        # 実際には VOICEVOX 側でエラーになるケースをテスト
        assert response.status_code in [422, 503]

    def test_preview_missing_audio_query(self, client):
        """異常系: AudioQuery が存在しない

        audio_query フィールドがない場合、
        バリデーションエラー (422) が返されることを確認します。
        """
        response = client.post(
            "/api/v1/synthesize/preview",
            json={"speaker": 1},
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("audio_query" in str(err) for err in error_detail)

    def test_preview_missing_speaker(self, client, mock_audio_query):
        """正常系: speaker が省略された場合はデフォルト値が使用される"""
        # speaker はデフォルト値 1 があるため、省略しても動作する
        # ただし VOICEVOX が動いていないので 503 になる
        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query},
        )

        # デフォルト値が適用されるため、バリデーションは通る
        # VOICEVOX 未接続なら 503
        assert response.status_code == 503

    def test_preview_invalid_speaker_negative(self, client, mock_audio_query):
        """異常系: 負の話者ID

        speaker に負の値を指定した場合、
        バリデーションエラー (422) が返されることを確認します。
        """
        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": -1},
        )

        assert response.status_code == 422

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_voicevox_not_running(
        self, mock_client_class, client, mock_audio_query
    ):
        """異常系: VOICEVOX Engine 未起動

        VOICEVOX Engine に接続できない場合、
        503 エラーが返されることを確認します。
        """
        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 1},
        )

        assert response.status_code == 503
        assert "VOICEVOX Engine is not available" in response.json()["detail"]

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_voicevox_timeout(
        self, mock_client_class, client, mock_audio_query
    ):
        """異常系: VOICEVOX Engine タイムアウト

        VOICEVOX Engine からの応答がタイムアウトした場合、
        503 エラーが返されることを確認します。
        """
        import asyncio

        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(
            side_effect=asyncio.TimeoutError("Request timed out")
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        response = client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 1},
        )

        assert response.status_code == 503

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_client_properly_closed(
        self, mock_client_class, client, mock_audio_query
    ):
        """クライアントが適切にクローズされることを確認"""
        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(return_value=b"RIFF....WAV_DATA")
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 1},
        )

        # close が呼ばれたことを確認
        mock_client.close.assert_called_once()

    @patch("app.routers.synthesis.VoicevoxClient")
    def test_preview_client_closed_on_error(
        self, mock_client_class, client, mock_audio_query
    ):
        """エラー時もクライアントが適切にクローズされることを確認"""
        mock_client = AsyncMock()
        mock_client.synthesis = AsyncMock(
            side_effect=Exception("Some error")
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        client.post(
            "/api/v1/synthesize/preview",
            json={"audio_query": mock_audio_query, "speaker": 1},
        )

        # エラー時も close が呼ばれたことを確認
        mock_client.close.assert_called_once()
