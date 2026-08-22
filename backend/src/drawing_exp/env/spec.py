"""環境仕様(pydantic)。5歳児スペックなど調整対象のパラメータをここに集約する。

数値はすべて「文書化した仮定」であり、実機データではない。調整はこのファイルで完結する。
5歳児の身体諸元(概算): 身長約110cm・体重約18kg。片腕質量は体重の約2.7%(≈0.5kg)。
片腕長は約0.45m(上腕>前腕>手)。関節トルクは成人よりはるかに小さい。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArmSpec(BaseModel):
    """平面4自由度アーム(肩・肘・手首・手)の諸元。

    すべての関節は鉛直軸(z)まわりのヒンジで、リンクは水平面内を動く(平面アーム)。
    ペン先は最終リンク先端から紙面(z=0)へ降ろした固定長のペンで、常に接地する。
    """

    # リンク長 [m]: 肩→上腕, 肘→前腕, 手首→手, 手→ペンホルダ。合計 ≈ 0.48m。
    link_lengths: tuple[float, float, float, float] = (0.20, 0.16, 0.08, 0.04)
    # リンク質量 [kg]: 合計 ≈ 0.5kg(5歳片腕相当)。先端ほど軽い。
    link_masses: tuple[float, float, float, float] = (0.25, 0.15, 0.06, 0.02)
    # リンク半径 [m]: 見た目/衝突用のカプセル半径(先端ほど細く)。
    link_radii: tuple[float, float, float, float] = (0.022, 0.018, 0.014, 0.010)
    # 各関節トルク上限 [N·m]: 5歳児想定の小さい値。actuator ctrlrange = ±この値。
    torque_limits: tuple[float, float, float, float] = (1.5, 1.0, 0.4, 0.2)
    # 関節ダンピング [N·m·s/rad]: dt=0.2 の大ステップを安定化(Euler陰的減衰)。
    joint_damping: tuple[float, float, float, float] = (0.15, 0.10, 0.05, 0.02)
    # 関節アーマチュア(等価回転慣性) [kg·m^2]: 数値安定化のため微小量を付与。
    joint_armature: tuple[float, float, float, float] = (0.010, 0.008, 0.005, 0.003)
    # リンクを紙面から浮かせる高さ [m](リンクが紙面に食い込まないように)。
    link_height: float = 0.03
    # ペン先の描画半径 [m](太さ)。
    pen_radius: float = 0.006


class CanvasSpec(BaseModel):
    """紙(キャンバス)の物理サイズと解像度。"""

    # 紙の中心座標 [m](アーム基部は原点、+x方向に紙を置く)。
    center_xy: tuple[float, float] = (0.22, 0.0)
    # 紙の一辺 [m](正方形)。5歳児が描く範囲を想定。
    size_m: float = 0.30
    # 内部ラスタ解像度 [px](動画のテクスチャ品質用。正方形)。
    raster_res: int = 512
    # 保存する描画像の解像度 [px]。
    image_res: int = 128
    # 描線の太さ [px](内部ラスタ基準)。
    stroke_width: int = Field(default=6, ge=1)


class SimSpec(BaseModel):
    """時間・ステップの仕様。物理精度より計算効率を優先する。"""

    # 1エピソードのステップ数。
    n_steps: int = 300
    # 1エピソードの実時間 [s]。
    duration_s: float = 60.0

    @property
    def dt(self) -> float:
        """1ステップの時間 [s] = duration_s / n_steps (= 0.2s)。"""
        return self.duration_s / self.n_steps
