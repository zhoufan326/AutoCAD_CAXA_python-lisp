# 导入必要的模块
import math
import os
import sys
import time

# 路径配置 - 包内使用相对导入
from .utils import set_layer, create_hatch, retry
from .utils.scale_select import get_dimension_params
from pyautocad import APoint, Autocad

# 常量定义 - 支持 PyInstaller 打包后运行时路径
def _get_template_path():
    """获取模板文件路径（兼容 PyInstaller 打包环境）"""
    # PyInstaller 打包后，文件在 sys._MEIPASS 下
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    template = os.path.join(base, "新图样.dwt")
    if os.path.exists(template):
        return template
    
    # 备用路径
    fallback = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新图样.dwt")
    return os.path.abspath(fallback)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_PATH = _get_template_path()
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


class DrawLens:
    """镜片绘制类 - 用于在AutoCAD中绘制镜片图形"""
    
    def __init__(self, acad=None, template_path=TEMPLATE_PATH):
        """初始化 AutoCAD 连接"""
        if acad is None:
            self.acad = Autocad(create_if_not_exists=True)
            print("正在连接AutoCAD...")
            
            # 使用retry检查连接稳定性
            try:
                app_name = retry(
                    lambda: self.acad.app.Name,
                    operation_name="AutoCAD连接检查",
                    max_retries=5,
                    initial_delay=1.0
                )
                print(f"✓ AutoCAD连接稳定 (版本: {app_name})")
                # 连接稳定后，等待一小段时间确保完全初始化
                time.sleep(1.0)
            except Exception as e:
                print(f"⚠️  AutoCAD连接不稳定: {e}")
                # 再等待一段时间以增加连接成功的可能性
                time.sleep(2.0)
        else:
            self.acad = acad
            print("使用外部提供的AutoCAD连接")

        if template_path and os.path.exists(template_path):
            retry(
                lambda: self.acad.app.Documents.Add(template_path),
                "加载模板"
            )
            
            # 设置打印样式表和绘图仪
            try:
                # 获取当前文档
                doc = self.acad.doc
                
                # 获取活动布局
                active_layout = doc.ActiveLayout
                
                # 设置打印样式表为 monochrome.ctb
                active_layout.StyleSheet = "monochrome.ctb"
                
                # 设置绘图仪为 PublishToWeb PNG.pc3
                active_layout.ConfigName = "PublishToWeb PNG.pc3"
                doc.SetVariable("Filedia", 0)  # 禁用文件对话框
                doc.SetVariable("BACKGROUNDPLOT", 0)  # 前台打印
                print("✓ 打印设置已配置: 样式表=monochrome.ctb, 绘图仪=PublishToWeb PNG.pc3")
            except Exception as e:
                print(f"⚠️ 设置打印参数时发生错误: {e}")

    def calculate_sagitta(self, radius, diameter):
        """计算矢高"""
        if radius is None or diameter is None:
            return None
        half_chord = diameter / 2
        theta = math.asin(half_chord / abs(radius))
        sagitta = abs(radius) * (1 - math.cos(theta))
        return math.copysign(sagitta, radius)
    
    def draw_lens(self, parameter):
        """绘制单个镜片"""
        R1 = parameter["radius1"]
        R2 = parameter["radius2"]
        Tc = parameter["center_thickness"]
        sagitta1 = parameter.get("sagitta1")
        sagitta2 = parameter.get("sagitta2")
        D = parameter["outer_diameter"]
        base = parameter["base"]
        
        # 计算矢高（如果未提供）
        if sagitta1 is None:
            sagitta1 = self.calculate_sagitta(R1, D)
        if sagitta2 is None:
            sagitta2 = self.calculate_sagitta(R2, D)
        
        # 基准点设置
        base1 = base
        base2 = APoint(base1.x + Tc, base1.y)
        
        # 圆心计算
        C1 = APoint(base1.x + R1, base1.y)
        C2 = APoint(base2.x + R2, base2.y)
        
        # 角度计算（Zemax方式）
        theta1 = math.acos((R1 - sagitta1) / R1) if R1 != 0 else 0
        theta2 = math.acos((R2 - sagitta2) / R2) if R2 != 0 else 0
        
        start_angle1 = -theta1 if R1 < 0 else math.pi - theta1
        end_angle1 = +theta1 if R1 < 0 else math.pi + theta1
        start_angle2 = -theta2 if R2 < 0 else math.pi - theta2
        end_angle2 = +theta2 if R2 < 0 else math.pi + theta2
        
        # 根据镜片外径D动态计算所有相关参数
        text_height, hatch_scale, dim_style_name, linetype_scale = get_dimension_params(D)
        
        # 计算关键点坐标
        x1 = base1.x + sagitta1
        x2 = base2.x + sagitta2
        
        # 上下端点
        up1 = APoint(x1, D/2)
        down1 = APoint(x1, -D/2)
        up2 = APoint(x2, D/2)
        down2 = APoint(x2, -D/2)
        
        # 弧线与直线的连接点
        sp1y = abs(R1) * math.sin(start_angle1) + C1.y
        ep1y = abs(R1) * math.sin(end_angle1) + C1.y
        start_point1 = APoint(x1, sp1y)
        end_point1 = APoint(x1, ep1y)
        
        sp2y = abs(R2) * math.sin(start_angle2) + C2.y
        ep2y = abs(R2) * math.sin(end_angle2) + C2.y
        start_point2 = APoint(x2, sp2y)
        end_point2 = APoint(x2, ep2y)
        
        # 确定连接方向
        u1 = end_point1 if R1 < 0 else start_point1
        d1 = start_point1 if R1 < 0 else end_point1
        u2 = end_point2 if R2 < 0 else start_point2
        d2 = start_point2 if R2 < 0 else end_point2
        
        # 中心线参数
        extension = D / 3
        line_start = APoint(base1.x - extension, base1.y)
        line_end = APoint(base2.x + extension, base2.y)
        
        # 绘制轮廓线
        time.sleep(1)  # 等待前一个操作完成
        retry(lambda: set_layer("轮廓线"), "设置图层")
        time.sleep(1.5)  # 等待图层切换完成
        
        arc1 = self.acad.model.AddArc(C1, abs(R1), start_angle1, end_angle1)
        arc2 = self.acad.model.AddArc(C2, abs(R2), start_angle2, end_angle2)
        
        # 连接弧线的直线
        line1 = self.acad.model.AddLine(up1, up2)
        line2 = self.acad.model.AddLine(down1, down2)
        
        # 连接弧线与直线
        self.acad.model.AddLine(u1, up1)
        self.acad.model.AddLine(u2, up2)
        self.acad.model.AddLine(d1, down1)
        self.acad.model.AddLine(d2, down2)
        
        time.sleep(0.3)  # 等待密集对象创建完成
        
        retry(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围"
        )
        time.sleep(0.5)  # 等待视图更新完成
        
        # 绘制剖面线
        retry(lambda: set_layer("剖面线"), "设置图层")
        retry(
            lambda: create_hatch(self.acad, base1.x + Tc/2, base1.y+D/4, 
                                pattern="GOST_GLASS", scale=hatch_scale),
            "创建填充"
        )
        
        # 绘制中心线
        retry(lambda: set_layer("中心线"), "设置图层")
        center_line = self.acad.model.AddLine(line_start, line_end)
        center_line.LinetypeScale = linetype_scale
        time.sleep(0.3)  # 等待中心线创建完成
        
        # 绘制标注
        retry(lambda: set_layer("标注线"), "设置图层")
        created = [None] * 10
        
        try:
            # 半径标注
            # 第一面半径标注
            if R1 != 0:
                angle_rad1 = math.pi - theta1/3 if R1 > 0 else theta1/3
                chord_point = APoint(
                    C1.x + abs(R1) * math.cos(angle_rad1),
                    C1.y + abs(R1) * math.sin(angle_rad1)
                )
                created[2] = self.acad.model.AddDimRadial(C1, chord_point, D/30)
                created[2].StyleName = f"{dim_style_name}$4"  # 使用主样式名称加上半径标注子样式后缀
                created[2].Update()
                
                radius1_tolerance = parameter.get("radius1_tolerance")
                if radius1_tolerance is not None:
                    radius1_tolerance = round(radius1_tolerance, 3)
                    created[2].TextOverride = f"<>±{radius1_tolerance:.3f}"
                else:
                    created[2].TextOverride = "<>"
            
            # 第二面半径标注
            if R2 != 0:
                angle_rad2 = math.pi - theta2/3 if R2 > 0 else theta2/3
                chord_point = APoint(
                    C2.x + abs(R2) * math.cos(angle_rad2),
                    C2.y + abs(R2) * math.sin(angle_rad2)
                )
                created[3] = self.acad.model.AddDimRadial(C2, chord_point, D/30)
                created[3].StyleName = f"{dim_style_name}$4"  # 使用主样式名称加上半径标注子样式后缀
                created[3].Update()
                
                radius2_tolerance = parameter.get("radius2_tolerance")
                if radius2_tolerance is not None:
                    radius2_tolerance = round(radius2_tolerance, 3)
                    created[3].TextOverride = f"<>±{radius2_tolerance:.3f}"
                else:
                    created[3].TextOverride = "<>"
            
            # 设置全局标注样式
            dim_style = self.acad.ActiveDocument.DimStyles.Item(dim_style_name)
            self.acad.ActiveDocument.ActiveDimStyle = dim_style
            
            # 文字标注S1和S2
            text_s1_point = APoint(line_start.x+D/6, line_start.y + D/20)
            text_s2_point = APoint(line_end.x-D/6, line_end.y + D/20)
            self.acad.model.AddText("S1", text_s1_point, text_height)
            self.acad.model.AddText("S2", text_s2_point, text_height)
            
            # 中心厚度标注
            dim_line_loc = APoint((base1.x + base2.x)/2, -D/2 - D/5)
            created[1] = self.acad.model.AddDimRotated(base1, base2, dim_line_loc, 0)
            
            thickness_tolerance = parameter.get("thickness_tolerance")
            if thickness_tolerance is not None:
                created[1].TextOverride = f"<>±{thickness_tolerance:.2f}"
            else:
                created[1].TextOverride = "<>"
            
            # Te参考值
            dim_line_loc = APoint((up1.x + up2.x)/2, up1.y + D/5)
            created[4] = self.acad.model.AddDimRotated(up1, up2, dim_line_loc, 0)
            created[4].TextOverride = "(<>)"
            
            # 镜片外径标注
            if radius1_tolerance is not None:
                dim_line_loc = APoint(up1.x - 1.25*D, (up1.y + down1.y)/2)
            else:
                dim_line_loc = APoint(up1.x - 0.8*D, (up1.y + down1.y)/2)
            created[5] = self.acad.model.AddDimRotated(up1, down1, dim_line_loc, math.pi/2)

            # 检查是否存在上下公差
            upper_tolerance = parameter.get("upper_tolerance")
            lower_tolerance = parameter.get("lower_tolerance")
            
            if upper_tolerance is not None and lower_tolerance is not None:
                # 两个公差都存在，使用AutoCAD内置公差系统显示
                created[5].TextOverride = "%%C<>"
                created[5].ToleranceDisplay = 2  # 启用公差显示
                created[5].ToleranceUpperLimit = upper_tolerance
                created[5].ToleranceLowerLimit = lower_tolerance
                created[5].TolerancePrecision = 3  # 公差精度为3位小数
                created[5].ToleranceHeightScale = 0.7  # 公差文字高度比例
                created[5].Update()  # 更新标注
            else:
                # 至少有一个公差不存在，只显示基本尺寸,别忘了添加直径符号
                created[5].TextOverride = "%%C<>"
            
            # 矢高标注
            # 如果矢高1存在，则创建矢高标注   
            if parameter["sagitta1"] is not None:
                created[6] = self.acad.model.AddDimRotated(base1, down1, 
                                                      APoint(down1.x/2, down1.y-D/2 -D/5), 
                                                      math.pi/2)
                sagitta1_tolerance = parameter.get("sagitta1_tolerance")
                if sagitta1_tolerance is not None:
                    sagitta1_tolerance = round(sagitta1_tolerance, 3)
                    created[6].TextOverride = f"<>±{sagitta1_tolerance:.3f}"
                else:
                    created[6].TextOverride = "<>"
            
            # 如果矢高2存在，则创建矢高标注   
            if parameter["sagitta2"] is not None:
                created[7] = self.acad.model.AddDimRotated(base2, down2, 
                                                      APoint(down2.x/2, down2.y-D/2 -D/5), 
                                                      math.pi/2)
                sagitta2_tolerance = parameter.get("sagitta2_tolerance")
                if sagitta2_tolerance is not None:
                    sagitta2_tolerance = round(sagitta2_tolerance, 3)
                    created[7].TextOverride = f"<>±{sagitta2_tolerance:.3f}"
                else:
                    created[7].TextOverride = "<>"
             
        except Exception as error:
            print(f"添加标注时发生异常: {error}")
        
        return arc1, arc2, line1, line2
        


def draw_multiple_lenses(params_list):
    """使用给定的参数列表绘制多个镜片"""
   
    try:
        lens = DrawLens()
        for i, params in enumerate(params_list, 1):
            print(f"\n正在绘制第 {i}/{len(params_list)} 个镜片... 参数: R1={params['radius1']}, R2={params['radius2']}, D={params['outer_diameter']}")
            lens.draw_lens(params)
        return True
    except Exception as e:
        print(f"\n✗ 绘制错误: {e}")
        return False




def main():
    """主程序入口 - 启动GUI界面"""
    try:
        from .lens_gui import main as gui_main
        gui_main()
    except ImportError:
        print("无法导入GUI模块，直接使用命令行模式")


if __name__ == "__main__":
    main()
