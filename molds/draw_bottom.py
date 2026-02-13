# draw_bottom.py - 绘制底座模块
from pyautocad import APoint, aDouble


def draw_bottom(self):
    """绘制底座部分
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
    # 中心小圆弧，r固定为4
    self.acad.model.AddArc(self.center2, 4, math.radians(90), math.radians(180))
    if self.drawing_type in ("XJMJM", "XPMJM"):
        B = APoint(self.center.x - 9, self.y_M)
        C = APoint(self.center.x - 9, self.y_L)
    
        points = [
            APoint(self.center.x - 5, self.y_U), 
            APoint(self.center.x - 5, self.y_M), 
            B,
            C,
            APoint(self.center.x + 9, self.y_L),
            APoint(self.center.x + 9, self.y_M),
            APoint(self.center.x + 5, self.y_M),
            APoint(self.center.x + 5, self.y_U),  
        ]
        poly_points = [j for i in points for j in i]
        poly_points = aDouble(poly_points)
        self.acad.model.AddPolyLine(poly_points)

        # 虚线
        self.set_layer("虚线")
        self.acad.model.AddLine(APoint(3, self.y_M), APoint(3, self.y_L))
    # ---------当模子不是精磨和抛光模时---------
    else:
        self.acad.model.AddLine(APoint(0, self.y_M2), APoint(7, self.y_M2))

        B = APoint(self.center.x - 7, self.y_M)
        B2 = APoint(self.center.x - 7, self.y_M2)
        C = APoint(self.center.x - 5, self.y_L)
        points = [
            APoint(self.center.x - 5, self.y_U), 
            APoint(self.center.x - 5, self.y_M), 
            B, B2, C,
            APoint(self.center.x + 5, self.y_L),
            APoint(self.center.x + 7, self.y_M - 5),
            APoint(self.center.x + 7, self.y_M),
            # 这三点是B,B2,C的对称点
            APoint(self.center.x + 5, self.y_M),
            APoint(self.center.x + 5, self.y_U),  
        ]
        poly_points = [j for i in points for j in i]
        poly_points = aDouble(poly_points)
        self.acad.model.AddPolyLine(poly_points)
    
    
