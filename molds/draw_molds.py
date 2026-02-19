# draw_molds.py （简化版）

from __future__ import annotations
import os
import sys
import time

from typing import Any, Dict, Optional, List


from pyautocad import Autocad, APoint

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录和 molds 目录到 Python 路径
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geometry import calculate_geometry
from drawing_operations import DrawingOperations
from Tool_calculation import SwingMachineToolingCalculator
from utils import insert_block, set_layer, create_hatch, generate_filename, save_drawing, date_name, safe_acad_retry

# ─── 常量 ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(PROJECT_ROOT, "output")
EXCEL_PATH = os.path.join(BASE_DIR, "口径常数.xlsx")

DEFAULT_A = 3
DEFAULT_B = 6
DEFAULT_C = 25

# 从 molds_gui.py 导入图形组配置
from molds_gui import GROUPS

# 转换 GUI 图形组配置为绘图类型配置表
DRAWING_TYPES = {
    gtype: {
        "display_name": name,
        "negative": neg,
        "radius_key": {
            "XPMJM": "下摆机抛光基模R值",
            "XJMJM": "下摆机精磨基模R值",
            "JZM": "镜片R值",
            "JZM_KC": "镜片R值",
            "GPMXJ": "高速抛光修盘基模R值",
            "GPMJX": "高速抛光基模修盘R值",
        }.get(gtype, "镜片R值"),
        "diameter_key": {
            "XPMJM": "下摆机抛光基模口径",
            "XJMJM": "下摆机精磨基模口径",
            "JZM": "基准模压聚氨酯口径",
            "JZM_KC": "基准模改丸片口径",
            "GPMXJ": "高速抛光修盘基模口径",
            "GPMJX": "高速抛光基模修盘口径",
        }.get(gtype, "基准模压聚氨酯口径"),
    }
    for i, (name, gtype, neg) in enumerate(GROUPS[:6])
}

# ─── 辅助函数 ────────────────────────────────────────────────────────────
@safe_acad_retry(3, 1.0, "打开模板")
def _open_template(path: str):
    """打开 AutoCAD 模板"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"模板文件不存在: {path}")
    
    # 创建AutoCAD实例
    acad = Autocad(create_if_not_exists=True)
    time.sleep(0.5)
    acad.app.Documents.Add(path)
  
@safe_acad_retry(3, 0.8, "添加剖面线")
def _add_hatch(acad, geometry: Dict):
    """添加剖面线"""
    create_hatch(acad, -3, geometry["y_U"] - 3)
    time.sleep(0.6)

@safe_acad_retry(4, 1.0, "插入图块")
def _insert_blocks(acad, drawing_type: str, designer_name: str):
    """插入图块"""
    pt = APoint(-187, -110)
    blocks_path = os.path.join(PROJECT_ROOT, "blocks")
    files = ["A4图框.dwg", f"{drawing_type}.dwg", f"{designer_name}.dwg"]

    for fname in files:
        path = os.path.join(blocks_path, fname)
        insert_block(acad, pt, path)
        time.sleep(0.6)

    acad.doc.SendCommand("_.zoom _e ")
    time.sleep(1.2)



    
    


# ─── 批量执行入口 ────────────────────────────────────────────────────────
def batch_draw_molds(
    r_value: float | str,
    d_value: float | str,
    selected_indices: Optional[List[int]] = None,
    draw_bottom: bool = True,
    designer_name: str = "周凡",
    a_value: float = DEFAULT_A,
    b_value: float = DEFAULT_B,
    c_value: float = DEFAULT_C
):
    """批量绘制模具图形"""
    R = float(r_value)
    D = float(d_value)

    # 计算所有参数
    calc = SwingMachineToolingCalculator(R=R, blank_D=D)
    results = calc.calculate_all(EXCEL_PATH)

    # 确定要处理的任务
    tasks = selected_indices or list(range(6))

    for idx in tasks:
        if 0 <= idx < 6:  # 只处理前6个任务
            # 直接从 GROUPS 获取绘图类型，避免创建映射字典
            name, dt, neg = GROUPS[idx]
            
            # 直接生成配置
            if cfg := DRAWING_TYPES.get(dt):
                radius = results[cfg["radius_key"]]
                if cfg["negative"]:
                    radius = -radius
                chord_length = results[cfg["diameter_key"]]

                print(f"\n绘制 {dt}  ── {DRAWING_TYPES[dt]['display_name']}")

                acad = None
                try:
                    # 计算几何参数，创建绘图操作实例
                    geometry = calculate_geometry(radius, chord_length, a_value, b_value, c_value)
                    # 打开模板
                    _open_template( DEFAULT_TEMPLATE_PATH)
                    set_layer("轮廓线")
                    
                    ops = DrawingOperations(geometry, dt, draw_bottom)
                    
                    ops.draw_views()
                    set_layer("剖面线")
                    _add_hatch(ops.acad, geometry)  # 使用ops内部的acad实例
                    set_layer("轮廓线")
                    _insert_blocks(ops.acad, dt, designer_name)  # 使用ops内部的acad实例
                    filename = generate_filename(radius, chord_length, drawing_type=dt)
                    date_name(name=filename)
                    save_drawing(ops.acad, filename, DEFAULT_SAVE_DIR, dwg_version=60)  # 使用ops内部的acad实例

                    print("  ✓ 完成")
                finally:
                    # 清理资源
                    if acad:
                        del acad
                    if idx != tasks[-1]:
                        time.sleep(1.2)  # 任务间最小间隔


if __name__ == "__main__":
    # 直接运行此文件时启动 GUI 界面
    current_dir = os.path.dirname(os.path.abspath(__file__))
    gui_file = os.path.join(current_dir, "molds_gui.py")
    os.system(f'python "{gui_file}"')
