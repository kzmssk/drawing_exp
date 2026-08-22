"""バブリング(殴り描き)実験。

決められたステップ数(=一定時間)をランダムトルクで動かし、以下を出力する。
  - drawing.png          : 描かれた画像 (128x128)
  - drawing_topdown.mp4  : 描画過程の動画 (真上カメラ, 512x512)
  - external.mp4         : 描画過程をそとから見た動画 (斜め俯瞰カメラ, 512x512)
  - config.json          : 実験設定(再現用)

実行:  uv run python experiments/babbling/run.py
共通ライブラリ(drawing_exp)を import するだけの薄い層で、実験は1ディレクトリで完結する。
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# このスクリプトのディレクトリを import パスに追加(config を隣から読む)。
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import BabblingConfig  # noqa: E402

from drawing_exp.env import DrawingEnv  # noqa: E402
from drawing_exp.experiment import METRICS_FILENAME, RunMetrics  # noqa: E402
from drawing_exp.render import SceneRenderer, VideoWriter, save_png  # noqa: E402

RUNS_DIR = Path(__file__).resolve().parent / "runs"


def run(cfg: BabblingConfig) -> Path:
    out_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    env = DrawingEnv(arm=cfg.arm, canvas=cfg.canvas, sim=cfg.sim)
    renderer = SceneRenderer(env.model, cfg.video_res, cfg.video_res)
    rng = np.random.default_rng(cfg.seed)
    limits = np.array(env.arm.torque_limits) * cfg.torque_scale

    topdown = VideoWriter(out_dir / "drawing_topdown.mp4", fps=cfg.fps)
    external = VideoWriter(out_dir / "external.mp4", fps=cfg.fps)

    obs = env.reset()
    prev_xy = obs.pen_xy.copy()
    path_len = 0.0
    torque = rng.uniform(-limits, limits)

    for step in range(cfg.sim.n_steps):
        if step % cfg.hold_steps == 0:
            torque = rng.uniform(-limits, limits)
        obs = env.step(torque)

        path_len += float(np.linalg.norm(obs.pen_xy - prev_xy))
        prev_xy = obs.pen_xy.copy()

        # 描線をキャンバステクスチャへ反映してから両カメラで撮る。
        renderer.upload_canvas(env.canvas.texture_rgb())
        topdown.add(renderer.render(env.data, "topdown"))
        external.add(renderer.render(env.data, "external"))

    save_png(out_dir / "drawing.png", env.canvas.to_image())
    topdown.close()
    external.close()
    renderer.close()

    (out_dir / "config.json").write_text(cfg.model_dump_json(indent=2))

    stable = bool(np.all(np.isfinite(obs.qpos)) and np.all(np.isfinite(obs.qvel)))
    metrics = RunMetrics(
        n_steps=cfg.sim.n_steps,
        duration_s=cfg.sim.duration_s,
        coverage=env.canvas.coverage(),
        pen_path_len_m=path_len,
        stable=stable,
    )
    (out_dir / METRICS_FILENAME).write_text(metrics.model_dump_json(indent=2))
    print(f"出力先: {out_dir}")
    print(f"  drawing.png         (128x128)  被覆率 {env.canvas.coverage():.3f}")
    print(f"  drawing_topdown.mp4 ({cfg.video_res}x{cfg.video_res}, {topdown.frame_count}フレーム)")
    print(f"  external.mp4        ({cfg.video_res}x{cfg.video_res}, {external.frame_count}フレーム)")
    print(f"  ペン移動距離 {path_len:.3f} m / 安定(NaN無し): {stable}")
    return out_dir


if __name__ == "__main__":
    run(BabblingConfig())
