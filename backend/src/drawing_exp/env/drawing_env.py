"""MuJoCo 物理 + Canvas を束ねる描画環境。

CONCEPT の観測(描画像 I_t・身体状態 s_t・ペン ON/OFF)を返す Gym 的インタフェース。
今回のバブリング実験だけでなく、将来の World Model 学習でも再利用する。
"""

from __future__ import annotations

from dataclasses import dataclass

import mujoco
import numpy as np

from drawing_exp.env.arm import PEN_SITE, build_arm_xml
from drawing_exp.env.canvas import Canvas
from drawing_exp.env.spec import ArmSpec, CanvasSpec, SimSpec


@dataclass
class Observation:
    """1ステップの観測。"""

    image: np.ndarray  # I_t: キャンバス画像 (image_res, image_res, 3) uint8
    qpos: np.ndarray  # 関節角 [rad]
    qvel: np.ndarray  # 関節角速度 [rad/s]
    pen_xy: np.ndarray  # ペン先のワールド座標 (x, y) [m]
    pen_down: bool  # 接地して紙上にあるか
    drew: bool  # このステップで描線したか


class DrawingEnv:
    def __init__(
        self,
        arm: ArmSpec | None = None,
        canvas: CanvasSpec | None = None,
        sim: SimSpec | None = None,
    ) -> None:
        self.arm = arm or ArmSpec()
        self.canvas_spec = canvas or CanvasSpec()
        self.sim = sim or SimSpec()

        xml = build_arm_xml(self.arm, self.canvas_spec)
        self.model = mujoco.MjModel.from_xml_string(xml)
        # spec の dt を反映(XML 側とも一致させる)。
        self.model.opt.timestep = self.sim.dt
        self.data = mujoco.MjData(self.model)

        self.canvas = Canvas(self.canvas_spec)
        self._pen_site_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_SITE, PEN_SITE
        )
        self._step_count = 0

    @property
    def nu(self) -> int:
        """アクチュエータ数(=関節数)。"""
        return self.model.nu

    def reset(self) -> Observation:
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)
        self.canvas.reset()
        self._step_count = 0
        # 初期ペン位置を1点だけ描いておく。
        x, y = self._pen_xy()
        drew = self.canvas.update(x, y, pen_down=True)
        return self._observe(pen_down=True, drew=drew)

    def step(self, torque: np.ndarray) -> Observation:
        """関節トルクを与えて1ステップ進め、観測を返す。"""
        self.data.ctrl[:] = np.asarray(torque, dtype=np.float64)[: self.nu]
        mujoco.mj_step(self.model, self.data)
        self._step_count += 1
        x, y = self._pen_xy()
        # 今回は平面・ペン常時接地。将来はここで z 高さから ON/OFF を判定する。
        pen_down = True
        drew = self.canvas.update(x, y, pen_down=pen_down)
        return self._observe(pen_down=pen_down, drew=drew)

    def _pen_xy(self) -> tuple[float, float]:
        pos = self.data.site_xpos[self._pen_site_id]
        return float(pos[0]), float(pos[1])

    def _observe(self, pen_down: bool, drew: bool) -> Observation:
        return Observation(
            image=self.canvas.to_image(),
            qpos=self.data.qpos.copy(),
            qvel=self.data.qvel.copy(),
            pen_xy=np.array(self._pen_xy()),
            pen_down=pen_down,
            drew=drew,
        )
