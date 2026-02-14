
# 标准库导入
import math
import os
import time
from typing import Optional

# 第三方库导入
from pyautocad import APoint, aDouble, Autocad

# 项目模块导入
from molds.Tool_calculation import SwingMachineToolingCalculator
from molds.dimension import date_name, dia
from utils import set_layer, create_hatch, insert_block, initial_connection, retry
from utils.filename import generate_filename
from utils.save_drawing import save_drawing

# 常量定义
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")
EXCEL_PATH = os.path.join(CURRENT_DIR, "口径常数.xlsx")

# 绘图类型常量
DRAWING_TYPE_JINGMO = "精磨丸片"
DRAWING_TYPE_XIUPAN = "修盘丸片"

class WP:
    """WP图形绘制类"""
    
    def __init__(self, acad=None, template_path=DEFAULT_TEMPLATE_PATH):
        self.acad = None
        self.filename = None
        initial_connection(self, acad, template_path)
    
    def save_drawing(self, parameter, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
        diameter, radius = parameter["diameter"], parameter["radius"]
        self.base_filename = generate_filename(radius, diameter, "WP")
        self.filename = f"{self.base_filename}.dwg"
        return save_drawing(self.acad, self.filename, save_directory, max_retries=3, retry_delay=1.0, check_connection=True, dwg_version=60)
           
    def main(self, parameter):
        diameter, radius, base = parameter["diameter"], parameter["radius"], parameter["base"]
        designer_name = parameter.get("designer_name", "默认设计师")
        drawing_type = parameter.get("drawing_type", DRAWING_TYPE_JINGMO)
        self.base_filename = generate_filename(radius, diameter, "WP")

        chord = diameter
        r = abs(radius)
        sagitta = r - math.sqrt(r**2 - (chord / 2)**2)
        sagitta2 = r - math.sqrt(r**2 - 0.5**2)
        half_angle = math.asin((chord / 2) / r)

        up, down = [0] * 7, [0] * 7
        set_layer("标注线")

        if radius >= 0:
            center = base + APoint(-radius + 3 + sagitta, 0)
            start_angle, end_angle = -half_angle, +half_angle
            up[1], down[1] = base + APoint(3, chord / 2), base + APoint(3, -chord / 2)
            up[5], down[5] = base + APoint(3 + sagitta - sagitta2, 0.5), base + APoint(3 + sagitta - sagitta2, -0.5)
        else:
            center = base + APoint(abs(radius) + 3, 0)
            start_angle, end_angle = math.pi - half_angle, math.pi + half_angle
            chord = chord + 1 if chord < 10 else chord + 2
            up[1], down[1] = base + APoint(3 + sagitta, chord / 2), base + APoint(3 + sagitta, -chord / 2)
            up[5], down[5] = base + APoint(3 + sagitta, 0.5), base + APoint(3 + sagitta, -0.5)
            #最外侧口径标注
            dim_point1 = APoint(up[1].x + 1.5 * chord, up[1].y)
            dim_obj1 = self.acad.model.AddDimAligned(up[1], down[1], dim_point1)
            dim_obj1.TextOverride = "%%c<>"
            dim_obj1.StyleName = "ZqStandard0.5"


         
        angle_rad = math.radians(30) if radius >= 0 else math.radians(210)
        chord_point = APoint(center.x + abs(radius) * math.cos(angle_rad), center.y + abs(radius) * math.sin(angle_rad))
        
        dim_rad = self.acad.model.AddDimRadial(center, chord_point, radius)
        dim_rad.StyleName = "ZqStandard0.5$4"
        dim_rad.TextOverride = f"{'凹' if radius < 0 else ''}<> ".strip()

        dim_style = self.acad.ActiveDocument.DimStyles.Item("ZqStandard0.5")
        self.acad.ActiveDocument.ActiveDimStyle = dim_style
        
        up[0], down[0] = base + APoint(0, chord / 2), base + APoint(0, -chord / 2)
        
        #总高标注
        dim_obj_up01 = self.acad.model.AddDimAligned(up[0], up[1], APoint(up[0].x, up[0].y + chord))
        #小孔口径标注
        up[2], down[2] = base + APoint(0, 0.75), base + APoint(0, -0.75)
        dim_obj2 = self.acad.model.AddDimAligned(up[2], down[2], APoint(up[2].x - chord/2, up[2].y))
        dim_obj2.TextOverride = "%%c<>"
        dim_obj2.ToleranceDisplay, dim_obj2.ToleranceUpperLimit, dim_obj2.ToleranceLowerLimit = 2, 0.02, 0.00
        dim_obj2.TolerancePrecision, dim_obj2.ToleranceHeightScale = 3, 0.7
        dim_obj2.Update()
        #小孔深度
        up[3], down[3] = base + APoint(1, 0.75), base + APoint(1, -0.75)
        self.acad.model.AddDimAligned(up[2], up[3], APoint(up[1].x, up[1].y + chord/2))
        
        up[4], down[4] = base + APoint(3, 0.5), base + APoint(3, -0.5)
        up[6] = center + APoint(radius * math.cos(half_angle), abs(radius) * math.sin(half_angle))
        down[6] = center + APoint(radius * math.cos(half_angle), -abs(radius) * math.sin(half_angle))
        #内口径标注
        dim_obj6 = self.acad.model.AddDimAligned(up[1], down[1], APoint(up[1].x + chord, up[1].y))
        dim_obj6.TextOverride = "%%c<>"

        set_layer("轮廓线")
        arc = self.acad.model.AddArc(center, abs(radius), start_angle, end_angle)

        pline1 = self.acad.model.AddPolyline(aDouble([j for i in [up[6], up[1], up[0], down[0], down[1], down[6], up[6]] for j in i]))
        pline2 = self.acad.model.AddPolyline(aDouble([j for i in [up[2], up[3], down[3], down[2]] for j in i]))
        pline3 = self.acad.model.AddPolyline(aDouble([j for i in [up[5], up[4], down[4], down[5]] for j in i]))

        center2 = center + APoint(4 * chord, 0)
        self.acad.model.AddCircle(center2, 1.5/2)
        self.acad.model.AddCircle(center2, abs(radius))
        if radius <= 0:
            self.acad.model.AddCircle(center2, chord/2)
        # 计算水平切线的x偏移量，确保使用正确的半径值并避免负数平方根
        if radius >= 0:
            current_radius = abs(radius)
        else:
            current_radius = chord / 2
        
        # 确保半径大于0.5，避免负数平方根
        if current_radius < 0.5:
            current_radius = 0.5
            
        x_offset = math.sqrt(current_radius ** 2 - 0.25)
        
       
        
        self.acad.model.AddLine(APoint(center2.x - x_offset, center2.y + 0.5), APoint(center2.x + x_offset, center2.y + 0.5))
        self.acad.model.AddLine(APoint(center2.x - x_offset, center2.y - 0.5), APoint(center2.x + x_offset, center2.y - 0.5))
        
        date_name(name=self.base_filename)
        set_layer("标注线")
        dia(self.acad, center2, radius, math.radians(90))
        if radius <= 0:
            dia(self.acad, center2, chord / 2, math.radians(135))
        
        retry(lambda: self.acad.doc.SendCommand("_.zoom _e "), "缩放到范围", max_retries=3, initial_delay=0.8)
        time.sleep(1.0)
        
        set_layer("剖面线")
        time.sleep(0.5)
        retry(lambda: create_hatch(self.acad, base.x + 2, base.y + 2), "创建填充", max_retries=3, initial_delay=1.0)
        
        set_layer("轮廓线")
        insertion_point = APoint(-187, -110)
        blocks_path = os.path.join(BASE_DIR, "blocks")
        
        block_files = ["A4图框.dwg", f"{drawing_type}.dwg", f"{designer_name}.dwg"]
        
        for i, block_file in enumerate(block_files, 1):
            block_path = os.path.join(blocks_path, block_file)
            insert_block(self.acad, insertion_point, block_path)
            time.sleep(1.5)
        
        return arc, pline1, pline2, pline3

def run_wp_from_params(r_value, d_value, selected_groups=None, designer_name="周凡"):
    """运行WP图形绘制
    
    Args:
        r_value: 镜片半径
        d_value: 镜片口径
        selected_groups: 选中的图形组索引列表
        designer_name: 设计师名称
    """
    R, D = float(r_value), float(d_value)
    calculator = SwingMachineToolingCalculator(R=R, blank_D=D, polyurethane_thickness=0.3, diamond_pellet_thickness=3, delta_arc=2)
    results = calculator.calculate_all(EXCEL_PATH)

    # 定义绘图配置
    drawing_configs = [
        {"name": "精磨基模", "radius": results["下摆机精磨基模R值"], "diameter": results["下摆机精磨基模口径"], "drawing_type": DRAWING_TYPE_JINGMO},
        {"name": "基准模改丸片", "radius": results["镜片R值"], "diameter": results["基准模改丸片口径"], "drawing_type": DRAWING_TYPE_XIUPAN}
    ]

    # 根据selected_groups选择要绘制的配置
    selected_configs = drawing_configs
    if selected_groups:
        selected_configs = [drawing_configs[i] for i in selected_groups]

    # 绘制选中的配置
    for i, config in enumerate(selected_configs, 1):
        print(f"\n✏️  第{i}/{len(selected_configs)}: {config['name']}")
        drawing_instance = WP()
        draw_params = {**config, "base": APoint(0, 0), "designer_name": designer_name}
        drawing_instance.main(draw_params)
        drawing_instance.save_drawing(draw_params)
        print(f"  ✓ {config['name']} 绘制成功")
        
        # 释放资源
        drawing_instance.acad = None
        
        # 绘制下一个图形前短暂延迟
        if i < len(selected_configs):
            time.sleep(2.0)

if __name__ == "__main__":
    R = float(input("请输入镜片半径R："))
    D = float(input("请输入镜片口径D："))
    print(f"\n开始绘制WP图形...\n参数: R = {R}, D = {D}\n{'-' * 50}")
    run_wp_from_params(R, D)
    print(f"{'-' * 50}\n\n✓ 所有图形处理完成")
