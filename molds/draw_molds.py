# 未来特性导入
from __future__ import annotations

# 标准库导入
import os
import sys
import time
from typing import Dict, Optional, Any

# 第三方库导入
from pyautocad import Autocad, APoint

# 设置项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 项目模块导入
from molds import calculate_geometry, DrawingOperations, SwingMachineToolingCalculator
from molds.dimension import dimension, date_name
from utils import insert_block, set_layer, create_hatch, generate_filename, safe_acad_operation
from utils.save_drawing import save_drawing

# 常量定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # draw文件夹
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
        return save_drawing(
            self.acad,
            self.filename,
            save_directory,
            max_retries=5,
            retry_delay=1.0,
            check_connection=True,
            dwg_version=60,
            verbose=True
        )
    
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
        
        # 3. 绘制主要视图
        self._draw_views()
        
        # 4. 添加剖面线
        self._add_hatch(geometry)
        
        # 5. 添加尺寸标注
        self._add_dimensions(geometry, drawing_type)
        
        # 6. 插入图块
        self._insert_blocks(drawing_type, designer_name)
        
        # 7. 添加图号和日期
        self._add_title_and_date(radius, chord_length, drawing_type)
        
        return geometry
        
    def _draw_views(self):
        """绘制图形视图"""
        print("开始绘制视图...")
        safe_acad_operation(
            lambda: self.drawing_ops.draw_views(),
            "绘制视图",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(2.0)
        
        print("缩放到范围...")
        self.acad.doc.SendCommand("_.zoom _e ")
        time.sleep(1.5)
        
    def _add_hatch(self, geometry):
        """添加剖面线"""
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
        
    def _add_dimensions(self, geometry, drawing_type):
        """添加尺寸标注"""
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
        
    def _insert_blocks(self, drawing_type, designer_name):
        """插入图块"""
        print("插入图块...")
        insertion_point = APoint(-187, -110)
        blocks_path = os.path.join(PROJECT_ROOT, "blocks")
        
        # 定义要插入的图块
        block_files = [
            "A4图框.dwg",
            f"{drawing_type}.dwg",
            f"{designer_name}.dwg"
        ]
        
        # 批量插入图块
        for i, block_file in enumerate(block_files, 1):
            block_path = os.path.join(blocks_path, block_file)
            print(f"  插入第 {i}/{len(block_files)} 个图块: {block_file}...")
            
            safe_acad_operation(
                lambda b=block_path, p=insertion_point: insert_block(self.acad, p, b),
                f"插入图块 {i}/{len(block_files)}",
                max_retries=3,
                retry_delay=1.0
            )
            time.sleep(2.0)
        
        # 再次缩放到范围
        print("缩放到范围...")
        safe_acad_operation(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.5)
        
    def _add_title_and_date(self, radius, chord_length, drawing_type):
        """添加图号和日期"""
        print("添加图号和日期...")
        self.filename = generate_filename(radius, chord_length, drawing_type=drawing_type)
        
        safe_acad_operation(
            lambda: date_name(name=self.filename),
            "添加图号和日期",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.5)
        
    def close(self) -> None:
        """关闭AutoCAD连接"""
        del self.acad

def run_drawing_from_params(r_value, d_value, selected_groups=None, draw_bottom_part=True, designer_name="周凡"):
    """从参数运行绘图任务
    
    Args:
        r_value: 镜片R值
        d_value: 毛坯直径
        selected_groups: 选中的图形组索引列表（可选）
        draw_bottom_part: 是否绘制底座部分（默认：True，仅用于GUI调用）
        designer_name: 设计者名称（默认："周凡"）
    """
    # 转换参数类型
    R = float(r_value)
    D = float(d_value)
    
    # 计算参数
    calculator = SwingMachineToolingCalculator(
        R=R, blank_D=D, polyurethane_thickness=0.3,
        diamond_pellet_thickness=3, delta_arc=2
    )
    results = calculator.calculate_all(EXCEL_PATH)
    
    # 定义绘图配置
    drawing_configs = [
        {
            "name": "下摆机抛光基模",
            "radius": results["下摆机抛光基模R值"],
            "chord_length": results["下摆机抛光基模口径"],
            "drawing_type": "XPMJM",
            "designer_name": designer_name
        },
        {
            "name": "下摆机精磨基模",
            "radius": results["下摆机精磨基模R值"],
            "chord_length": results["下摆机精磨基模口径"],
            "drawing_type": "XJMJM",
            "designer_name": designer_name
        },
        {
            "name": "基准模",
            "radius": results["镜片R值"],
            "chord_length": results["基准模压聚氨酯口径"],
            "drawing_type": "JZM",
            "designer_name": designer_name,
            "b": 3
        },
        {
            "name": "基准模改丸片",
            "radius": -results["镜片R值"],
            "chord_length": results["基准模改丸片口径"],
            "drawing_type": "JZM_KC",
            "designer_name": designer_name,
            "b": 3
        },
        {
            "name": "高速抛光修盘基模",
            "radius": results["高速抛光修盘基模R值"],
            "chord_length": results["高速抛光修盘基模口径"],
            "drawing_type": "GPMXJ",
            "designer_name": designer_name,
            "b": 6
        },
        {
            "name": "高速抛光基模修盘",
            "radius": results["高速抛光基模修盘R值"],
            "chord_length": results["高速抛光基模修盘口径"],
            "drawing_type": "GPMJX",
            "designer_name": designer_name,
            "b": 3
        }
    ]
    
    # 过滤选中的图形组
    selected_configs = drawing_configs if not selected_groups else [drawing_configs[i] for i in selected_groups]
    
    # 批量绘制图形
    for i, config in enumerate(selected_configs, 1):
        print(f"\n✏️  第{i}/{len(selected_configs)}: {config['name']}")
        
        drawing_instance = None
        try:
            # 创建绘图实例
            drawing_instance = AutoCadDrawing()
            
            # 执行绘图 - 排除'name'键（create_drawing方法不接受此参数）
            config_without_name = {k: v for k, v in config.items() if k != 'name'}
            drawing_instance.create_drawing(**config_without_name, draw_bottom_part=draw_bottom_part)
            drawing_instance.save_drawing()
            
            print(f"  ✓ {config['name']} 绘制成功")
            
        except Exception as e:
            print(f"  ✗ {config['name']} 绘制失败: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # 清理资源
            if drawing_instance:
                drawing_instance.close()
            
            # 绘制下一个图形前等待
            if i < len(selected_configs):
                time.sleep(2.0)


if __name__ == "__main__":
    import sys
    
    print("AutoCAD绘图工具启动中...")
    print("=" * 50)
    
    # 命令行模式
    if len(sys.argv) >= 3:
        try:
            R = sys.argv[1]
            D = sys.argv[2]
            
            print(f"命令行参数: R = {R}, D = {D}")
            
            # 解析图形组选择参数
            selected_groups = []
            if "--groups" in sys.argv:
                idx = sys.argv.index("--groups")
                if idx + 1 < len(sys.argv):
                    groups_str = sys.argv[idx+1]
                    selected_groups = [int(x) for x in groups_str.split(",") if x.isdigit()]
                    print(f"选择的图形组: {selected_groups}")
            
            print("=" * 50)
            
            # 执行绘图任务
            run_drawing_from_params(R, D, selected_groups)
            
            print("=" * 50)
            print("✓ 绘图任务完成")
            
        except ValueError as e:
            print(f"\n✗ 参数错误: {e}")
            print("使用方式:")
            print("  python draw_molds.py <R值> <D值> [--groups <组索引列表>]")
            print("例如:")
            print("  python draw_molds.py 100 50")
            print("  python draw_molds.py 100 50 --groups 0,1")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ 执行错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # GUI模式
    else:
        try:
            print("没有提供命令行参数，启动GUI界面...")
            print("如果需要使用命令行模式，请提供R值和D值")
            print("=" * 50)
            
            from molds.molds_gui import create_gui
            create_gui()
            
        except ImportError:
            print("\n✗ GUI模块导入失败")
            print("请确保molds_gui.py文件存在且可导入")
            print("\n尝试使用命令行模式:")
            print("  python draw_molds.py <R值> <D值>")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ GUI启动失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
