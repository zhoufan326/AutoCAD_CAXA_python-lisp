from __future__ import annotations

import os
import time
import sys
from typing import Dict, Optional, Any
from pyautocad import Autocad, APoint

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 从molds包导入模块
from molds import calculate_geometry, DrawingOperations, SwingMachineToolingCalculator
# 导入utils模块
from utils import insert_block, set_layer, create_hatch, generate_filename, safe_acad_operation
# 使用绝对导入替代相对导入
from molds.dimension import dimension, date_name

# 常量定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # draw文件夹
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # 项目根目录
DEFAULT_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "新图样.dwt")  # 模板文件在根目录
DEFAULT_SAVE_DIR = os.path.join(PROJECT_ROOT, "output")  # 输出目录在根目录
EXCEL_PATH = os.path.join(BASE_DIR, "口径常数.xlsx")  # Excel文件在draw文件夹

# 默认几何参数
DEFAULT_PARAM_A = 3  # 变量a的默认值定义
DEFAULT_PARAM_B = 6
DEFAULT_PARAM_C = 25


class AutoCadDrawing:
    """用于创建和管理AutoCAD图形"""
    
    def __init__(self, template_path: Optional[str] = DEFAULT_TEMPLATE_PATH):
        # 连接 AutoCAD
        self.acad = Autocad(create_if_not_exists=True)
        time.sleep(1.5)

        # 如果提供了模板，尝试打开
        if template_path and os.path.exists(template_path):
            print(f"使用模板: {template_path}")
            for _ in range(3):
                try:
                    self.acad.app.Documents.Add(template_path)
                    time.sleep(1.5)
                    break
                except Exception as e:
                    if '繁忙' in str(e) or '2147418111' in str(e):
                        time.sleep(1.5)
                        continue

        

    def save_drawing(self, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
        """保存图形到指定目录"""
        os.makedirs(save_directory, exist_ok=True)
        
        if not self.filename.endswith('.dwg'):
            self.filename += '.dwg'
        
        filepath = os.path.join(save_directory, self.filename)
        os.makedirs(os.path.dirname(filepath) or save_directory, exist_ok=True)
        
        # 尝试保存，如果AutoCAD繁忙则重试
        for _ in range(5):
            try:
                self.acad.doc.SaveAs(filepath, 60)
                print(f"保存成功: {filepath}")
                return filepath
            except Exception as error:
                error_str = str(error)
                if '-2147418111' in error_str or '拒绝接收' in error_str:
                    time.sleep(1)
                    continue
                else:
                    break
    
    def create_drawing(self, radius: float, chord_length: float, a: float = DEFAULT_PARAM_A, 
                      b: float = DEFAULT_PARAM_B, c: float = DEFAULT_PARAM_C, drawing_type: str = "XJMJM", designer_name: str = "戴磊", draw_bottom_part: bool = True) -> Dict[str, Any]:
        """绘制图形
        
        Args:
            radius: 半径
            chord_length: 弦长
            a: 参数a
            b: 参数b
            c: 参数c
            drawing_type: 绘图类型
            designer_name: 设计者名称
            draw_bottom_part: 是否绘制底座部分（默认：True，仅GUI模式使用）
        """
        
        # 1. 计算几何参数
        geometry = calculate_geometry(radius, chord_length, a, b, c)
        
        # 2. 初始化绘图操作对象
        self.drawing_ops = DrawingOperations(self.acad, set_layer, geometry, drawing_type, draw_bottom_part=draw_bottom_part)
        
        # 3. 绘图
        print("开始绘制视图...")
        safe_acad_operation(
            lambda: self.drawing_ops.draw_views(),
            "绘制视图",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(2.0)
        print("缩放到范围...")
        self.acad.doc.SendCommand("_.zoom _e "),                        
        time.sleep(1.5)
        # 3. 添加剖面线
        set_layer("剖面线")
        internal_x = -3
        internal_y = geometry["y_U"] - 3
        
        safe_acad_operation(
            lambda: create_hatch(self.acad, internal_x=internal_x, internal_y=internal_y),
            "添加剖面线",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(2.0)

        # 4. 添加尺寸标注
        set_layer("标注线")
        print("添加尺寸标注...")
        safe_acad_operation(
            lambda: dimension(geometry, drawing_type),
            "添加标注",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(2.0)
        
        set_layer("轮廓线")
        
        # 5. 插入图块
        print("插入图块...")
        insertionPnt = APoint(-187, -110)
        insertionPnt2 = APoint(-187, -110)
        
        base_path = os.path.join(PROJECT_ROOT, "blocks")
        block_configs = [
            (insertionPnt, os.path.join(base_path, "A4图框.dwg")),
            (insertionPnt2, os.path.join(base_path, f"{drawing_type}.dwg")),
            (insertionPnt2, os.path.join(base_path, f"{designer_name}.dwg"))
        ]
        
        for i, config in enumerate(block_configs, 1):
            print(f"  插入第 {i}/3 个图块...")
            safe_acad_operation(
                lambda c=config: insert_block(self.acad, *c),
                f"插入图块 {i}/3",
                max_retries=3,
                retry_delay=1.0
            )
            time.sleep(2.0)
        
        # 6. 缩放到范围
        print("缩放到范围...")
        safe_acad_operation(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.5)
        
        # 7. 添加图号和日期
        print("添加图号和日期...")
        self.filename = generate_filename(radius, chord_length, drawing_type=drawing_type)
        safe_acad_operation(
            lambda: date_name(name=self.filename),
            "添加图号和日期",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.5)

        return geometry
        
    def close(self) -> None:
        """关闭AutoCAD连接"""
        del self.acad

def run_drawing_from_params(r_value, d_value, selected_groups=None, draw_bottom_part=True):
    """从参数运行绘图任务
    
    Args:
        r_value: 镜片R值
        d_value: 毛坯直径
        selected_groups: 选中的图形组索引列表（可选）
        draw_bottom_part: 是否绘制底座部分（默认：True，仅用于GUI调用）
    """
    R = float(r_value)
    D = float(d_value)
    
    # 计算参数
    calculator = SwingMachineToolingCalculator(
        R=R, blank_D=D, polyurethane_thickness=0.3,
        diamond_pellet_thickness=3, delta_arc=2
    )
    results = calculator.calculate_all(EXCEL_PATH)
    
    # 定义所有绘图参数
    all_params = [
        {
          "radius": results["下摆机抛光基模R值"],
          "chord_length": results["下摆机抛光基模口径"],
          "drawing_type": "XPMJM", "designer_name": "周凡"
        },
        {
          "radius": results["下摆机精磨基模R值"],
          "chord_length": results["下摆机精磨基模口径"],
          "drawing_type": "XJMJM", "designer_name": "周凡"
        },
        {
            "radius": results["镜片R值"],
            "chord_length": results["基准模压聚氨酯口径"],
            "drawing_type": "JZM", "designer_name": "周凡", "b": 3
        },
        {
            "radius": -results["镜片R值"],
            "chord_length": results["基准模改丸片口径"],
            "drawing_type": "JZM_KC", "designer_name": "周凡", "b": 3
        },
        {
          "radius": results["高速抛光修盘基模R值"],
          "chord_length": results["高速抛光修盘基模口径"],
          "drawing_type": "GPMXJ", "designer_name": "周凡", "b": 6
        },
        {
          "radius": results["高速抛光基模修盘R值"],
          "chord_length": results["高速抛光基模修盘口径"],
          "drawing_type": "GPMJX", "designer_name": "周凡", "b": 3
        }
    ]
    
    # 过滤选中的图形组
    params_list = all_params if not selected_groups else [all_params[i] for i in selected_groups]
    
    # 批量绘图
    for i, params in enumerate(params_list, 1):
        print(f"\n第{i}/{len(params_list)}: {params['drawing_type']}")
        
        drawing = None
        try:
            drawing = AutoCadDrawing()
            drawing.create_drawing(**params, draw_bottom_part=draw_bottom_part)
            drawing.save_drawing()
        except Exception as e:
            print(f"失败: {e}")
        finally:
            if drawing:
                drawing.close()
            if i < len(params_list):
                time.sleep(2.0)


if __name__ == "__main__":
    import sys
    
    # 如果有命令行参数，使用命令行模式
    if len(sys.argv) >= 3:
        R = sys.argv[1]
        D = sys.argv[2]
        
        # 解析图形组选择
        selected_groups = []
        if "--groups" in sys.argv:
            idx = sys.argv.index("--groups")
            if idx + 1 < len(sys.argv):
                selected_groups = [int(x) for x in sys.argv[idx+1].split(",") if x.isdigit()]
        
        run_drawing_from_params(R, D, selected_groups)
    else:
        # 没有命令行参数，自动打开GUI
        print("没有提供命令行参数，启动GUI界面...")
        from molds.molds_gui import create_gui
        create_gui()
