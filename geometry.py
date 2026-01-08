# geometry.py
import math
from pyautocad import APoint

def calculate_geometry(radius, chord_length, a=3, b=6, c=25):
    """计算所有几何参数 
    a为模子的厚度,b为底座上半部分的高度,c为底座下半部分的高度。"""
    half_chord = chord_length / 2
    half_theta_rad = math.asin(half_chord / abs(radius))
    half_theta_deg = math.degrees(half_theta_rad)
       
    center = APoint(0, 0)
    #圆弧中心点的坐标
    arc_center_point = APoint(0, radius)+center
    #此处计算弦的位置。    
    chord_height = radius * math.cos(half_theta_rad)
    #弦的纵坐标
    chord_y = center.y + chord_height
    #此处计算剩余横线的纵坐标 
    #（圆弧上的弦不考虑）y_U为上横线的纵坐标，y_M为中横线的纵坐标，y_L为下横线的纵坐标。

    y_U = chord_y - a
    if radius<=0:
        y_M =arc_center_point.y-a
        left_angle = 270 - half_theta_deg
        right_angle = 270 + half_theta_deg

    else:
        y_M = y_U - b
    y_L = y_M - c
    
    right_angle = 90 - half_theta_deg
    left_angle = 90 + half_theta_deg
    
    left_point = APoint(center.x - half_chord, chord_y)
    right_point = APoint(center.x + half_chord, chord_y)
    
    center2 = APoint(0, y_U - b - c)
    
    return {
        "radius": radius,
        "abs_radius": abs(radius),
        "a": a,
        "b": b,
        "c": c,
        "half_chord": half_chord,
        "chord_length": chord_length,
        "chord_y": chord_y,
        "y_U": y_U, "y_M": y_M, "y_L": y_L,
        "right_angle": right_angle,
        "left_angle": left_angle,
        "center": center,
        "center2": center2,
        "left_point": left_point,
        "right_point": right_point
    }

def generate_filename(radius, chord_length):
    """生成文件名"""
    if radius < 0:
        return f"-R{abs(radius):.3f}-Φ{chord_length:.3f}"
    else:
        return f"R{radius:.3f}-Φ{chord_length:.3f}"