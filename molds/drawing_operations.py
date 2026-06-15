# drawing_operations.py
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.com_interface import APoint, Autocad
from geometry import calculate_geometry
from draw_main_view import draw_main_view
from draw_top_view import draw_top_view
from utils import safe_acad_retry
from draw_bottom import draw_bottom

class DrawingOperations:
    def __init__(self, radius: float, chord_length: float, a_value: float = 3, b_value: float = 6, c_value: float = 25, drawing_type=None, draw_bottom_part=True):
        """初始化DrawingOperations类
        
        Args:
            geometry: 几何参数字典
            drawing_type: 绘图类型
            draw_bottom_part: 是否绘制底座部分（默认：True，仅GUI模式使用）
        """
        # 计算几何参数，这里直接将几何参数计算作为绘图类的属性
        if drawing_type in ("XJMJM", "XPMJM"):
            location=APoint(0,40)
        else:
            location=APoint(0,10)
        geometry = calculate_geometry(location, radius, chord_length, a_value, b_value, c_value)
        self._initialize_acad()
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
        self.y_connect = geometry["y_connect"]
        self.y_Up = geometry["y_Up"]
        self.abs_radius = geometry["abs_radius"]
        self.start_angle = geometry["start_angle"]
        self.end_angle = geometry["end_angle"]
        self.radius2 = geometry["radius2"]
        self.theta_small = geometry["theta_small"]
        self.theta_big = geometry["theta_big"]
        self.theta = geometry["theta"]  # theta直接使用半圆心角（弧度）
        self.half_chord = geometry["half_chord"]
        self.half_chordN = geometry["half_chordN"]
        self.y_Low = geometry["y_Low"]
        self.y_Up2 = geometry["y_Up2"]
        self.a = geometry["a"]
        self.b = geometry.get("b", 6)
        self.c = geometry.get("c", 25)
        self.chord_y2 = self.chord_y - self.a 
        self.chord_center=geometry["chord_center"]
        #连接轴的宽度
        self.width_Connect=geometry["width_Connect"]
        #底座的上宽度和下宽度
        self.width_Up=geometry["width_Up"]
        self.width_Low=geometry["width_Low"]
                
    @safe_acad_retry(max_retries=5, delay=1.0, name="初始化AutoCAD实例")
    def _initialize_acad(self):
        """初始化并验证AutoCAD实例"""
        self.acad = Autocad(create_if_not_exists=True)
        time.sleep(0.5)  # 增加初始化延迟
        

    def draw_views(self):
        """绘制所有视图"""
        if self.drawing_type in ("XJMJM", "XPMJM"):
            draw_main_view(self)
            
            #判断是否绘制底座,如果不绘制底座，也不绘制俯视图
            if self.draw_bottom_part:
                draw_bottom(self)
                draw_top_view(self) 


        else:

            draw_main_view(self) 
            if self.draw_bottom_part:
               draw_bottom(self)
        print("缩放到范围...")
        self.acad.doc.SendCommand("_.zoom _e ")
        time.sleep(0.5) 







   
   
           
           
