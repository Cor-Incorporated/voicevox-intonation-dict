import httpx
from typing import Dict, Any, List
from app.config import get_settings

settings = get_settings()


class VoicevoxClient:
    """VOICEVOX Engineとの通信クライアント"""
    
    def __init__(self):
        self.base_url = settings.voicevox_engine_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_version(self) -> str:
        """バージョン情報を取得"""
        response = await self.client.get(f"{self.base_url}/version")
        response.raise_for_status()
        return response.text.strip('"')
    
    async def get_speakers(self) -> List[Dict[str, Any]]:
        """話者一覧を取得"""
        response = await self.client.get(f"{self.base_url}/speakers")
        response.raise_for_status()
        return response.json()
    
    async def create_audio_query(self, text: str, speaker: int) -> Dict[str, Any]:
        """AudioQueryを作成"""
        response = await self.client.post(
            f"{self.base_url}/audio_query",
            params={"text": text, "speaker": speaker}
        )
        response.raise_for_status()
        return response.json()
    
    async def synthesis(self, audio_query: Dict[str, Any], speaker: int) -> bytes:
        """音声合成を実行"""
        response = await self.client.post(
            f"{self.base_url}/synthesis",
            params={"speaker": speaker},
            json=audio_query
        )
        response.raise_for_status()
        return response.content
    
    async def close(self):
        """クライアントをクローズ"""
        await self.client.aclose()
