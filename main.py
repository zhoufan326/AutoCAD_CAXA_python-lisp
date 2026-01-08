from pyautocad import Autocad, APoint
import math
import os
import sys
from datetime import datetime

# 导入重构的模块
from geometry import calculate_geometry, generate_filename
from drawing_operations import DrawingOperations

class AutoCadDrawing:
    def __init__(self, template_path=None):
        import os
        
        # 修正路径
        if template_path:
            template_path = os.path.normpath(template_path)
        
        try:
            # 创建AutoCAD连接
            self.acad = Autocad(create_if_not_exists=True)
            
            # 如果有模板，创建新文档
            if template_path and os.path.exists(template_path):
                print(f"使用模板: {template_path}")
                # 直接创建新文档，原文档会被自动关闭或保留
                self.acad.doc = self.acad.app.Documents.Add(template_path)
                self.acad.app.ActiveDocument = self.acad.doc
            
            print(f"当前文档: {self.acad.doc.Name}")
            
        except Exception as e:
            print(f"错误: {e}")
            # 如果失败，尝试默认方式
            self.acad = Autocad(create_if_not_exists=True)
        
        # 加载其他模块
        self.load_modules()
        
        # 初始化绘图操作类
        self.drawing_ops = DrawingOperations(self.acad, self.set_layer)
    
    def load_modules(self):
        """加载所有依赖模块"""
        try:
            from fast_hatch import create_hatch
            self.create_hatch_func = create_hatch
        except:
            self.create_hatch_func = lambda acad, scale: None
        
        try:
            import blocks
            from blocks import insert_block, insert_XJMJM, insert_Zhoufan
            self.insert_block = insert_block
            self.insert_XJMJM = insert_XJMJM
            self.insert_Zhoufan = insert_Zhoufan
        except Exception as e:
            print(f"Warning: Blocks module not found - {e}")
            self.insert_block = lambda pnt: None
            self.insert_XJMJM = lambda pnt: None
            self.insert_Zhoufan = lambda pnt: None
        
        try:
            from layer import set_layer
            self.set_layer = set_layer
        except:
            self.set_layer = lambda name: None
        
        try:
            import dimension
            from dimension import dimension, date_name
            self.dimension = dimension
            self.date_name = date_name
        except:
            self.dimension = lambda *args: None
            self.date_name = lambda **kwargs: None
    
    def add_dimensions(self, geom):
        """添加尺寸标注"""
        self.set_layer("尺寸线")
        self.dimension(geom["left_point"], geom["right_point"], 
                      geom["a"], geom["b"], geom["c"],
                      geom["center"], geom["abs_radius"], geom["center2"])
    
    def add_title(self, name):
        """添加标题，使用当前日期"""
        # 获取当前日期
        current_date = datetime.now()
        date_str = current_date.strftime("%Y/%m/%d")
        
        # 调用date_name函数，传入当前日期
        self.date_name(date1=date_str, date2=date_str, name=name)
    
    def save_drawing(self, radius, chord_length, save_dir="D:\\CAD"):
        """保存图纸"""
        import os
        
        # 创建目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件路径
        filename = generate_filename(radius, chord_length)
        if not filename.endswith('.dwg'):
            filename += '.dwg'
        filepath = os.path.join(save_dir, filename)
        
        # 直接保存
        try:
            self.acad.doc.SaveAs(filepath, 60)
            print(f"保存成功: {filepath}")
            return filepath
        except:
            # 备用方案
            self.acad.doc.SendCommand(f'._saveas "60" "{filepath}"\n\n')
            return filepath if os.path.exists(filepath) else None
    
    def create_drawing(self, radius, chord_length, a=3, b=6, c=25, type="XJMJM"):
        """创建完整图纸"""
        # 1. 计算几何参数
        geom = calculate_geometry(radius, chord_length, a, b, c)
        
        # 2. 绘制主视图
        self.drawing_ops.draw_main_view(geom)
        
        # 3. 绘制中心线
        self.drawing_ops.draw_center_line(geom["abs_radius"])
        
        # 4. 绘制俯视图
        self.drawing_ops.draw_top_view(geom)
        
        # 5. 添加剖面线
        self.drawing_ops.add_hatching(self.create_hatch_func)
        
        # 6. 添加尺寸标注
        self.add_dimensions(geom)
        
        # 7. 插入图块
        self.drawing_ops.insert_all_blocks(
            geom, 
            self.insert_block, 
            self.insert_XJMJM, 
            self.insert_Zhoufan
        )
        
        # 8. 缩放视图
        self.acad.doc.SendCommand("_.zoom _e ")
        
        # 9. 添加标题（使用自动生成的日期）
        # generate_filename 接受 (radius, chord_length)，不含 type 参数
        # 将 type 作为前缀拼接到标题中
        self.add_title(f"{type}/{generate_filename(radius, chord_length)}")
        
        return geom
    
    def close(self):
        """关闭连接"""
        try:
            del self.acad
        except:
            pass

