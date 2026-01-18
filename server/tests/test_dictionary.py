"""
統合テスト: 辞書APIエンドポイント

辞書のCRUD操作（取得・追加・更新・削除）の動作を検証します。
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.extended_dict import ExtendedDictEntry


@pytest.fixture
def client() -> TestClient:
    """テスト用 FastAPI クライアント"""
    return TestClient(app)


@pytest.fixture
def temp_dict_dir(tmp_path: Path) -> Path:
    """一時的な辞書ディレクトリを作成"""
    return tmp_path


@pytest.fixture
def empty_dict_file(temp_dict_dir: Path) -> Path:
    """空の辞書ファイルを作成"""
    dict_file = temp_dict_dir / "extended_dict.json"
    dict_file.write_text("[]", encoding="utf-8")
    return dict_file


@pytest.fixture
def populated_dict_file(temp_dict_dir: Path) -> Path:
    """データ入りの辞書ファイルを作成"""
    dict_file = temp_dict_dir / "extended_dict.json"
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
        },
        {
            "word": "めたん",
            "pronunciation": "メタン",
            "accent_type": 0,
            "mora_count": 3,
            "pitch_values": [5.0, 5.1, 5.2],
            "length_values": [0.12, 0.10, 0.12],
            "speaker_id": 1,
            "accent_phrases": None,
        },
    ]
    dict_file.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return dict_file


def create_valid_entry() -> dict[str, Any]:
    """有効な辞書エントリを作成するヘルパー"""
    return {
        "word": "テスト",
        "pronunciation": "テスト",
        "accent_type": 1,
        "mora_count": 3,
        "pitch_values": [5.0, 5.1, 5.2],
        "length_values": [0.12, 0.10, 0.12],
    }


class TestGetDictionary:
    """辞書一覧取得エンドポイントのテスト"""

    def test_get_dictionary_empty(
        self, client: TestClient, empty_dict_file: Path
    ) -> None:
        """正常系: 空の辞書を取得"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = empty_dict_file

            response = client.get("/api/v1/dictionary/")

            assert response.status_code == 200
            data = response.json()
            assert data == {"entries": [], "total": 0}

    def test_get_dictionary_with_entries(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """正常系: データありの辞書を取得"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            response = client.get("/api/v1/dictionary/")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["entries"]) == 2

            # エントリの内容を検証
            words = [entry["word"] for entry in data["entries"]]
            assert "ずんだもん" in words
            assert "めたん" in words

    def test_get_dictionary_file_not_exists(
        self, client: TestClient, temp_dict_dir: Path
    ) -> None:
        """正常系: 辞書ファイルが存在しない場合は空リストを返す"""
        non_existent_path = temp_dict_dir / "non_existent.json"

        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = non_existent_path

            response = client.get("/api/v1/dictionary/")

            assert response.status_code == 200
            data = response.json()
            assert data == {"entries": [], "total": 0}


class TestAddEntry:
    """辞書エントリ追加エンドポイントのテスト"""

    def test_add_entry_success(
        self, client: TestClient, empty_dict_file: Path
    ) -> None:
        """正常系: 新規エントリを追加"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = empty_dict_file

            entry = create_valid_entry()
            response = client.post("/api/v1/dictionary/", json=entry)

            assert response.status_code == 200
            data = response.json()
            assert data["word"] == entry["word"]
            assert data["pronunciation"] == entry["pronunciation"]
            assert data["accent_type"] == entry["accent_type"]

            # ファイルに保存されていることを確認
            saved_data = json.loads(empty_dict_file.read_text(encoding="utf-8"))
            assert len(saved_data) == 1
            assert saved_data[0]["word"] == entry["word"]

    def test_add_entry_upsert_existing(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """正常系: 既存エントリを上書き（upsert）"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            # 既存の「ずんだもん」を更新するエントリ
            updated_entry = {
                "word": "ずんだもん",
                "pronunciation": "ズンダモン",
                "accent_type": 2,  # 変更
                "mora_count": 5,
                "pitch_values": [7.0, 7.1, 7.2, 7.3, 7.4],  # 変更
                "length_values": [0.20, 0.15, 0.20, 0.20, 0.18],  # 変更
            }

            response = client.post("/api/v1/dictionary/", json=updated_entry)

            assert response.status_code == 200
            data = response.json()
            assert data["word"] == "ずんだもん"
            assert data["accent_type"] == 2
            assert data["pitch_values"] == [7.0, 7.1, 7.2, 7.3, 7.4]

            # ファイル内のエントリ数が増えていないことを確認（上書きされた）
            saved_data = json.loads(populated_dict_file.read_text(encoding="utf-8"))
            assert len(saved_data) == 2  # 元の2件のまま

            # 上書きされた内容を確認
            zundamon_entry = next(e for e in saved_data if e["word"] == "ずんだもん")
            assert zundamon_entry["accent_type"] == 2

    def test_add_entry_empty_word_validation_error(self, client: TestClient) -> None:
        """異常系: 空のwordでバリデーションエラー"""
        entry = {
            "word": "",  # 空文字
            "pronunciation": "テスト",
            "accent_type": 1,
        }

        response = client.post("/api/v1/dictionary/", json=entry)

        assert response.status_code == 422

    def test_add_entry_missing_required_fields(self, client: TestClient) -> None:
        """異常系: 必須フィールドが欠けている"""
        entry = {
            "word": "テスト",
            # pronunciation と accent_type が欠けている
        }

        response = client.post("/api/v1/dictionary/", json=entry)

        assert response.status_code == 422

    def test_add_entry_minimal_fields(
        self, client: TestClient, empty_dict_file: Path
    ) -> None:
        """正常系: 最小限の必須フィールドのみで追加"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = empty_dict_file

            entry = {
                "word": "テスト",
                "pronunciation": "テスト",
                "accent_type": 1,
            }

            response = client.post("/api/v1/dictionary/", json=entry)

            assert response.status_code == 200
            data = response.json()
            assert data["word"] == "テスト"
            assert data["pronunciation"] == "テスト"
            assert data["accent_type"] == 1
            # オプションフィールドはNone
            assert data["mora_count"] is None
            assert data["pitch_values"] is None


class TestDeleteEntry:
    """辞書エントリ削除エンドポイントのテスト"""

    def test_delete_entry_success(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """正常系: エントリを削除"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            response = client.delete("/api/v1/dictionary/ずんだもん")

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "ずんだもん" in data["message"]

            # ファイルから削除されていることを確認
            saved_data = json.loads(populated_dict_file.read_text(encoding="utf-8"))
            assert len(saved_data) == 1
            assert saved_data[0]["word"] == "めたん"

    def test_delete_entry_not_found(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """異常系: 存在しないエントリの削除で404エラー"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            response = client.delete("/api/v1/dictionary/存在しない単語")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert data["detail"] == "Entry not found"

    def test_delete_entry_empty_dictionary(
        self, client: TestClient, empty_dict_file: Path
    ) -> None:
        """異常系: 空の辞書から削除しようとすると404エラー"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = empty_dict_file

            response = client.delete("/api/v1/dictionary/テスト")

            assert response.status_code == 404


class TestSearchDictionary:
    """辞書検索エンドポイントのテスト"""

    def test_search_found(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """正常系: 検索で見つかる"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            response = client.get("/api/v1/dictionary/search?word=ずんだもん")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["entries"]) == 1
            assert data["entries"][0]["word"] == "ずんだもん"

    def test_search_not_found(
        self, client: TestClient, populated_dict_file: Path
    ) -> None:
        """正常系: 検索で見つからない"""
        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = populated_dict_file

            response = client.get("/api/v1/dictionary/search?word=存在しない")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["entries"]) == 0


class TestDictionaryIntegration:
    """辞書APIの統合テスト（CRUD操作の連携）"""

    def test_crud_workflow(
        self, client: TestClient, temp_dict_dir: Path
    ) -> None:
        """統合テスト: Create -> Read -> Update -> Delete の一連の流れ"""
        dict_file = temp_dict_dir / "extended_dict.json"

        with patch("app.routers.dictionary.get_dict_path") as mock_get_path:
            mock_get_path.return_value = dict_file

            # 1. 初期状態は空（ファイルが存在しない）
            response = client.get("/api/v1/dictionary/")
            assert response.status_code == 200
            assert response.json()["total"] == 0

            # 2. 新規追加
            entry = {
                "word": "四国めたん",
                "pronunciation": "シコクメタン",
                "accent_type": 0,
                "mora_count": 5,
            }
            response = client.post("/api/v1/dictionary/", json=entry)
            assert response.status_code == 200

            # 3. 追加後の確認
            response = client.get("/api/v1/dictionary/")
            assert response.status_code == 200
            assert response.json()["total"] == 1

            # 4. 検索で確認
            response = client.get("/api/v1/dictionary/search?word=四国めたん")
            assert response.status_code == 200
            assert response.json()["total"] == 1

            # 5. 更新（upsert）
            updated_entry = {
                "word": "四国めたん",
                "pronunciation": "シコクメタン",
                "accent_type": 1,  # 変更
                "mora_count": 5,
            }
            response = client.post("/api/v1/dictionary/", json=updated_entry)
            assert response.status_code == 200
            assert response.json()["accent_type"] == 1

            # 6. 更新後もエントリ数は変わらない
            response = client.get("/api/v1/dictionary/")
            assert response.status_code == 200
            assert response.json()["total"] == 1

            # 7. 削除
            response = client.delete("/api/v1/dictionary/四国めたん")
            assert response.status_code == 200

            # 8. 削除後は空
            response = client.get("/api/v1/dictionary/")
            assert response.status_code == 200
            assert response.json()["total"] == 0
