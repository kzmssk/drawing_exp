"""spec から MuJoCo XML(平面4自由度アーム + 紙 + カメラ)を生成する。

- アーム: 基部固定 → 鉛直軸ヒンジ4関節 → 先端のペン。各関節に motor アクチュエータ。
- 紙: `table` ボディ上の plane geom。canvas 用の2Dテクスチャ material を貼り、
  実行時に描線ラスタをアップロードして描画過程を映す。
- カメラ: `topdown`(真上/描画過程) と `external`(斜め俯瞰/そとから)。どちらも紙を注視。
"""

from __future__ import annotations

from drawing_exp.env.spec import ArmSpec, CanvasSpec

# 実行時にラスタを流し込むキャンバステクスチャ名(recorder から参照)。
CANVAS_TEXTURE = "canvas_tex"
# ペン先位置を読むサイト名。
PEN_SITE = "pen_tip"


def build_arm_xml(arm: ArmSpec, canvas: CanvasSpec) -> str:
    """平面アーム + 紙 + カメラの MuJoCo XML 文字列を返す。"""
    cx, cy = canvas.center_xy
    half = canvas.size_m / 2.0
    res = canvas.raster_res

    # アーム連鎖(肩→肘→手首→手→ペン)を入れ子ボディで組み立てる。
    chain = _build_chain(arm)
    actuators = "\n".join(
        f'    <motor name="act{i}" joint="j{i}" gear="1" '
        f'ctrlrange="{-t} {t}"/>'
        for i, t in enumerate(arm.torque_limits)
    )

    return f"""<mujoco model="planar_drawing_arm">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="0.2" integrator="Euler" gravity="0 0 -9.81"/>

  <visual>
    <global offwidth="1024" offheight="1024"/>
    <quality shadowsize="2048"/>
  </visual>

  <asset>
    <texture name="{CANVAS_TEXTURE}" type="2d" builtin="flat"
             rgb1="1 1 1" width="{res}" height="{res}"/>
    <material name="canvas_mat" texture="{CANVAS_TEXTURE}"
              texrepeat="1 1" texuniform="false" reflectance="0"/>
    <material name="floor_mat" rgba="0.85 0.85 0.88 1" reflectance="0"/>
    <material name="arm_mat" rgba="0.30 0.45 0.85 1"/>
    <material name="pen_mat" rgba="0.10 0.10 0.10 1"/>
  </asset>

  <worldbody>
    <light pos="0.2 -0.2 1.0" dir="0 0 -1" diffuse="0.9 0.9 0.9"/>
    <light pos="-0.4 -0.6 0.8" dir="0.4 0.6 -0.8" diffuse="0.4 0.4 0.4"/>

    <body name="table" pos="{cx} {cy} 0">
      <geom name="floor" type="plane" size="0.8 0.8 0.05" pos="0 0 -0.005"
            material="floor_mat"/>
      <geom name="paper" type="plane" size="{half} {half} 0.01" pos="0 0 0"
            material="canvas_mat"/>
    </body>

{chain}

    <camera name="topdown" mode="targetbody" target="table"
            pos="{cx} {cy} 0.55" fovy="45"/>
    <camera name="external" mode="targetbody" target="table"
            pos="{cx - 0.15} {cy - 0.6} 0.5" fovy="50"/>
  </worldbody>

  <actuator>
{actuators}
  </actuator>
</mujoco>
"""


def _build_chain(arm: ArmSpec) -> str:
    """入れ子ボディでアーム連鎖を生成。基部は原点、+x 方向へ伸びる。"""
    h = arm.link_height
    lengths = arm.link_lengths
    masses = arm.link_masses
    radii = arm.link_radii
    damping = arm.joint_damping
    armature = arm.joint_armature

    # 末端(ペン)から内側へ組み立て、入れ子文字列を作る。
    inner = _pen_body(arm, lengths[-1])
    for i in reversed(range(len(lengths))):
        pos = "0 0 0" if i == 0 else f"{lengths[i - 1]} 0 0"
        # i==0 の基部リンクは worldbody 直下に置くため高さ h を付与。
        body_pos = f"0 0 {h}" if i == 0 else pos
        link = f"""    <body name="link{i}" pos="{body_pos}">
      <joint name="j{i}" type="hinge" axis="0 0 1" damping="{damping[i]}"
             armature="{armature[i]}"/>
      <geom name="g{i}" type="capsule" material="arm_mat"
            fromto="0 0 0 {lengths[i]} 0 0" size="{radii[i]}" mass="{masses[i]}"/>
{inner}
    </body>"""
        inner = link
    return inner


def _pen_body(arm: ArmSpec, last_len: float) -> str:
    """最終リンク先端から紙面(z=0)へ降ろすペンと、ペン先サイト。"""
    h = arm.link_height
    r = arm.pen_radius
    return f"""      <body name="pen" pos="{last_len} 0 0">
        <geom name="pen_geom" type="capsule" material="pen_mat"
              fromto="0 0 0 0 0 {-h}" size="{r}" mass="0.005"/>
        <site name="{PEN_SITE}" pos="0 0 {-h}" size="{r}" rgba="1 0 0 0.0"/>
      </body>"""
