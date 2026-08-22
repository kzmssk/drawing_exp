"""API 応答スキーマ。store の内部モデルに成果物URLを付与して返す。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from drawing_exp.experiment.manifest import RunMetrics
from drawing_exp.experiment.store import (
    Artifact,
    ArtifactKind,
    RunDetail,
    RunSummary,
)

# StaticFiles のマウント先。rel_path を URL へ変換する接頭辞。
ARTIFACTS_PREFIX = "/api/artifacts"


def _artifact_url(rel_path: str) -> str:
    return f"{ARTIFACTS_PREFIX}/{rel_path}"


class ArtifactInfo(BaseModel):
    name: str
    kind: ArtifactKind
    url: str
    size_bytes: int

    @classmethod
    def from_artifact(cls, a: Artifact) -> "ArtifactInfo":
        return cls(
            name=a.name, kind=a.kind, url=_artifact_url(a.rel_path), size_bytes=a.size_bytes
        )


class RunSummaryOut(BaseModel):
    experiment: str
    run_id: str
    created_at: datetime
    metrics: RunMetrics | None
    artifact_count: int
    thumbnail_url: str | None

    @classmethod
    def from_summary(cls, s: RunSummary) -> "RunSummaryOut":
        thumb = _artifact_url(s.thumbnail_rel_path) if s.thumbnail_rel_path else None
        return cls(
            experiment=s.experiment,
            run_id=s.run_id,
            created_at=s.created_at,
            metrics=s.metrics,
            artifact_count=s.artifact_count,
            thumbnail_url=thumb,
        )


class RunDetailOut(BaseModel):
    experiment: str
    run_id: str
    created_at: datetime
    metrics: RunMetrics | None
    config: dict[str, Any] | None
    artifacts: list[ArtifactInfo]

    @classmethod
    def from_detail(cls, d: RunDetail) -> "RunDetailOut":
        return cls(
            experiment=d.experiment,
            run_id=d.run_id,
            created_at=d.created_at,
            metrics=d.metrics,
            config=d.config,
            artifacts=[ArtifactInfo.from_artifact(a) for a in d.artifacts],
        )
