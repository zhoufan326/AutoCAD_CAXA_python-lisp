# draw_main_view.py - 绘制主视图模块
import math
import time
from pyautocad import APoint, aDouble


def draw_main_view(self):
    """绘制主视图
    
    Args:
        self: DrawingOperations类的实例
    """
    if (self.drawing_type in ("XJMJM", "GPMXJ")) and (abs(self.radius) < 11 or self.chord_length < 18):
    # 这种情况下绘制的其实是丸片底座
        self.y_U = self.chord_y - self.a  # 凹面圆弧底座连接轴的上横线纵坐标
        self.y_M = self.y_U - self.b  # 凹面圆弧底座连接轴的下横线纵坐标
        _draw_small_caliber_base(self)
    else:    
            if self.radius > 0:
                _draw_main_view_positive_radius(self)
            elif self.radius < 0:
                _draw_main_view_negative_radius(self)


    
    print("缩放到范围...")
    self.acad.doc.SendCommand("_.zoom _e ")
    time.sleep(1.0)  # 增加等待时间


def _draw_main_view_positive_radius(self):
    """绘制正半径主视图（凸圆弧）
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
    draw_polylines_P(self)

    # 画直线，对于凸圆弧，只画对称轴右侧的线
    self.acad.model.AddLine(APoint(self.center.x, self.chord_y), self.right_point)
    self.acad.model.AddLine(APoint(self.center.x, self.y_U), APoint(self.center.x + 5, self.y_U))
    self.acad.model.AddLine(APoint(self.center.x, self.y_M), APoint(self.center.x + 5, self.y_M))
   
    # 创建圆弧
    arc = self.acad.model.AddArc(
        self.center, 
        self.abs_radius, 
        math.radians(self.right_angle), 
        math.radians(self.left_angle)
    )  # 逆时针绘制圆弧，因此先右后左
    
    return arc


def _draw_main_view_negative_radius(self):
    """绘制负半径主视图（凹圆弧）
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
   
    # 画弦和直线，统一剖面线到左侧，所以这里绘制右侧直线
    self.acad.model.AddLine(self.left_point, self.right_point)
    self.acad.model.AddLine(APoint(self.center.x, self.y_U), APoint(self.center.x + 5, self.y_U))
    self.acad.model.AddLine(APoint(self.center.x, self.y_M), APoint(self.center.x + 5, self.y_M))
    self.acad.model.AddLine(APoint(self.center.x, self.chord_y - self.a), APoint(self.center.x + self.half_chordN, self.chord_y - self.a))
    
    # 创建圆弧,只有左侧有剖面线，因此只需要绘制左侧的圆弧
    arc = self.acad.model.AddArc(
        self.center, 
        self.abs_radius, 
        math.radians(self.left_angle), 
        math.radians(270)
    )
    
    # 创建下方圆弧
    arc_down = self.acad.model.AddArc(
        self.center, self.radius2, math.pi*1.5 + self.theta_small, math.pi*1.5 + self.theta_big
    )  # 右半边的圆弧
    
    arc_down2 = self.acad.model.AddArc(
        self.center, self.radius2, math.pi*1.5 - self.theta_big, math.pi*1.5 - self.theta_small
    )  # 左半边的圆弧
    
    point_l = self.left_pointN
    point_r = self.right_pointN

    # 绘制两条连接圆弧的竖线
    self.acad.doc.SendCommand(f'_LINE {arc_down2.StartPoint[0]},{arc_down2.StartPoint[1]} {point_l.x},{point_l.y} \n')
    self.acad.doc.SendCommand(f'_LINE {point_r.x},{point_r.y} {arc_down.EndPoint[0]},{arc_down.EndPoint[1]} \n')
    
    draw_polylines_N(self)
    
    return arc, arc_down, arc_down2


def draw_polylines_P(self):
    """绘制正半径多段线
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
    
    # 左侧多段线
    points = [
        APoint(self.left_point.x, self.left_point.y),
        APoint(self.left_point.x, self.y_U),
        APoint(self.center.x - 5, self.y_U), 
    ]
    poly_points = [j for i in points for j in i]
    poly_points = aDouble(poly_points)
    self.acad.model.AddPolyLine(poly_points)
    
    # 右侧多段线
    points = [
        APoint(self.right_point.x, self.right_point.y), 
        APoint(self.right_point.x, self.y_U),
        APoint(self.center.x + 5, self.y_U), 
    ]

    poly_points = [j for i in points for j in i]
    poly_points = aDouble(poly_points)
    self.acad.model.AddPolyLine(poly_points)


def draw_polylines_N(self):
    """绘制负半径多段线
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
    
    # 左侧多段线
    points = [
        APoint(self.left_point.x, self.left_point.y),
        APoint(self.left_point.x - 1, self.left_point.y), 
    ]
    poly_points = [j for i in points for j in i]
    poly_points = aDouble(poly_points)
    self.acad.model.AddPolyLine(poly_points)
    
    # 右侧多段线
    points = [
        APoint(self.right_point.x, self.right_point.y), 
        APoint(self.right_point.x + 1, self.right_point.y), 
    ]

    poly_points = [j for i in points for j in i]
    poly_points = aDouble(poly_points)
    self.acad.model.AddPolyLine(poly_points)


    

def _draw_small_caliber_base(self):
    """绘制小口径成型丸片的底座
    
    Args:
        self: DrawingOperations类的实例
    """
    self.set_layer("轮廓线")
    points = [None] * 10
    
    # 创建left_point和right_point对象
    left_point = APoint(0, 0)
    right_point = APoint(0, 0)
    
    if self.radius < 0:
        left_point.x = self.left_pointN.x
        right_point.x = self.right_pointN.x
    else:
        left_point.x = self.left_point.x
        right_point.x = self.right_point.x
    left_point.y = self.y_U
    right_point.y = self.y_U



    # 保持原始绘制点顺序，重新分配数组索引
    points[0] = APoint(-5, left_point.y)                 # 第1个点
    points[1] = APoint(left_point.x, left_point.y)       # 第2个点
    points[2] = APoint(left_point.x, left_point.y + 2)   # 第3个点
    points[3] = APoint(-0.75, left_point.y + 2)          # 第4个点
    points[4] = APoint(-0.75, left_point.y + 3)          # 第5个点
    points[5] = APoint(0.75, left_point.y + 3)           # 第6个点
    points[6] = APoint(0.75, left_point.y + 2)           # 第7个点
    points[7] = APoint(right_point.x, left_point.y + 2)   # 第8个点
    points[8] = APoint(right_point.x, left_point.y)       # 第9个点
    points[9] = APoint(0, left_point.y)                  # 第10个点
    
    poly_points = [j for i in points for j in i]
    poly_points = aDouble(poly_points)
    self.acad.model.AddPolyLine(poly_points)
    self.acad.model.AddLine(APoint(0,left_point.y + 2), points[6])
