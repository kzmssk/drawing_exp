"""バブリング実験の設定。

共通ライブラリの spec を合成し、実験固有パラメータ(乱数トルクの強さ・保持長・録画設定)
を足す。config 一枚で1実験を再現できるよう、run 時に config.json として保存する。
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from drawing_exp.env.spec import ArmSpec, CanvasSpec, SimSpec


class BabblingConfig(BaseModel):
    arm: ArmSpec = Field(default_factory=ArmSpec)
    canvas: CanvasSpec = Field(default_factory=CanvasSpec)
    sim: SimSpec = Field(default_factory=SimSpec)

    # 乱数シード(再現用)。
    seed: int = 0
    # トルクの強さ(各関節の上限に対する倍率, 0〜1)。
    torque_scale: float = 1.0
    # 同じ乱数トルクを保持するステップ数(大きいほど滑らかな軌跡)。
    hold_steps: int = 5

    # 動画解像度 [px](正方形)。
    video_res: int = 512
    # 動画フレームレート。300フレームを fps で再生(既定30 → 約10秒)。
    fps: int = 30
