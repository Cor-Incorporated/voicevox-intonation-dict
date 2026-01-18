from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dictionary, synthesis
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="VOICEVOX Intonation Dictionary Extension",
    description="VOICEVOX辞書機能を拡張し、イントネーション詳細を保存するAPIサーバー",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(dictionary.router, prefix="/api/v1/dictionary", tags=["dictionary"])
app.include_router(synthesis.router, prefix="/api/v1", tags=["synthesis"])


@app.get("/")
async def root():
    return {"message": "VOICEVOX Intonation Dictionary Extension API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
