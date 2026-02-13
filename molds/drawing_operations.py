# drawing_operations.py
import math
import time
from pyautocad import APoint, aDouble

# 导入模块化的绘制函数
from .draw_main_view import draw_main_view
from .draw_bottom import draw_bottom
from .draw_top_view import draw_top_view

class DrawingOperations:
    def __init__(self, acad, set_layer_func, geometry=None, drawing_type=None, draw_bottom_part=True):
        """初始化DrawingOperations类
        
        Args:
            acad: AutoCAD对象
            set_layer_func: 设置图层的函数
            geometry: 几何参数字典（可选）
            drawing_type: 绘图类型（可选）
            draw_bottom_part: 是否绘制底座部分（默认：True，仅GUI模式使用）
        """
        self.acad = acad
        self.set_layer = set_layer_func
        self.drawing_type = drawing_type
        self.draw_bottom_part = draw_bottom_part
        

        self.radius = geometry["radius"]
        self.chord_length = geometry["chord_length"]
        self.center2 = geometry["center2"]
        self.left_pointN = geometry["left_pointN"]
        self.right_pointN = geometry["right_pointN"]
        self.left_point = geometry["left_point"]
        self.right_point = geometry["right_point"]
        self.center = geometry["center"]
        self.chord_y = geometry["chord_y"]
        self.y_U = geometry["y_U"]
        self.y_M = geometry["y_M"]
        self.abs_radius = geometry["abs_radius"]
        self.right_angle = geometry["right_angle"]
        self.left_angle = geometry["left_angle"]
        self.radius2 = geometry["radius2"]
        self.theta_small = geometry["theta_small"]
        self.theta_big = geometry["theta_big"]
        self.half_chord = geometry["half_chord"]
        self.half_chordN = geometry["half_chordN"]
        self.y_L = geometry["y_L"]
        self.y_M2 = geometry["y_M2"]
        self.a = geometry["a"]
        self.b = geometry.get("b", 6)
        self.c = geometry.get("c", 25)
    def draw_views(self):
        """绘制所有视图"""
        #------绘制主视图------#
        draw_main_view(self)
        
        #------绘制底座------#
        if self.draw_bottom_part:
            draw_bottom(self)
        
        #------绘制中心线------#
        self.draw_center_line()
        
        #------绘制俯视图------#
        if self.drawing_type in ("XJMJM", "XPMJM"):
            draw_top_view(self)  # 只有这两类绘制俯视图
        
        #------缩放到范围------#
        print("缩放到范围...")
        self.acad.doc.SendCommand("_.zoom _e ")
        time.sleep(1.0)  # 增加等待时间

    def draw_center_line(self):
        """绘制中心线"""
        self.set_layer("中心线")
        center_line_start = APoint(self.center.x, self.y_L + 60)
        center_line_end = APoint(self.center.x, self.y_U - 50)
        center_line = self.acad.model.AddLine(center_line_start, center_line_end)
        center_line.Color = 1
        
        try:
            center_line.Linetype = "CENTER2"
            # 虚线通常需要较小的比例
            center_line.LinetypeScale = 0.1  # 使虚线更密集
        except:
            try:
                center_line.Linetype = "CENTER"
                center_line.LinetypeScale = 0.1
            except:
                pass
