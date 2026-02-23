
# 标准库导入
import math
import os
import sys
import time

# 添加项目根目录和当前目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录和 molds 目录到 Python 路径
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 第三方库导入
from pyautocad import APoint, aDouble, Autocad

# 项目模块导入
from Tool_calculation import SwingMachineToolingCalculator
from utils import date_name,CL
from utils import set_layer, create_hatch, insert_block, safe_acad_retry, _open_template
from utils import generate_filename, save_drawing, _initialize_acad

from wp_side_view import draw_side_view
from wp_main_view import draw_main_view

# 常量定义
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "新图样.dwt")
EXCEL_PATH = os.path.join(CURRENT_DIR, "口径常数.xlsx")

# 绘图类型常量
DRAWING_TYPE_JINGMO = "精磨丸片"
DRAWING_TYPE_XIUPAN = "修盘丸片"



@safe_acad_retry(max_retries=3, delay=0.8, name="缩放到范围并创建填充")
def _zoom_and_create_hatch(acad, x, y):
    """缩放到范围并创建填充"""
    acad.doc.SendCommand("_.zoom _e ")
    set_layer("剖面线")
    time.sleep(0.5)
    create_hatch(acad, x, y)
 
 
 
 
def main(parameter):
    diameter, radius, base = parameter["diameter"], parameter["radius"], parameter["base"]
    if radius >= 0:
        chord_to_center=math.sqrt(radius**2 - (diameter/2)**2)
        center = base + APoint(-chord_to_center + 3 , 0)
    else:
        center = base + APoint(-radius + 3 , 0)
   
   
    
    designer_name = parameter.get("designer_name", "默认设计师")
    drawing_type = parameter.get("drawing_type", DRAWING_TYPE_JINGMO)
    filename = generate_filename(radius, diameter, "WP")
    acad = _initialize_acad()
    set_layer("轮廓线")
    # 绘制侧视图
    draw_side_view(acad, center, diameter, radius)
    # 绘制主视图
    draw_main_view(acad, radius, center, chord=diameter)   
    
    # 后续通用操作
    date_name(name=filename)
    
    _zoom_and_create_hatch(acad, base.x + 2, base.y + 2)
    CL(acad, base+APoint(-3,0), base+APoint(10,0))
    set_layer("轮廓线")
    insertion_point = APoint(-187, -110)
    blocks_path = os.path.join(BASE_DIR, "blocks")
    
    block_files = ["A4图框.dwg", f"{drawing_type}.dwg", f"{designer_name}.dwg"]
    
    for i, block_file in enumerate(block_files, 1):
        block_path = os.path.join(blocks_path, block_file)
        insert_block(acad, insertion_point, block_path)
        time.sleep(1.5)
    
    return  acad, filename


def run_wp_from_params(r_value, d_value, selected_groups=None, designer_name="周凡"):
    R, D = float(r_value), float(d_value)
    calculator = SwingMachineToolingCalculator(R=R, blank_D=D, polyurethane_thickness=0.3, diamond_pellet_thickness=3, delta_arc=2)
    results = calculator.calculate_all(EXCEL_PATH)

    # 定义绘图配置
    drawing_configs = [
        {"name": "精磨基模", "radius": results["下摆机精磨基模R值"], "diameter": results["下摆机精磨基模口径"], "drawing_type": DRAWING_TYPE_JINGMO},
        {"name": "基准模改丸片", "radius": results["镜片R值"], "diameter": results["基准模改丸片口径"], "drawing_type": DRAWING_TYPE_XIUPAN}
    ]

    # 选择要绘制的配置
    selected_configs = [drawing_configs[i] for i in selected_groups] if selected_groups else drawing_configs

    # 绘制选中的配置
    for config in selected_configs:
       
        draw_params = {**config, "base": APoint(0, 0), "designer_name": designer_name}
        _open_template(DEFAULT_TEMPLATE_PATH)
        acad, filename = main(draw_params)
        # 直接使用utils中的save_drawing函数
        save_drawing(acad, filename, DEFAULT_SAVE_DIR)

if __name__ == "__main__":
    try:
        R = float(input("请输入镜片半径R："))
        D = float(input("请输入镜片口径D："))
        run_wp_from_params(R, D)
    except KeyboardInterrupt:
        print("\n程序已被用户中断。")
    except ValueError:
        print("\n输入错误，请输入有效的数字。")
