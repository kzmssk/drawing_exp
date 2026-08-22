"""実験成果物ディレクトリの共通契約(ファイル名と metrics スキーマ)。"""

from __future__ import annotations

from pydantic import BaseModel

# run ディレクトリに置く既知ファイル名(実験の書き込みと store の読み取りで共有)。
CONFIG_FILENAME = "config.json"
METRICS_FILENAME = "metrics.json"


class RunMetrics(BaseModel):
    """1エピソードの要約指標。実験横断で使う最小の共通項目。"""

    n_steps: int
    duration_s: float
    coverage: float  # 描画被覆率(非白ピクセル割合)
    pen_path_len_m: float  # ペン移動距離 [m]
    stable: bool  # qpos/qvel に NaN が無いか
