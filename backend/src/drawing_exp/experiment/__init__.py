"""実験成果物の契約(manifest)とファイルストア(store)。

閲覧・将来の実験遂行で共有する。実験は runs/<run_id>/ に出力し、任意で
config.json / metrics.json を置くだけで閲覧対象になる(疎結合な契約)。
"""

from __future__ import annotations

from drawing_exp.experiment.manifest import (
    CONFIG_FILENAME,
    METRICS_FILENAME,
    RunMetrics,
)
from drawing_exp.experiment.store import RunStore

__all__ = ["CONFIG_FILENAME", "METRICS_FILENAME", "RunMetrics", "RunStore"]
