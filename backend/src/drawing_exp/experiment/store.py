"""成果物ディレクトリを走査して run を発見する読み取り専用ストア。

`<runs_root>/<experiment>/runs/<run_id>/` を run とみなす。成果物は dir 内の
全ファイルを拡張子で分類するだけなので、別実験・別出力でも自動で閲覧対象になる。
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from drawing_exp.experiment.manifest import (
    CONFIG_FILENAME,
    METRICS_FILENAME,
    RunMetrics,
)

_SAFE_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")
_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
_VIDEO_EXT = {".mp4", ".webm", ".mov"}


class ArtifactKind(str, Enum):
    image = "image"
    video = "video"
    json = "json"
    other = "other"


class Artifact(BaseModel):
    """run 内の1成果物ファイル。rel_path は runs_root からの相対パス。"""

    name: str
    kind: ArtifactKind
    rel_path: str
    size_bytes: int


class RunSummary(BaseModel):
    """一覧表示用の run 要約。"""

    experiment: str
    run_id: str
    created_at: datetime
    metrics: RunMetrics | None
    artifact_count: int
    thumbnail_rel_path: str | None


class RunDetail(BaseModel):
    """詳細表示用の run 情報。"""

    experiment: str
    run_id: str
    created_at: datetime
    metrics: RunMetrics | None
    config: dict[str, Any] | None
    artifacts: list[Artifact]


def _default_runs_root() -> Path:
    env = os.environ.get("DRAWING_EXP_RUNS_ROOT")
    if env:
        return Path(env)
    # backend/src/drawing_exp/experiment/store.py -> backend/experiments
    return Path(__file__).resolve().parents[3] / "experiments"


def _classify(path: Path) -> ArtifactKind:
    ext = path.suffix.lower()
    if ext in _IMAGE_EXT:
        return ArtifactKind.image
    if ext in _VIDEO_EXT:
        return ArtifactKind.video
    if ext == ".json":
        return ArtifactKind.json
    return ArtifactKind.other


class RunStore:
    def __init__(self, runs_root: Path | None = None) -> None:
        self.runs_root = (runs_root or _default_runs_root()).resolve()

    def list_runs(self, experiment: str | None = None) -> list[RunSummary]:
        """全 run の要約を作成時刻の新しい順に返す。"""
        summaries: list[RunSummary] = []
        if not self.runs_root.is_dir():
            return summaries
        for exp_dir in sorted(self.runs_root.iterdir()):
            if not exp_dir.is_dir() or not _SAFE_NAME.match(exp_dir.name):
                continue
            if experiment is not None and exp_dir.name != experiment:
                continue
            runs_dir = exp_dir / "runs"
            if not runs_dir.is_dir():
                continue
            for run_dir in runs_dir.iterdir():
                if not run_dir.is_dir() or not _SAFE_NAME.match(run_dir.name):
                    continue
                summaries.append(self._summarize(exp_dir.name, run_dir))
        summaries.sort(key=lambda s: s.created_at, reverse=True)
        return summaries

    def get_run(self, experiment: str, run_id: str) -> RunDetail | None:
        """1 run の詳細。存在しなければ None。"""
        run_dir = self._safe_run_dir(experiment, run_id)
        if run_dir is None or not run_dir.is_dir():
            return None
        artifacts = self._artifacts(experiment, run_dir)
        return RunDetail(
            experiment=experiment,
            run_id=run_id,
            created_at=datetime.fromtimestamp(run_dir.stat().st_mtime),
            metrics=self._read_metrics(run_dir),
            config=self._read_json(run_dir / CONFIG_FILENAME),
            artifacts=artifacts,
        )

    def resolve_artifact(self, experiment: str, run_id: str, name: str) -> Path | None:
        """成果物ファイルの絶対パス。範囲外・不正名は None。"""
        run_dir = self._safe_run_dir(experiment, run_id)
        if run_dir is None or not _SAFE_NAME.match(name):
            return None
        path = (run_dir / name).resolve()
        if run_dir not in path.parents or not path.is_file():
            return None
        return path

    def _safe_run_dir(self, experiment: str, run_id: str) -> Path | None:
        if not (_SAFE_NAME.match(experiment) and _SAFE_NAME.match(run_id)):
            return None
        run_dir = (self.runs_root / experiment / "runs" / run_id).resolve()
        if self.runs_root not in run_dir.parents:
            return None
        return run_dir

    def _summarize(self, experiment: str, run_dir: Path) -> RunSummary:
        artifacts = self._artifacts(experiment, run_dir)
        thumb = next(
            (a.rel_path for a in artifacts if a.kind == ArtifactKind.image), None
        )
        return RunSummary(
            experiment=experiment,
            run_id=run_dir.name,
            created_at=datetime.fromtimestamp(run_dir.stat().st_mtime),
            metrics=self._read_metrics(run_dir),
            artifact_count=len(artifacts),
            thumbnail_rel_path=thumb,
        )

    def _artifacts(self, experiment: str, run_dir: Path) -> list[Artifact]:
        items: list[Artifact] = []
        for f in sorted(run_dir.iterdir()):
            if not f.is_file():
                continue
            rel = f"{experiment}/runs/{run_dir.name}/{f.name}"
            items.append(
                Artifact(
                    name=f.name,
                    kind=_classify(f),
                    rel_path=rel,
                    size_bytes=f.stat().st_size,
                )
            )
        return items

    def _read_metrics(self, run_dir: Path) -> RunMetrics | None:
        data = self._read_json(run_dir / METRICS_FILENAME)
        if data is None:
            return None
        try:
            return RunMetrics.model_validate(data)
        except ValueError:
            return None

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text())
        except (ValueError, OSError):
            return None
