# patterns.md - 再利用パターン

## API パターン

### FastAPI ルーター構成
```python
# routers/xxx.py
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/xxx", tags=["xxx"])

@router.get("/")
async def list_items() -> List[ItemModel]:
    pass

@router.post("/")
async def create_item(item: CreateItemRequest) -> ItemModel:
    pass

@router.get("/{item_id}")
async def get_item(item_id: str) -> ItemModel:
    pass
```

### サービス層構成
```python
# services/xxx_service.py
class XxxService:
    def __init__(self):
        pass

    def process(self, data: InputModel) -> OutputModel:
        """
        ビジネスロジックをここに実装。

        Args:
            data: 入力データ

        Returns:
            処理結果

        Raises:
            ValueError: 不正な入力の場合
        """
        pass
```

---

## VOICEVOX 連携パターン

### AudioQuery 取得
```python
async def get_audio_query(text: str, speaker: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": speaker}
        )
        response.raise_for_status()
        return response.json()
```

### 音声合成
```python
async def synthesize(audio_query: dict, speaker: int) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": speaker},
            json=audio_query
        )
        response.raise_for_status()
        return response.content
```

---

## テストパターン

### pytest フィクスチャ
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_audio_query():
    return {
        "accent_phrases": [
            {
                "moras": [
                    {"text": "ズ", "pitch": 5.0, "vowel_length": 0.1},
                    {"text": "ン", "pitch": 5.5, "vowel_length": 0.1}
                ],
                "accent": 1
            }
        ]
    }
```

---

## エラーハンドリングパターン

```python
from fastapi import HTTPException

# 404 Not Found
raise HTTPException(status_code=404, detail="Item not found")

# 400 Bad Request
raise HTTPException(status_code=400, detail="Invalid input")

# 503 Service Unavailable (VOICEVOX Engine 接続エラー)
raise HTTPException(
    status_code=503,
    detail="VOICEVOX Engine is not available"
)
```