# 主函数
def create_new_drawing(radius, chord_length, a=3, b=6, c=25, type="XJMJM", save_dir=None):
    """创建新图纸的入口函数"""
    if save_dir is None:
        save_dir = "D:\\CAD\\test"
    
    drawing = None
    try:
        drawing = AutoCadDrawing(template_path=r"D:\CAD\新图样.dwt")
        drawing.create_drawing(radius, chord_length, a, b, c, type)
        return drawing.save_drawing(radius, chord_length, save_dir)
    
    finally:
        if drawing:
            drawing.close()

if __name__ == "__main__":
    from Tool_calculation import SwingMachineToolingCalculator
    
    # 定义镜片参数（R值和毛坯口径）
    # 默认输入一组镜片参数，生成6个图纸
    # 可以添加多组镜片参数，生成多组图纸
    lens_params = [
        {"R": 52.704, "blank_D": 22}
        # 可以添加更多镜片参数，例如：
        # {"R": 45.5, "blank_D": 20},
        # {"R": 38.2, "blank_D": 18},
    ]
    
    excel_path = "Z:/AutoCAD_AI/口径常数.xlsx"
    save_dir = "D:\\CAD\\test"
    
    # 固定参数
    a = 3
    b = 6
    c = 25
    
    # 存储所有图纸参数
    drawing_params = []
    
    # 对每组镜片参数进行计算
    for i, lens_param in enumerate(lens_params, 1):
        print(f"\n{'='*50}")
        print(f"正在计算第 {i}/{len(lens_params)} 组镜片参数...")
        print(f"镜片R值: {lens_param['R']}, 毛坯口径: {lens_param['blank_D']}")
        print(f"{'='*50}")
        
        try:
            # 创建计算器实例
            calculator = SwingMachineToolingCalculator(
                R=lens_param["R"],
                blank_D=lens_param["blank_D"],
                polyurethane_thickness=0.3,
                diamond_pellet_thickness=3,
                delta_arc=4
            )
            
            # 执行计算
            results = calculator.calculate_all(excel_path)
            
            # 从计算结果中提取参数创建6个图纸
            # 前4组：不同工装类型
            params_list = [
                # 1. 下摆机精磨基模
                {
                    "radius": results["下摆机精磨基模R值"],
                    "chord_length": results["下摆机精磨基模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "XJMJM",
                    "save_dir": save_dir
                },
                # 2. 下摆机抛光基模
                {
                    "radius": results["下摆机抛光基模R值"],
                    "chord_length": results["下摆机抛光基模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "XPMJM",
                    "save_dir": save_dir
                },
                # 3. 高速抛光修盘基模
                {
                    "radius": results["高速抛光修盘基模R值"],
                    "chord_length": results["高速抛光修盘基模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "GPMXJ",
                    "save_dir": save_dir
                },
                # 4. 抛光基模修改模
                {
                    "radius": results["抛光基模修改模R值"],
                    "chord_length": results["抛光基模修改模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "XPMJM",
                    "save_dir": save_dir
                },
                # 5. 基准模（正R值）
                {
                    "radius": results["镜片R值"],
                    "chord_length": results["基准模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "JZM",
                    "save_dir": save_dir
                },
                # 6. 基准模（负R值）
                {
                    "radius": -results["镜片R值"],
                    "chord_length": results["基准模口径"],
                    "a": a,
                    "b": b,
                    "c": c,
                    "type": "JZM",
                    "save_dir": save_dir
                }
            ]
            
            drawing_params.extend(params_list)
            print(f"✓ 第 {i} 组镜片参数计算完成，生成 {len(params_list)} 个图纸参数")
            
        except Exception as e:
            print(f"✗ 第 {i} 组镜片参数计算失败: {e}")
    
    # 批量创建图纸
    print(f"\n{'='*50}")
    print(f"开始批量创建图纸，共 {len(drawing_params)} 个")
    print(f"{'='*50}")
    
    success_count = 0
    fail_count = 0
    failed_files = []
    
    for i, params in enumerate(drawing_params, 1):
        print(f"\n正在创建第 {i}/{len(drawing_params)} 个图纸...")
        print(f"类型: {params['type']}, radius={params['radius']:.2f}, chord_length={params['chord_length']:.2f}")
        
        try:
            saved_file = create_new_drawing(**params)
            if saved_file:
                print(f"✓ 图纸创建成功: {saved_file}")
                success_count += 1
            else:
                print(f"✗ 图纸创建失败")
                fail_count += 1
                failed_files.append(params)
        except Exception as e:
            print(f"✗ 图纸创建失败，错误: {e}")
            fail_count += 1
            failed_files.append(params)
    
    # 输出统计信息
    print(f"\n{'='*50}")
    print(f"批量创建完成！")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"{'='*50}")
    
    if failed_files:
        print("\n失败的图纸参数:")
        for i, params in enumerate(failed_files, 1):
            print(f"{i}. 类型={params['type']}, radius={params['radius']:.2f}, chord_length={params['chord_length']:.2f}")