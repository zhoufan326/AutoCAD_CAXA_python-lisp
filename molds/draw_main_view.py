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

def draw_main_view(self):
    """绘制主视图
    """

    if (self.drawing_type in ("XJMJM", "GPMXJ")) and (abs(self.radius) < 11 or self.chord_length < 18):
    # 这种情况下绘制的其实是丸片底座
        self.y_connect = self.chord_y - self.a  
        small_caliber_base(self)
    elif  self.radius > 0:
        positive_radius(self)
        KC(self)
    else:
        negative_radius(self)
        KC(self)
    # 绘制中心线
    CL(self.acad, self.chord_center+APoint(0, 15), APoint(self.center.x, self.y_Low - 15))
 

    self.acad.doc.SendCommand("_.zoom _e ")
    time.sleep(1.0)  # 增加等待时间

def KC(self):
    """绘制开槽标注"""
    if self.drawing_type in ("JZM_KC", "GPMJX"):
        # 添加开槽标注
        
        arrow_pnt = APoint(0, self.radius) + self.center
        baseline_pnt = arrow_pnt + APoint(25, 15)
        pnts_array = np.array([arrow_pnt, baseline_pnt]).flatten()
        pnts_array = aDouble(pnts_array)
        leader = self.acad.model.AddMLeader(pnts_array, 0)
        leader.DoglegLength = 8
        leader.LandingGap = 3
        leader.TextString = "开槽"
        leader.Layer = "标注线"

def positive_radius(self):
    """绘制正半径主视图
    """
    self.acad.model.AddLine(APoint(self.center.x, self.chord_y), self.right_point)

    #y_connect指连接轴的上半部分，y_Up指底座的上纵坐标，y_Low指底座的下纵坐标
    locate=self.left_point+APoint(-7, 0)
    LD(self.acad, self.left_point, APoint(self.left_point.x, self.y_connect), locate)

    self.acad.model.AddLine(APoint(self.left_point.x, self.y_connect), APoint(self.center.x - 5, self.y_connect))
    self.acad.model.AddLine(self.right_point, APoint(self.right_point.x, self.y_connect))
    self.acad.model.AddLine(APoint(self.right_point.x, self.y_connect), APoint(self.center.x , self.y_connect))

    # 使用AD函数绘制圆弧并添加标注
    arc, dim_arc = AD(self.acad, self.center, self.radius, self.start_angle, self.end_angle, leader_length=20, locate_angle=self.start_angle+1.5*self.theta)
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


    locate_angle=self.start_angle+self.theta/6
    arc, dim_arc = AD(self.acad, self.center, self.radius, self.start_angle, math.pi*1.5, locate_angle=locate_angle)
    if dim_arc is not None:
        dim_arc.TextOverride = "凹<>"

    self.acad.model.AddArc(self.center, self.radius2, math.pi*1.5 + self.theta_small, math.pi*1.5 + self.theta_big)
    self.acad.model.AddArc(self.center, self.radius2, math.pi*1.5 - self.theta_big, math.pi*1.5 - self.theta_small)
    
    
    locate=self.left_pointN+APoint(-7, 0)
    LD(self.acad, self.left_pointN, APoint(self.left_pointN.x, self.chord_y2), locate)
    self.acad.model.AddLine(self.right_pointN, APoint(self.right_pointN.x, self.chord_y2))
    self.acad.model.AddLine(APoint(self.center.x, self.chord_y2), APoint(self.center.x + self.half_chordN, self.chord_y2))

    
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
    left_point.y = self.y_connect
    right_point.y = self.y_connect

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
