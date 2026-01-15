from __future__ import annotations

import os
import time

from typing import Dict, Optional, Any
from pyautocad import Autocad, APoint

# 导入自定义的模块
from draw import calculate_geometry, generate_filename, DrawingOperations
from utils import insert_block, set_layer, dimension, date_name, create_hatch

# 常量定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")
EXCEL_PATH = os.path.join(BASE_DIR, "draw", "口径常数.xlsx")

# 默认几何参数
DEFAULT_PARAM_A = 3
DEFAULT_PARAM_B = 6
DEFAULT_PARAM_C = 25

def safe_acad_operation(operation, operation_name="AutoCAD操作", max_retries=3, retry_delay=1.5):
    """
    安全执行AutoCAD操作的包装函数，带有重试机制
    
    参数:
        operation: 要执行的函数或lambda表达式
        operation_name: 操作名称，用于日志
        max_retries: 最大重试次数
        retry_delay: 重试之间的延迟（秒）
    
    返回:
        操作的结果，如果所有重试都失败则返回None
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            return result
        except Exception as e:
            error_str = str(e)
            is_busy_error = '-2147418111' in error_str or '拒绝接收' in error_str or '繁忙' in error_str
            
            if is_busy_error and attempt < max_retries - 1:
                print(f"  {operation_name}繁忙，等待重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 1.2  # 逐渐增加延迟
            else:
                print(f"  {operation_name}失败: {e}")
                raise
    return None

class AutoCadDrawing:
    """用于创建和管理AutoCAD图形"""
    
    def __init__(self, template_path: Optional[str] = DEFAULT_TEMPLATE_PATH):
       
            # 连接 AutoCAD 并保存到实例属性
        self.acad = Autocad(create_if_not_exists=True)
        
        # 等待 AutoCAD 完全初始化
        print("等待 AutoCAD 初始化...")
        time.sleep(1.5)

            # 如果提供了模板，尝试打开（带简单重试）
        if template_path:
            template_path = os.path.normpath(template_path)
            if os.path.exists(template_path):
                print(f"使用模板: {template_path}")
                for _ in range(3):
                    try:
                            # 使用 self.acad 的 app 对象添加模板
                            self.acad.app.Documents.Add(template_path)
                            print("模板加载成功，等待文档准备就绪...")
                            time.sleep(1.5)
                            break
                    except Exception as e:
                            if '繁忙' in str(e) or '2147418111' in str(e):
                                time.sleep(1.5)
                                continue

            # 将 utils 中的辅助函数绑定到实例，便于在方法中以 self.xxx 形式调用
            self.set_layer = set_layer
            self.dimension = dimension
            self.date_name = date_name
            self.create_hatch = create_hatch
            self.insert_block = insert_block
            # 初始化绘图操作对象（将当前 acad 与 set_layer 传入）
            self.drawing_ops = DrawingOperations(self.acad, self.set_layer)

            # 打印当前文档名（容错访问 doc/ActiveDocument）
            try:
                doc = getattr(self.acad, 'doc', None) or getattr(self.acad, 'ActiveDocument', None)
                print(f"当前文档: {doc.Name}")
            except Exception:
                print("当前文档: (unknown)")
    
    #-----------定义保存函数------------#
    def save_drawing(self, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
  
        # 如果目录不存在则创建
        os.makedirs(save_directory, exist_ok=True)
        
        # 生成文件路径
        
        if not self.filename.endswith('.dwg'):
            self.filename += '.dwg'
        filepath = os.path.join(save_directory, self.filename)
        # 确保父目录存在（generate_filename 可能返回带子目录的名字/历史兼容）
        parent_dir = os.path.dirname(filepath) or save_directory
        os.makedirs(parent_dir, exist_ok=True)
        
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
                      b: float = DEFAULT_PARAM_B, c: float = DEFAULT_PARAM_C, drawing_type: str = "XJMJM", designer_name: str = "戴磊") -> Dict[str, Any]:
       
        # 1. 计算几何参数
        geometry = calculate_geometry(radius, chord_length, a, b, c)
        
        # 2. 绘图
        print("开始绘制视图...")
        safe_acad_operation(
            lambda: self.drawing_ops.draw_views(geometry, drawing_type=drawing_type),
            "绘制视图",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(1.0)  # 增加等待时间
        
        # 5. 添加剖面线
        self.set_layer("剖面线")

        # 使用现有的AutoCAD连接，而不是创建新的连接
        internal_x=geometry["center"].x-1
        internal_y=geometry["left_point"].y-15
        
        safe_acad_operation(
            lambda: self.create_hatch(self.acad, internal_x=internal_x, internal_y=internal_y),
            "添加剖面线",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(1.5)  # 增加等待时间
       

        # 6. 添加尺寸标注
        self.set_layer("标注线")
        print("添加尺寸标注...")
        safe_acad_operation(
            lambda: self.dimension(geometry, drawing_type),
            "添加标注",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(1.0)  # 增加等待时间
        
        self.set_layer("轮廓线")
        # 7. 插入图块
        print("插入图块...")
        insertionPnt = APoint(-187, -110)
        insertionPnt2 = APoint(-187, -110)
        
        base_path = os.path.join(BASE_DIR, "blocks")
        block_configs = [
        (insertionPnt, os.path.join(base_path, "A4图框.dwg")),
        (insertionPnt2, os.path.join(base_path, f"{drawing_type}.dwg")),
        (insertionPnt2, os.path.join(base_path, f"{designer_name}.dwg"))
            ]       
        block_results = []
        for i, config in enumerate(block_configs, 1):
            print(f"  插入第 {i}/3 个图块...")
            result = safe_acad_operation(
                lambda c=config: self.insert_block(*c),
                f"插入图块 {i}/3",
                max_retries=3,
                retry_delay=1.0  # 增加重试延迟
            )
            block_results.append(result)
            time.sleep(1.5)  # 增加等待时间

        
        # 8. 缩放到范围
        print("缩放到范围...")
        safe_acad_operation(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.0)  # 增加等待时间
        
        # 9. 添加标题和自动生成的日期
        print("添加标题和日期...")
        self.filename=generate_filename(radius, chord_length, drawing_type=drawing_type)
        safe_acad_operation(
            lambda: self.date_name(name=self.filename),
            "添加标题和日期",
            max_retries=3,
            retry_delay=0.8
        )
        time.sleep(1.0)  # 增加等待时间

        return geometry, block_results
        
    def close(self) -> None:
        """关闭AutoCAD连接"""
        try:
            del self.acad
        except Exception:
            pass

if __name__ == "__main__":
    from draw import SwingMachineToolingCalculator
    
    lens_parameters = [
        {"R": 52.704, "blank_D": 22}]
        # 可以添加更多镜片参数：
 
    
    # 存储所有绘图参数
    drawing_parameters = []
    
    # 处理每组镜片参数
    for index, lens_param in enumerate(lens_parameters, 1):
        print(f"\n{'='*50}")
        print(f"正在处理第 {index}/{len(lens_parameters)} 组镜片参数...")
        print(f"镜片R值: {lens_param['R']}, 毛坯直径: {lens_param['blank_D']}")
        print(f"{'='*50}")
        
            # 创建计算器实例
        calculator = SwingMachineToolingCalculator(
                R=lens_param["R"],
                blank_D=lens_param["blank_D"],
                polyurethane_thickness=0.3,
                diamond_pellet_thickness=3,
                delta_arc=4
            )
            
            # 执行计算
        results = calculator.calculate_all(EXCEL_PATH)
        designer_name = "周凡"    
            # 从结果中提取参数以创建图形
        params_list = [
                # 1. 下摆机精磨基模
                {
                    "radius": results["下摆机精磨基模R值"],
                    "chord_length": results["下摆机精磨基模口径"],
                    # "a": DEFAULT_PARAM_A,
                    # "b": DEFAULT_PARAM_B,
                    # "c": DEFAULT_PARAM_C,
                    "drawing_type": "XJMJM",
                    "designer_name": designer_name,
                    
                },
                
                 {
                    "radius": results["下摆机抛光基模R值"],
                    "chord_length": results["下摆机抛光基模口径"],
                    "drawing_type": "XPMJM",
                    "designer_name": designer_name,
                    
                }, 
                {
                    "radius": results["镜片R值"],
                    "chord_length": results["基准模口径"],
                    "drawing_type": "JZM",
                    "designer_name": designer_name,
                   
                },
                {
                    "radius": - results["镜片R值"],
                    "chord_length": results["基准模口径"],
                    "drawing_type": "JZM",
                    "designer_name": designer_name,
                    
                },
      
                {
                    "radius": results["高速抛光修盘基模R值"],
                    "chord_length": results["高速抛光修盘基模口径"],
                    "drawing_type": "GPMXJ",
                    "designer_name": designer_name
                   
                },
                 {
                    "radius": results["高速抛光基模修盘R值"],
                    "chord_length": results["高速抛光基模修盘口径"],
                    "drawing_type": "GPMJX",
                    "designer_name": designer_name
                   
                }
            ]
      
        # 合并所有参数
        drawing_parameters.extend(params_list)
    # 批量创建图形
    for index, params in enumerate(drawing_parameters, 1):
        print(f"\n正在创建第 {index}/{len(drawing_parameters)} 个图形...")
        print(f"类型: {params['drawing_type']}, 半径={params['radius']:.2f}, 弦长={params['chord_length']:.2f}")
        
        try:
            drawing = AutoCadDrawing()
            created_file = drawing.create_drawing(**params)
            saved_file = drawing.save_drawing()
            
            if saved_file:
                print(f"✓ 图形创建并保存成功: {saved_file}")
            
        except Exception as error:
            print(f"✗ 图形创建失败，错误: {error}")
          
        finally:
            if drawing:
                print("关闭 AutoCAD 连接...")
                drawing.close()
                print("等待 AutoCAD 释放资源...")
                time.sleep(3.0)  # 增加等待时间，确保AutoCAD完全释放资源
            
            # 如果不是最后一个图形，额外等待一段时间
            if index < len(drawing_parameters):
                print(f"等待 {2.0} 秒后创建下一个图形...")
                time.sleep(2.0)
    
    