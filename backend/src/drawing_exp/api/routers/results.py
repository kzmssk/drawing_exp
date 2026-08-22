"""実験結果の閲覧エンドポイント(run 一覧・詳細)。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from drawing_exp.api.schemas import RunDetailOut, RunSummaryOut
from drawing_exp.experiment.store import RunStore

router = APIRouter(prefix="/api", tags=["results"])
_store = RunStore()


@router.get("/runs")
def list_runs(experiment: str | None = None) -> list[RunSummaryOut]:
    """run 一覧(新しい順、任意で experiment 絞り込み)。"""
    return [RunSummaryOut.from_summary(s) for s in _store.list_runs(experiment)]


@router.get("/runs/{experiment}/{run_id}")
def get_run(experiment: str, run_id: str) -> RunDetailOut:
    """run 詳細(config・metrics・成果物一覧)。"""
    detail = _store.get_run(experiment, run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunDetailOut.from_detail(detail)
