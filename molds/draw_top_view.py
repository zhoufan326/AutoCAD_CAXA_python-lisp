# draw_top_view.py - 绘制俯视图模块
import math
from pyautocad import APoint, aDouble


def draw_top_view(self):
    """绘制俯视图
    1. 绘制中心小圆
    2. 绘制中心圆弧(优弧，并标注弦长)
    3. 标注直径
    由于俯视图不常用，所以直接将绘图与标注集成在一起。
    
    Args:
        self: DrawingOperations类的实例
    """
    radius = self.radius
    # 中心点（用于俯视图），使用 geometry 中计算的 center2
    center_down = APoint(0, -40) + self.center2
    self.set_layer("虚线")
    # 中心小圆
    circle = self.acad.model.AddCircle(center_down, 4)
    circle.LinetypeScale = 0.2
    circle.Update()
    # 中心圆弧,优弧
    radius_down2 = 9
    chord_length2 = 6
    half_chord2 = chord_length2 / 2
    half_theta_rad2 = math.asin(half_chord2 / radius_down2)
    chord_to_center = radius_down2 * math.cos(half_theta_rad2)
    l = APoint(-half_chord2, chord_to_center) + center_down
    r = APoint(half_chord2, chord_to_center) + center_down

    right_angle2 = 2.5*math.pi - half_theta_rad2
    left_angle2 = math.pi/2 + half_theta_rad2
    
    if self.half_chord + 1 >= 9:
        self.set_layer("虚线")
        arc3 = self.acad.model.AddArc(center_down, radius_down2, left_angle2, right_angle2)
        line1 = self.acad.model.AddLine(l, r)
        # 设置line1的线型比例为0.2
        arc3.LinetypeScale = 0.2
        line1.LinetypeScale = 0.2
        arc3.Update()
        line1.Update()
    else:
        self.set_layer("轮廓线")
        arc3 = self.acad.model.AddArc(center_down, radius_down2, left_angle2, right_angle2)
        line1 = self.acad.model.AddLine(l, r)
       
    self.set_layer("标注线")
    # 给 line1 添加线性标注
    dim1 = self.acad.model.AddDimAligned(l, r, APoint(l.x, l.y + 7))
    dim2 = self.acad.model.AddDimRotated(
        l, 
        APoint((l.x + r.x) / 2, center_down.y - 9),
        APoint(l.x - self.half_chord - 5, l.y), 
        math.radians(90)
    )
    
    # 给标注文本增加括号
    dim2.TextOverride = "(<>)"
        
    # 主圆（外圆）
    self.set_layer("轮廓线")
    self.acad.model.AddCircle(center_down, self.half_chord)
    
    if radius < 0:
        # 负半径特有：绘制额外的外圆
        # 外圆半径 = half_chord + 1，与主圆共享同一中心点
        self.set_layer("轮廓线")
        self.acad.model.AddCircle(center_down, self.half_chord + 1)
        self.set_layer("标注线")
        dia(self, center_down, self.half_chord + 1, math.radians(70))
    
    self.set_layer("标注线")
    dia(self, center_down, self.half_chord, math.radians(45)) 
    dia(self, center_down, 4, 0) 
    
    if self.chord_length >= 32:
        dia(self, center_down, 9, math.radians(135), 1)
    else:
        dia(self, center_down, 9, math.radians(135), 12)
    
    return arc3, line1, dim1, dim2


def dia(self, center, radius, angle, leader_length=10):
    """标注直径
    
    Args:
        self: DrawingOperations类的实例
        center: 圆心
        radius: 半径
        angle: 角度
        leader_length: 引导线长度
    """
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)

    chord_point = center + APoint(x, y)
    far_chord_point = center - APoint(x, y)
    
    return self.acad.model.AddDimDiametric(chord_point, far_chord_point, leader_length)
