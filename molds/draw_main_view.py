# draw_main_view.py - 绘制主视图模块
import math
import time
import sys
import os
import numpy as np

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyautocad import APoint, aDouble
from utils import LD, AD, CL
from draw_bottom import bottom

def draw_main_view(self):
    """绘制主视图
    """

    if (self.drawing_type in ("XJMJM", "GPMXJ")) and (abs(self.radius) < 11 or self.chord_length < 18):
    # 这种情况下绘制的其实是丸片底座
        self.y_U = self.chord_y - self.a  
        small_caliber_base(self)
    elif  self.radius > 0:
        positive_radius(self)
        KC(self)
    else:
        negative_radius(self)
        KC(self)
    #判断是否绘制底座
    if self.draw_bottom_part:
        bottom(self)
    # 绘制中心线
    CL(self, self.chord_center+APoint(0, 15), APoint(self.center.x, self.y_L - 15))
 

    self.acad.doc.SendCommand("_.zoom _e ")
    time.sleep(1.0)  # 增加等待时间

def KC(self):
    """绘制开槽标注"""
    if self.drawing_type in ("JZM_KC", "GPMJX"):
        # 添加开槽标注
        try:
            arrow_pnt = APoint(0, self.radius) + self.center
            baseline_pnt = arrow_pnt + APoint(25, 15)
            pnts_array = np.array([arrow_pnt, baseline_pnt]).flatten()

            leader = self.acad.model.AddMLeader(pnts_array, 0)
            leader.DoglegLength = 8
            leader.LandingGap = 3
            leader.TextString = "开槽"
            leader.Layer = "标注线"
        except Exception as e:
            print(f"绘制开槽标注时发生错误: {e}")

def positive_radius(self):
    """绘制正半径主视图
    """
    self.acad.model.AddLine(APoint(self.center.x, self.chord_y), self.right_point)
    self.acad.model.AddLine(APoint(self.center.x, self.y_U), APoint(self.center.x + 5, self.y_U))
    self.acad.model.AddLine(APoint(self.center.x, self.y_M), APoint(self.center.x + 5, self.y_M))
   
    self.acad.model.AddLine(self.left_point, APoint(self.left_point.x, self.y_U))
    self.acad.model.AddLine(APoint(self.left_point.x, self.y_U), APoint(self.center.x - 5, self.y_U))
    self.acad.model.AddLine(self.right_point, APoint(self.right_point.x, self.y_U))
    self.acad.model.AddLine(APoint(self.right_point.x, self.y_U), APoint(self.center.x + 5, self.y_U))

    # 使用AD函数绘制圆弧并添加标注
    arc, dim_arc = AD(self.acad, self.center, self.radius, self.start_angle, self.end_angle, leader_length=20, chord_angle=self.start_angle+0.6*self.theta)
    if dim_arc is not None:
        dim_arc.TextOverride = "凸<>"
    return arc
def negative_radius(self):
    """绘制负半径主视图
    """
    locationPoint = self.chord_center + APoint(0, self.half_chordN)
    line1, dim1 = LD(self.acad, self.left_pointN, self.right_pointN, locationPoint)
    if dim1 is not None:
        dim1.TextOverride = "%%c<>"
    locationPoint2 = self.chord_center + APoint(0, 7)
    line2, dim2 = LD(self.acad, self.left_point, self.right_point, locationPoint2)
    if dim2 is not None:
        dim2.TextOverride = "%%c<>"
        dim2.StyleName = "ZqStandard$0"  # 设置为半标注

    line3 = self.acad.model.AddLine(APoint(self.center.x, self.y_U2), APoint(self.center.x + self.half_chordN, self.y_U2))
    line3.Layer = "轮廓线"
    
    arc, dim_arc = AD(self.acad, self.center, self.radius, self.start_angle, math.pi*1.5, chord_angle=self.start_angle+self.theta/3)
    if dim_arc is not None:
        dim_arc.TextOverride = "凹<>"
    
    line4 = self.acad.model.AddArc(self.center, self.radius2, math.pi*1.5 + self.theta_small, math.pi*1.5 + self.theta_big)
    line4.Layer = "轮廓线"
    line5 = self.acad.model.AddArc(self.center, self.radius2, math.pi*1.5 - self.theta_big, math.pi*1.5 - self.theta_small)
    line5.Layer = "轮廓线"

    arc1 = self.acad.model.AddLine(self.left_pointN, APoint(self.left_pointN.x, self.y_U2))
    arc1.Layer = "轮廓线"
    arc2 = self.acad.model.AddLine(self.right_pointN, APoint(self.right_pointN.x, self.y_U2))
    arc2.Layer = "轮廓线"
    
    return arc



    
        
    
    



  


def small_caliber_base(self):
    """绘制小口径成型丸片的底座
    """
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

    set_layer("轮廓线")
    self.acad.model.AddPolyLine(poly_points)
    self.acad.model.AddLine(APoint(0, left_point.y + 2), points[6])
    set_layer("标注线")
    dim45 = self.acad.model.AddDimAligned(
        points[4], points[5], APoint((points[4].x + points[5].x) / 2, points[4].y + 2), 
    )
    dim45.ToleranceDisplay, dim45.ToleranceUpperLimit, dim45.ToleranceLowerLimit = 2, 0, 0.02
    dim45.TolerancePrecision, dim45.ToleranceHeightScale = 3, 0.7
    dim45.Update()
