"""共通シミュレーション土台: MuJoCo 平面アーム + ラスタキャンバス。

実験横断で再利用する。実験固有のロジックは backend/experiments/<name>/ 側に置く。
"""

from __future__ import annotations

from drawing_exp.env.canvas import Canvas
from drawing_exp.env.drawing_env import DrawingEnv, Observation
from drawing_exp.env.spec import ArmSpec, CanvasSpec, SimSpec

__all__ = [
    "ArmSpec",
    "CanvasSpec",
    "SimSpec",
    "Canvas",
    "DrawingEnv",
    "Observation",
]
