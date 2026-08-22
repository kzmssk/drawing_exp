"""ペン軌跡を蓄積するラスタキャンバス。

ワールド座標のペン先(x,y)を紙面上のテクセルへ写像し、連続サンプル間を線分で描く。
内部は PIL の RGB 画像(白背景・黒描線)。MuJoCo のキャンバステクスチャへ流し込む配列と、
保存用の縮小画像の双方を提供する。
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from drawing_exp.env.spec import CanvasSpec


class Canvas:
    def __init__(self, spec: CanvasSpec) -> None:
        self.spec = spec
        self._cx, self._cy = spec.center_xy
        self._half = spec.size_m / 2.0
        self._res = spec.raster_res
        self._img = Image.new("RGB", (self._res, self._res), (255, 255, 255))
        self._draw = ImageDraw.Draw(self._img)
        self._prev_px: tuple[int, int] | None = None

    def reset(self) -> None:
        self._img.paste((255, 255, 255), (0, 0, self._res, self._res))
        self._prev_px = None

    def _world_to_px(self, x: float, y: float) -> tuple[int, int] | None:
        """ワールド(x,y)→テクセル(col,row)。紙外なら None。"""
        u = (x - self._cx + self._half) / (2.0 * self._half)
        v = (y - self._cy + self._half) / (2.0 * self._half)
        if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0):
            return None
        col = int(round(u * (self._res - 1)))
        # +y が画像の上に来るよう v を反転。
        row = int(round((1.0 - v) * (self._res - 1)))
        return col, row

    def update(self, x: float, y: float, pen_down: bool = True) -> bool:
        """ペン先位置を1サンプル追加。描線したら True。

        紙外・ペンアップのときは軌跡を切って(prev をリセット)線を飛ばさない。
        """
        px = self._world_to_px(x, y) if pen_down else None
        if px is None:
            self._prev_px = None
            return False
        drew = False
        if self._prev_px is not None:
            self._draw.line(
                [self._prev_px, px],
                fill=(0, 0, 0),
                width=self.spec.stroke_width,
            )
            drew = True
        else:
            # 単発点も描いておく(太さ分の円)。
            r = self.spec.stroke_width // 2
            self._draw.ellipse(
                [px[0] - r, px[1] - r, px[0] + r, px[1] + r], fill=(0, 0, 0)
            )
        self._prev_px = px
        return drew

    def texture_rgb(self) -> np.ndarray:
        """MuJoCo テクスチャアップロード用の (res, res, 3) uint8 配列。"""
        return np.asarray(self._img, dtype=np.uint8)

    def to_image(self, res: int | None = None) -> np.ndarray:
        """保存用の縮小 RGB 画像 (res, res, 3) uint8。"""
        res = res or self.spec.image_res
        small = self._img.resize((res, res), Image.LANCZOS)
        return np.asarray(small, dtype=np.uint8)

    def coverage(self) -> float:
        """非白ピクセルの割合(描画被覆率)。"""
        arr = np.asarray(self._img)
        drawn = np.any(arr < 250, axis=-1)
        return float(drawn.mean())
