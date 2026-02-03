# 导入必要的模块
import math  # 数学计算模块
import os    # 文件系统操作模块
import sys   # 系统模块
import time  # 时间管理模块
import traceback  # 异常跟踪模块
from typing import Optional  # 类型提示模块
from pyautocad import APoint, Autocad  # AutoCAD操作模块

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from utils import set_layer, create_hatch, safe_acad_operation, date_name  # 工具函数模块

# 常量定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")  # 默认模板文件路径
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")  # 默认保存目录


class DrawLens:
    """镜片绘制类 - 用于在AutoCAD中绘制镜片图形
    半径的正负参考Zemax，即圆心在左侧时，半径为负，圆心在右侧时，半径为正"""       
    
    def __init__(self, acad=None, template_path=DEFAULT_TEMPLATE_PATH):
        """
        初始化 DrawLens 类
        
        参数:
            acad: AutoCAD 连接对象，如果为 None 则自动创建
            template_path: 模板文件路径，用于创建新的AutoCAD文档
        """
        # 初始化AutoCAD连接
        if acad is None:
            self.acad = Autocad(create_if_not_exists=True)
            print("正在连接AutoCAD...")
            time.sleep(2)  # 增加等待时间确保AutoCAD完全启动
        else:
            self.acad = acad

        # 加载模板文件
        if template_path and os.path.exists(template_path):
            print(f"使用模板: {template_path}")
            safe_acad_operation(
                lambda: self.acad.app.Documents.Add(template_path),
                "模板加载",
                max_retries=3,
                retry_delay=2.0
            )
            print("模板加载成功")
            time.sleep(1.5)
        
        # 绑定工具函数
        self.set_layer = set_layer
    
    def calculate_sagitta(self, radius, diameter):
        """计算矢高
        
        参数:
            radius: 球面半径
            diameter: 直径
            
        返回:
            float: 计算得到的矢高值
        """
        if radius is None or diameter is None:
            return None
        # 矢高计算公式: h = R - √(R² - (D/2)²)
        half_chord = diameter / 2
        # 利用三角函数：矢高 h = R * (1 - cos(θ))，其中 θ = arcsin(half_chord / |R|)
        theta = math.asin(half_chord / abs(radius))
        sagitta = abs(radius) * (1 - math.cos(theta))
        # 矢高与半径同号
        return math.copysign(sagitta, radius)
    
    def draw_lens(self, parameter):
        """绘制单个镜片
        
        参数:
            parameter: 包含镜片参数的字典
            
        返回:
            tuple: 绘制的AutoCAD对象 (arc1, arc2, line1, line2)
        """
        # 设置图层为轮廓线
        self.set_layer("轮廓线")
        
        # 提取参数
        R1 = parameter["radius1"]  # 第一面曲率半径
        R2 = parameter["radius2"]  # 第二面曲率半径
        Tc = parameter["center_thickness"]  # 中心厚度
        sg1 = parameter["sagitta1"]  # 第一面矢高
        sg2 = parameter["sagitta2"]  # 第二面矢高
        D = parameter["outer_diameter"]  # 外径
        base = parameter["base"]  # 基准点
        
        # 如果矢高未提供，自动计算
        if sg1 is None:
            sg1 = self.calculate_sagitta(R1, D)
            print(f"计算镜面1矢高: {sg1:.3f}mm")
        
        if sg2 is None:
            sg2 = self.calculate_sagitta(R2, D)
            print(f"计算镜面2矢高: {sg2:.3f}mm")
        
        # 计算基准点坐标
        base1=base
        base2=APoint(base1.x + Tc, base1.y)
        
        # 计算圆心坐标
        center1_x, center1_y = base1.x + R1, base1.y
        center2_x, center2_y = base2.x + R2, base2.y
        #由于采用Zemax中的半径定义，所以圆心在左侧时，半径为负，圆心在右侧时，半径为正，简化确定圆心位置的方法
        C1 = APoint(center1_x, center1_y)
        C2 = APoint(center2_x, center2_y)
        
        # 计算圆弧角度
        theta1 = math.acos((R1 - sg1) / R1) if R1 != 0 else 0
        theta2 = math.acos((R2 - sg2) / R2) if R2 != 0 else 0
        
        # 确定圆弧绘制方向
        start_angle1 =  - theta1 if R1 < 0 else math.pi - theta1
        end_angle1 =  + theta1 if R1 < 0 else math.pi + theta1
        start_angle2 =  - theta2 if R2 < 0 else math.pi - theta2
        end_angle2 =  + theta2 if R2 < 0 else math.pi + theta2
        
        # 绘制圆弧
        arc1 = self.acad.model.AddArc(C1, abs(R1), start_angle1, end_angle1)
        arc2 = self.acad.model.AddArc(C2, abs(R2), start_angle2, end_angle2)
        
        # 计算直线端点，矢高sg1与sg2与半径符号相同，采用Zemax中的定义
        x1 = base1.x + sg1
        x2 = base2.x + sg2
        up1 = APoint(x1, D/2)
        down1 = APoint(x1, -D/2)
        up2 = APoint(x2, D/2)
        down2 = APoint(x2, -D/2)
        
        # 绘制直线
        line1 = self.acad.model.AddLine(up1, up2)
        line2 = self.acad.model.AddLine(down1, down2)
        
        # 计算镜面端点
        sp1y = abs(R1) * math.sin(start_angle1) + center1_y
        ep1y = abs(R1) * math.sin(end_angle1) + center1_y
        start_point1 = APoint(x1, sp1y)
        end_point1 = APoint(x1, ep1y)
        
        sp2y = abs(R2) * math.sin(start_angle2) + center2_y
        ep2y = abs(R2) * math.sin(end_angle2) + center2_y
        start_point2 = APoint(x2, sp2y)
        end_point2 = APoint(x2, ep2y)
        
        # 确定侧面线连接点
        u1 = end_point1 if R1 < 0 else start_point1
        #半径小于0时，圆弧终点在上方，起点在下方，大于0时相反
        d1 = start_point1 if R1 < 0 else end_point1
        u2 = end_point2 if R2 < 0 else start_point2
        d2 = start_point2 if R2 < 0 else end_point2
        
        # 绘制侧面线
        self.acad.model.AddLine(u1, up1)
        self.acad.model.AddLine(u2, up2)
        self.acad.model.AddLine(d1, down1)
        self.acad.model.AddLine(d2, down2)
        
        # 缩放视图到合适大小
        print("调整视图...")
        safe_acad_operation(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围",
            max_retries=3,
            retry_delay=1.0
        )
        time.sleep(0.5)
        
        # 绘制剖面线
        self.set_layer("剖面线")
        internal_x, internal_y = base1.x + Tc/2, base1.y
        # 根据外径D自动设置剖面线比例
        scale = 0.25 if D < 40 else 0.5 if D < 100 else 1
        safe_acad_operation(
            lambda: create_hatch(self.acad, internal_x, internal_y, pattern="GOST_GLASS", scale=scale),
            "创建填充",
            max_retries=3,
            retry_delay=1.0
        )
        
        # 添加标注
        self.set_layer("标注线")
        created = [None] * 10  # 初始化10个标注对象
        
        try:
            # 1. 中心厚度标注（对称偏差）
            try:
                dim_line_loc = APoint((base1.x + base2.x)/2, -D/2 - 3)
                created[1] = self.acad.model.AddDimRotated(base1, base2, dim_line_loc, 0)
                # 设置标注样式为"镜片标注"
                created[1].StyleName = "镜片标注"
                # 获取厚度偏差值，默认为±0.02
                thickness_tolerance = parameter.get("thickness_tolerance", 0.02)
                # 其他标注的偏差值的精度设置为0.01
                thickness_tolerance = round(thickness_tolerance, 2)
                # 设置对称偏差格式
                created[1].TextOverride = f"<>\n±{thickness_tolerance:.2f}"
            except Exception:
                created[1] = None
            
            # 2. Te参考值（up1与up2之间）
            try:
                dim_line_loc = APoint((up1.x + up2.x)/2, up1.y + 10)
                created[4] = self.acad.model.AddDimRotated(up1, up2, dim_line_loc, 0)
                # 设置标注样式为"镜片标注"
                created[4].StyleName = "镜片标注"
                created[4].TextOverride = "(<>)."
            except Exception:
                created[4] = None
            
            # 3. 镜片外径标注
            try:
                dim_line_loc = APoint(up1.x - 3, (up1.y + down1.y)/2)
                created[5] = self.acad.model.AddDimRotated(up1, down1, dim_line_loc, math.pi/2)
                # 设置标注样式为"镜片标注"
                created[5].StyleName = "镜片标注"
                # 获取偏差值，默认为0
                upper_tolerance = parameter.get("upper_tolerance", 0.0)
                lower_tolerance = parameter.get("lower_tolerance", 0.0)
                # 其他标注的偏差值的精度设置为0.01
                upper_tolerance = round(upper_tolerance, 2)
                lower_tolerance = round(lower_tolerance, 2)
                # 设置极限偏差格式
                created[5].TextOverride = f"<>\n+{upper_tolerance:.2f}\n{lower_tolerance:.2f}"
            except Exception:
                created[5] = None
            
            # 4. 第一面半径标注（对称偏差）
            try:
                if R1 != 0:
                    angle_rad = math.radians(15 if R1 > 0 else 105)
                    chord_point = APoint(
                        C1.x + abs(R1) * math.cos(angle_rad),
                        C1.y + abs(R1) * math.sin(angle_rad)
                    )
                    created[2] = self.acad.model.AddDimRadial(C1, chord_point, 15)
                    # 设置标注样式为"镜片标注"
                    created[2].StyleName = "镜片标注"
                    created[2].TextPosition =  APoint(-10, 1) + chord_point
                    # 获取半径偏差值，默认为0
                    radius_tolerance = parameter.get("radius_tolerance", 0.0)
                    # 半径标注偏差值的精度设置为0.001
                    radius_tolerance = round(radius_tolerance, 3)
                    # 设置对称偏差格式
                    created[2].TextOverride = f"<>\n±{radius_tolerance:.3f}"
            except Exception:
                created[2] = None
            
            # 5. 第二面半径标注（对称偏差）
            try:
                if R2 != 0:
                    angle_rad = math.radians(15 if R2 > 0 else 105)
                    chord_point = APoint(
                        C2.x + abs(R2) * math.cos(angle_rad),
                        C2.y + abs(R2) * math.sin(angle_rad)
                    )
                    created[3] = self.acad.model.AddDimRadial(C2, chord_point, 15)
                    # 设置标注样式为"镜片标注"
                    created[3].StyleName = "镜片标注"
                    created[3].TextPosition = APoint(10, 1) + chord_point
                    # 获取半径偏差值，默认为0
                    radius_tolerance = parameter.get("radius_tolerance", 0.0)
                    # 半径标注偏差值的精度设置为0.001
                    radius_tolerance = round(radius_tolerance, 3)
                    # 设置对称偏差格式
                    created[3].TextOverride = f"<>\n±{radius_tolerance:.3f}"
            except Exception:
                created[3] = None
                
        except Exception as error:
            print(f"添加标注时发生异常: {error}")
        
        print(f"镜片绘制完成: R1={R1}, R2={R2}, D={D}")

        return arc1, arc2, line1, line2


