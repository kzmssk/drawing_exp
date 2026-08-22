"""FastAPI アプリ。実験結果の閲覧API + 成果物配信。

起動: `uv run uvicorn drawing_exp.api.main:app --reload --port 8000`
将来 ROOT_PLAN の configs / experiments(実験遂行)ルーターをここに追加する。
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from drawing_exp.api.routers import results
from drawing_exp.experiment.store import RunStore

app = FastAPI(title="drawing-exp")

# dev: frontend(vite)から直接叩く場合に許可。通常は vite proxy 経由で同一オリジン。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(results.router)

# 成果物(画像・動画)を配信。StaticFiles は Range 要求に対応し mp4 のシークが効く。
app.mount(
    "/api/artifacts",
    StaticFiles(directory=str(RunStore().runs_root)),
    name="artifacts",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
