"""MuJoCo シーンの録画と、キャンバスへの描線反映。

SceneRenderer は毎フレーム描線ラスタをキャンバステクスチャへアップロードしてから
指定カメラで描画する。これにより topdown / external の両カメラに描画過程が映る。
"""

from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import mujoco
import numpy as np

from drawing_exp.env.arm import CANVAS_TEXTURE


class SceneRenderer:
    """指定解像度でシーンを描画し、キャンバステクスチャを実行時更新する。"""

    def __init__(self, model: mujoco.MjModel, width: int = 512, height: int = 512) -> None:
        self.model = model
        self.renderer = mujoco.Renderer(model, height, width)
        self.texid = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_TEXTURE, CANVAS_TEXTURE
        )
        # Renderer 内部の GL / MjrContext(テクスチャアップロードに必要)。
        self._ctx = getattr(self.renderer, "_mjr_context", None)
        self._gl = getattr(self.renderer, "_gl_context", None)

    def upload_canvas(self, raster: np.ndarray) -> None:
        """描線ラスタ (H, W, 3) uint8 をキャンバステクスチャへ流し込む。

        テクスチャサイズと同一形状を前提(spec.raster_res でXMLと一致させている)。
        """
        if self.texid < 0 or self._ctx is None:
            return
        adr = int(self.model.tex_adr[self.texid])
        flat = np.ascontiguousarray(raster, dtype=np.uint8).reshape(-1)
        self.model.tex_data[adr : adr + flat.size] = flat
        if self._gl is not None:
            self._gl.make_current()
        mujoco.mjr_uploadTexture(self.model, self._ctx, self.texid)

    def render(self, data: mujoco.MjData, camera: str) -> np.ndarray:
        """指定カメラで1フレーム描画して (H, W, 3) uint8 を返す。"""
        self.renderer.update_scene(data, camera=camera)
        return self.renderer.render()

    def close(self) -> None:
        self.renderer.close()


class VideoWriter:
    """imageio(同梱ffmpeg)で mp4 を書き出す薄いラッパ。"""

    def __init__(self, path: str | Path, fps: int = 30) -> None:
        self.path = str(path)
        self._writer = imageio.get_writer(
            self.path, fps=fps, codec="libx264", macro_block_size=None
        )
        self._count = 0

    def add(self, frame: np.ndarray) -> None:
        self._writer.append_data(np.ascontiguousarray(frame, dtype=np.uint8))
        self._count += 1

    @property
    def frame_count(self) -> int:
        return self._count

    def close(self) -> None:
        self._writer.close()

    def __enter__(self) -> "VideoWriter":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def save_png(path: str | Path, image: np.ndarray) -> None:
    """RGB 画像 (H, W, 3) uint8 を PNG 保存する。"""
    imageio.imwrite(str(path), np.ascontiguousarray(image, dtype=np.uint8))