def run_with_gui(params_list=None):
    """
    使用GUI配置参数并运行绘图
    
    参数:
        params_list: 可选的参数列表，默认使用内置的三组参数
    """
    try:
        from gui_config import configure_params_gui  # 导入GUI配置模块
    except ImportError:
        print("错误: 找不到gui_config模块")
        return
    
    # 如果没有提供参数列表，直接传递None，让gui_config.py使用存储的参数
    # 移除了硬编码的默认参数，优先使用用户保存的参数
    
    # 打印标题
    print("=" * 50)
    print("镜片参数配置工具")
    print("=" * 50)
    
    # 运行GUI配置
    confirmed, configured_params = configure_params_gui(params_list)
    
    if confirmed and configured_params:
        print(f"\n成功配置 {len(configured_params)} 个镜片参数")
        
        try:
            # 创建并使用DrawLens实例
            lens = DrawLens()
            
            # 逐个绘制镜片
            for index, params in enumerate(configured_params, 1):
                print(f"\n正在绘制第 {index}/{len(configured_params)} 个镜片...")
                print(f"参数: R1={params['radius1']}, R2={params['radius2']}, D={params['outer_diameter']}")
                
                # 绘制并计时
                start_time = time.time()
                lens.draw_lens(params)
                print(f"✓ 第 {index} 个镜片绘制成功 (耗时: {time.time() - start_time:.1f}秒)")
                
        except Exception as e:
            print(f"\n✗ 绘制过程中出现错误: {str(e)}")
            
        finally:
            print("\nAutoCAD操作完成，保持窗口打开以供查看...")
          
    else:
        print("\n配置已取消")


def run_demo():
    """运行演示（不使用GUI）
    
    直接使用默认参数绘制一个镜片，用于快速测试功能
    """
    print("运行演示模式...")
    
    # 直接使用默认参数绘制
    params = {
        "base": APoint(0, 0),
        "radius1": -28.11,
        "radius2": 28,
        "outer_diameter": 11.5,
        "center_thickness": 5,
        "edge_thickness": 5.3,
        "sagitta1": -0.316,
        "sagitta2": None,
        "inner_diameter_S1": None,
        "inner_diameter_S2": None
    }
    
    try:
        # 创建实例并绘制
        lens = DrawLens()
        lens.draw_lens(params)
        print("演示完成")
    except Exception as e:
        print(f"演示失败: {str(e)}")


if __name__ == "__main__":
    """主程序入口
    
    根据命令行参数选择运行模式：
    - 无参数: 运行GUI配置模式
    - --demo: 运行演示模式
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()  # 运行演示模式
    else:
        run_with_gui()  # 默认运行GUI配置模式