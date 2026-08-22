"""環境スモークテスト: 主要ライブラリの import と極小の動作確認。

`uv run python -m drawing_exp.smoke` で実行する。
研究ロジックは含まず、依存が正しく入っているかだけを確認する。
"""

from __future__ import annotations


def main() -> None:
    import numpy as np
    import torch
    import mujoco

    print(f"numpy  {np.__version__}")
    print(f"torch  {torch.__version__}")
    print(f"mujoco {mujoco.__version__}")

    # numpy: 配列演算
    a = np.arange(6).reshape(2, 3)
    assert a.sum() == 15

    # torch: テンソル演算（可能なら MPS を使用）
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    x = torch.ones(2, 3, device=device)
    y = (x @ x.T)
    assert y.shape == (2, 2)
    print(f"torch device: {device}")

    # mujoco: 最小モデルを XML からロードし1ステップ進める
    xml = """
    <mujoco>
      <worldbody>
        <body>
          <joint type="hinge"/>
          <geom type="box" size="0.1 0.1 0.1"/>
        </body>
      </worldbody>
    </mujoco>
    """
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_step(model, data)
    print(f"mujoco model: nq={model.nq}, step ok (time={data.time:.3f})")

    print("smoke: OK")


if __name__ == "__main__":
    main()
