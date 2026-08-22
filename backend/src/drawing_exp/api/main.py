"""FastAPI 最小アプリ: 環境確認用の /health のみ。

`uv run uvicorn drawing_exp.api.main:app` で起動する。
将来 ROOT_PLAN の configs / experiments / results ルーターをここに登録する。
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="drawing-exp")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
