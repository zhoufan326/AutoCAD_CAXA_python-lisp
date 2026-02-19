# draw_top_view.py - 绘制俯视图模块
import math
from pyautocad import APoint, aDouble
from dimension import dia
from utils import LD, AD, CD, set_layer


def draw_top_view(self):
    """绘制俯视图
    1. 绘制中心小圆
    2. 绘制中心圆弧(优弧，并标注弦长)
    3. 标注直径
    由于俯视图不常用，所以直接将绘图与标注集成在一起。
    """
    radius = self.radius
    # 中心点（用于俯视图），使用 geometry 中计算的 center2
    center_top = APoint(0, -40) + self.center2
    
    # 使用CD函数绘制中心小圆并添加标注
    leader_length = 5
    circle, dim_circle = CD(self.acad, center_top, 4, -math.pi/6, leader_length, layer="虚线")
    circle.LinetypeScale = 0.2
    dim_circle.Layer = "虚线"
    circle.Update()
    # 中心圆弧,优弧
    radius_down2 = 9
    chord_length2 = 6
    half_chord2 = chord_length2 / 2
    half_theta_rad2 = math.asin(half_chord2 / radius_down2)
    chord_to_center = radius_down2 * math.cos(half_theta_rad2)
    l = APoint(-half_chord2, chord_to_center) + center_top
    r = APoint(half_chord2, chord_to_center) + center_top

    right_angle2 = 2.5*math.pi - half_theta_rad2
    left_angle2 = math.pi/2 + half_theta_rad2
    
    if self.half_chord + 1 >= 9:
        # 使用AD函数绘制中心圆弧
        arc3=self.acad.model.AddArc(center_top, radius_down2, left_angle2, right_angle2)
        # 使用LD函数绘制优弧的连接直线并添加标注
        line1, dim1 = LD(self.acad, l, r, APoint(l.x, l.y + 1), line_layer="虚线")
        # 设置line1和arc3的线型比例为0.2
        if arc3 is not None:
            arc3.LinetypeScale = 0.2
            arc3.Layer = "虚线"
            arc3.Update()
        if line1 is not None:
            line1.LinetypeScale = 0.2
            line1.Layer = "虚线"
            line1.Update()
    else:
        
        # 俯视图的优弧使用AddArc函数绘制，不使用半径标注，使用直径标注
        arc3 = self.acad.AddArc(center_top, radius_down2, left_angle2, right_angle2)
        arc3.Layer = "轮廓线"
        arc3.Update()
        
        # 使用LD函数绘制直线并添加标注，使用默认图层，LD函数默认为轮廓线
        line1, dim1 = LD(self.acad, l, r, APoint(l.x, l.y + 7), line_layer="轮廓线")
    #这里创建的是底座中优弧底座的最小径向标注
    dim2 = self.acad.model.AddDimRotated(
        l, 
        APoint((l.x + r.x) / 2, center_top.y - 9),
        APoint(l.x - self.half_chord - 5, l.y), 
        math.pi/2
    )
    
    # 给标注文本增加括号
    dim2.TextOverride = "(<>)"
    dim2.layer = "标注线"     
    # 主圆，使用CD函数绘制主圆并添加标注
    main_circle, dim_main_circle = CD(self.acad, center_top, self.half_chord, angle=math.pi/3, leader_length=12, layer="轮廓线")
    main_circle.Layer = "轮廓线"
    if radius < 0:
        extra_circle, dim_extra_circle = CD(self.acad, center_top, self.half_chordN, angle=math.pi/8, leader_length=12, layer="轮廓线")
        extra_circle.Layer = "轮廓线"
 
