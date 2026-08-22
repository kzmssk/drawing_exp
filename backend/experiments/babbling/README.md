# バブリング実験

ランダムトルクで平面4自由度アームを動かし、殴り描き(CONCEPT フェーズ1)を生成する。
学習は行わない。共通ライブラリ `drawing_exp.env` / `drawing_exp.render` を使う薄い実験層。

## 実行

```bash
cd backend
uv run python experiments/babbling/run.py
```

## 出力 (`runs/<timestamp>/`, gitignore対象)

- `drawing.png` — 描かれた画像 (128x128)
- `drawing_topdown.mp4` — 描画過程の動画(真上カメラ, 512x512)
- `external.mp4` — 描画過程をそとから見た動画(斜め俯瞰, 512x512)
- `config.json` — 実験設定(再現用)

## 仕様

- アーム諸元(5歳児想定)・紙サイズ・解像度・ステップ数は `drawing_exp.env.spec` に集約。
- 1エピソード = 60秒 = 300ステップ(dt=0.2s)。物理精度より計算効率を優先。
- 乱数の強さ・保持長・シード・動画設定は `config.py` の `BabblingConfig` で調整。

## 他実験の作り方

`experiments/<name>/` を新規に作り、`drawing_exp` を import して独自の制御ループを書く。
env/render は共通、実験固有のロジックだけを各ディレクトリに置く(疎結合)。
