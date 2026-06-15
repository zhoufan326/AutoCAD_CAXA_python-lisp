# 导入必要的模块
import math
import os
import sys
import time

# 路径配置 - 必须在导入本地模块之前设置
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from utils.com_interface import APoint, Autocad
from utils import set_layer, create_hatch, retry
from utils.scale_select import get_dimension_params

# 常量定义
if getattr(sys, 'frozen', False):
    TEMPLATE_PATH = os.path.join(sys._MEIPASS, "新图样.dwt")
else:
    TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "新图样.dwt")


class DrawLens:
    """镜片绘制类 - 用于在AutoCAD中绘制镜片图形"""
    
    def __init__(self, acad=None, template_path=TEMPLATE_PATH):
        """初始化 AutoCAD 连接"""
        if acad is None:
            self.acad = Autocad(create_if_not_exists=True)
            print("正在连接AutoCAD...")
            try:
                retry(
                    lambda: self.acad.app.Name,
                    operation_name="AutoCAD连接检查",
                    max_retries=5,
                    initial_delay=1.0
                )
            except Exception:
                pass
            time.sleep(1.0)
        else:
            self.acad = acad
            print("使用外部提供的AutoCAD连接")

        if template_path and os.path.exists(template_path):
            self.acad.app.Documents.Add(template_path)

        self.sagitta_warnings = []

    def calculate_sagitta(self, radius, diameter):
        """计算矢高"""
        if radius is None or diameter is None:
            return None
        if radius == 0:
            return 0.0
        half_chord = diameter / 2
        theta = math.asin(half_chord / abs(radius))
        sagitta = abs(radius) * (1 - math.cos(theta))
        return math.copysign(sagitta, radius)

    def _compute_surface(self, base_x, C, R, sagitta, D):
        """计算单个球面的角度与关键点坐标，返回 (theta, start, end, up, down, u, d)"""
        calc_sagitta = self.calculate_sagitta(R, D)
        if sagitta is None:
            sagitta = calc_sagitta
        elif abs(sagitta) > abs(calc_sagitta):
            self.sagitta_warnings.append(f"输入的矢高 ({sagitta:.3f}) 超过最大值 ({calc_sagitta:.3f})，已使用计算值")
            sagitta = calc_sagitta
        theta, start, end = self._calc_surface_angles(R, sagitta)
        chord = end if R < 0 else start
        x = base_x + sagitta
        y = abs(R) * math.sin(chord)
        return (theta, start, end,
                APoint(x, D/2), APoint(x, -D/2),
                APoint(x, y + C.y), APoint(x, -y + C.y))

    def _draw_outline(self, up1, up2, down1, down2, u1, u2, d1, d2):
        """绘制6条轮廓直线（上下边缘 + 弧线连接线）"""
        
        self.acad.AddLine(up1, up2)
        self.acad.AddLine(down1, down2)
        self.acad.AddLine(u1, up1)
        self.acad.AddLine(u2, up2)
        self.acad.AddLine(d1, down1)
        self.acad.AddLine(d2, down2)
        

    def _calc_surface_angles(self, R, sagitta):
        """计算单面的 theta 和起止角度（Zemax方式），返回 (theta, start_angle, end_angle)"""
        theta = math.acos((R - sagitta) / R) if R != 0 else 0
        start_angle = -theta if R < 0 else math.pi - theta
        end_angle = +theta if R < 0 else math.pi + theta
        return theta, start_angle, end_angle

    def _add_radius_dim(self, C, theta, R, tolerance_key, D, dim_style_name, leaderlength):
        """添加单一镜面的半径标注（角度计算方式同Zemax），返回标注对象"""
        if R == 0:
            return None
        angle_rad = math.pi - theta/3 if R > 0 else theta/3
      
        chord_point = APoint(
            C.x + abs(R) * math.cos(angle_rad),
            C.y + abs(R) * math.sin(angle_rad)
        )
        dim = self.acad.AddDimRadial(C, chord_point, leaderlength)
        dim.StyleName = f"{dim_style_name}$4"

        tol = self.cur_param.get(tolerance_key)
        dim.TextOverride = f"<>±{round(tol, 3):.3f}" if tol is not None else "<>"
        dim.Update()
        return dim

    def _add_sagitta_dim(self, base, down, tolerance_key):
        """添加单一镜面的矢高标注，返回标注对象"""
        D = self.cur_param["outer_diameter"]
        dim = self.acad.AddDimRotated(
            base, down,
            APoint(down.x/2, down.y - D/2 ),
            math.pi
        )
        tol = self.cur_param.get(tolerance_key)
        dim.TextOverride = f"<>±{round(tol, 3):.3f}" if tol is not None else "<>"
        dim.Update()
        return dim
    
    def draw_lens(self, parameter):
        """绘制单个镜片"""
        self.cur_param = parameter  # 供辅助方法读取公差等参数
        R1 = parameter["radius1"]
        R2 = parameter["radius2"]
        Tc = parameter["center_thickness"]
        sagitta1 = parameter.get("sagitta1")
        sagitta2 = parameter.get("sagitta2")
        D = parameter["outer_diameter"]
        base = parameter["base"]
        Min_D = parameter.get("outer_diameter_min")
        Min_sagitta1 = parameter.get("Minsagitta1")
        Min_sagitta2 = parameter.get("Minsagitta2")

        # 基准点设置
        base1 = base
        base2 = APoint(base1.x + Tc, base1.y)

        # 圆心计算
        C1 = APoint(base1.x + R1, base1.y)
        C2 = APoint(base2.x + R2, base2.y)

        theta1, start1, end1, up1, down1, u1, d1 = self._compute_surface(base1.x, C1, R1, sagitta1, D)
        theta2, start2, end2, up2, down2, u2, d2 = self._compute_surface(base2.x, C2, R2, sagitta2, D)
        #绘制直线
        set_layer("轮廓线")
        self._draw_outline(up1, up2, down1, down2, u1, u2, d1, d2)

        if R1 != 0:
            self.acad.AddArc(C1, abs(R1), start1, end1)
        else:
            self.acad.AddLine(u1, d1)
        if R2 != 0:
            self.acad.AddArc(C2, abs(R2), start2, end2)
        else:
            self.acad.AddLine(u2, d2)

        if Min_D is not None:
            _, _, _, min_up1, min_down1, min_u1, min_d1 = self._compute_surface(base1.x, C1, R1, Min_sagitta1, Min_D)
            _, _, _, min_up2, min_down2, min_u2, min_d2 = self._compute_surface(base2.x, C2, R2, Min_sagitta2, Min_D)
            #绘制额外的直线
            set_layer("细实线")
            self._draw_outline(min_up1, min_up2, min_down1, min_down2, min_u1, min_u2, min_d1, min_d2)

        self.acad.doc.SendCommand("_.zoom _e ")

        # 根据镜片外径D动态计算所有相关参数
        text_height, hatch_scale, dim_style_name, linetype_scale = get_dimension_params(D, Tc)

        # 中心线参数
        extension = D / 3
        line_start = APoint(base1.x - extension, base1.y)
        line_end = APoint(base2.x + extension, base2.y)
        
        # 绘制剖面线
        set_layer("剖面线")
        create_hatch(self.acad, base1.x + Tc/2, base1.y+D/4, 
                     pattern="GOST_GLASS", scale=hatch_scale)
        
        # 绘制中心线
        set_layer("中心线")
        center_line = self.acad.AddLine(line_start, line_end)
        center_line.LinetypeScale = linetype_scale
        
        # 绘制标注
        set_layer("标注线")
        
        try:
            # 半径标注 — 第一面 (R1) / 第二面 (R2)  #引线长度为负值时在圆弧内侧，反之在圆弧外侧
            leaderlength = D/30  if R1 > 0 else -D/30
            self._add_radius_dim(C1, theta1, R1, "radius1_tolerance", D, dim_style_name, leaderlength)
            
            leaderlength = -D/30  if R2 > 0 else D/30
            self._add_radius_dim(C2, theta2, R2, "radius2_tolerance", D, dim_style_name, leaderlength)
            
            # 设置全局标注样式
            dim_style = self.acad.ActiveDocument.DimStyles.Item(dim_style_name)
            self.acad.ActiveDocument.ActiveDimStyle = dim_style
            
            # 文字标注S1和S2
            text_s1_point = APoint(line_start.x+D/6, line_start.y + D/20)
            text_s2_point = APoint(line_end.x-D/6, line_end.y + D/20)
            self.acad.AddText("S1", text_s1_point, text_height)
            self.acad.AddText("S2", text_s2_point, text_height)
            
            # 中心厚度标注
            dim_line_loc = APoint((base1.x + base2.x)/2, -D/2 - D/5)
            dim_tc = self.acad.AddDimRotated(base1, base2, dim_line_loc, 0)
            thickness_tolerance = parameter.get("thickness_tolerance")
            dim_tc.TextOverride = f"<>±{thickness_tolerance:.3f}" if thickness_tolerance is not None else "<>"
            dim_tc.Update()
            
            # Te参考值
            dim_line_loc = APoint((up1.x + up2.x)/2, up1.y + D/5)
            dim_te = self.acad.AddDimRotated(up1, up2, dim_line_loc, 0)
            dim_te.TextOverride = "(<>)"

            # 镜片外径标注（有R1公差时标注线左移更多，给公差文字留空间）
            dim_line_loc = APoint(up1.x - (1.25*D if self.cur_param.get("radius1_tolerance") is not None else 0.8*D),
                                  base1.y)
            dim_outer = self.acad.AddDimRotated(up1, down1, dim_line_loc, math.pi/2)

            # 检查是否存在上下公差
            upper_tolerance = parameter.get("upper_tolerance")
            lower_tolerance = parameter.get("lower_tolerance")
            
            if upper_tolerance is not None and lower_tolerance is not None:
                dim_outer.TextOverride = "%%C<>"
                dim_outer.ToleranceDisplay = 2
                dim_outer.ToleranceUpperLimit = upper_tolerance
                dim_outer.ToleranceLowerLimit = lower_tolerance
                dim_outer.TolerancePrecision = 3
                dim_outer.ToleranceHeightScale = 1
                dim_outer.Update()
            else:
                dim_outer.TextOverride = "%%C<>"

            
            if Min_D is not None:
                # 最小外径标注（仅当提供了最小外径时）
                dim_line_loc = APoint(min_up1.x -  0.7*Min_D, base1.y)
                dim_min_outer = self.acad.AddDimRotated(min_up1, min_down1, dim_line_loc, math.pi/2)
                dim_min_outer.TextOverride = "%%C<>"
                min_upper = parameter.get("outer_diameter_min_upper_tolerance")
                min_lower = parameter.get("outer_diameter_min_lower_tolerance")
                if min_upper is not None and min_lower is not None:
                    dim_min_outer.ToleranceDisplay = 2
                    dim_min_outer.ToleranceUpperLimit = min_upper
                    dim_min_outer.ToleranceLowerLimit = min_lower
                    dim_min_outer.TolerancePrecision = 3
                    dim_min_outer.ToleranceHeightScale = 1
                    dim_min_outer.Update()

                # 最小内径标注（仅当提供了最小矢高时），S1和S2的最小内径标注分别绘制
                if parameter["Minsagitta1"] is not None:
                    dim_line_loc = APoint(min_u1.x - 0.5*Min_D, base1.y)
                    dim_min_inner = self.acad.AddDimRotated(min_u1, min_d1, dim_line_loc, math.pi/2)
                    dim_min_inner.TextOverride = "最小内径%%C<>"
                    dim_min_inner.Update()
                if parameter["Minsagitta2"] is not None:
                    dim_line_loc = APoint(min_u2.x + 0.5*Min_D, base2.y)
                    dim_min_inner = self.acad.AddDimRotated(min_u2, min_d2, dim_line_loc, math.pi/2)
                    dim_min_inner.TextOverride = "最小内径%%C<>"
                    dim_min_inner.Update()


            # 矢高标注 — S1 / S2，当且仅当最小外径存在时绘制
            if Min_D is None:
                if parameter["sagitta1"] is not None:
                    self._add_sagitta_dim(base1, down1, "sagitta1_tolerance")
                if parameter["sagitta2"] is not None:
                    self._add_sagitta_dim(base2, down2, "sagitta2_tolerance")
            
        except Exception as error:
            print(f"添加标注时发生异常: {error}")
        
       
        




def draw_multiple_lenses(params_list):
    """使用给定的参数列表绘制多个镜片，返回 (success, warnings)"""
   
    try:
        lens = DrawLens()
        for i, params in enumerate(params_list, 1):
            print(f"\n正在绘制第 {i}/{len(params_list)} 个镜片... 参数: R1={params['radius1']}, R2={params['radius2']}, D={params['outer_diameter']}")
            lens.draw_lens(params)
        return True, lens.sagitta_warnings
    except Exception as e:
        print(f"\n[ERR] 绘制错误: {e}")
        return False, []




def main():
    """主程序入口 - 启动GUI界面"""
    try:
        from lens_gui import main as gui_main
        gui_main()
    except ImportError:
        print("无法导入GUI模块，直接使用命令行模式")


if __name__ == "__main__":
    main()

__version__ = "0.3.1"