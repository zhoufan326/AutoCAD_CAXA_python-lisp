# geometry.py
import math
from pyautocad import APoint

def calculate_geometry(radius, chord_length, a=3, b=6, c=25):
    """计算所有几何参数 
    a为模子的厚度,b为底座中间连接轴的高度,c为底座的高度。"""
    # 边界情况检查
    if chord_length > 2 * abs(radius):
        raise ValueError("弦长不能大于直径")
    #----------------------------重要参数----------------------------#
    chord_center=APoint(0,45) #定义模子圆弧上弦的位置   
    half_chord = chord_length / 2
    half_theta_rad = math.asin(half_chord / abs(radius))
    half_theta_deg = math.degrees(half_theta_rad)
    #此处计算弦距离圆心的垂直高度。 弦心距   
    chord_to_center = abs(radius) * math.cos(half_theta_rad)#注意一下，这里弦高本身就可以是复制
   
    if radius > 0:
        # 球面模的圆心位置  #A4纸210*297
        center = chord_center - APoint(0, chord_to_center)
        #弦的纵坐标 
        chord_y = chord_center.y
        #此处计算剩余横线的纵坐标 
        #y_U为上横线的纵坐标，y_M为中横线的纵坐标，y_L为下横线的纵坐标。

        # 根据半径正负设置不同的中横线位置和角度
    
        y_U = chord_y - a
        y_M = y_U - b
        
        #凸面圆弧端点角度（弧度）
        start_angle = math.pi/2 - half_theta_rad
        end_angle = math.pi/2 + half_theta_rad
        
        # 为radius > 0的情况设置默认值
        radius2 = None  
        half_chordN = None  
        theta_big = None  
        theta_small = None  
     
    
    else: 
    #半径小于0的情况
        # 只有当R≥11且Φ≥18时，凹模才加厚1.5mm，否则保持原值
        if abs(radius) >= 11 and chord_length >= 18:
            a=a+1.5#凹模稍微加厚一点
        # 否则保持a的原值不变


        center = chord_center + APoint(0, chord_to_center)
        chord_y = chord_center.y

        #计算下方圆弧的弦心距，半弦长，圆心与上方圆弧相同。
        #大圆心角对应的弦心距
        chord_to_center2=chord_to_center+a
        half_chordN=half_chord+1
        #计算下方圆弧的半径
        theta_big=math.atan(half_chordN/chord_to_center2)
        #半径2根据弦心距和半弦长计算
        radius2=half_chordN/math.sin(theta_big)

        theta_small=math.asin(5/radius2)
        #小圆心角对应的弦心距
        chord_to_center3=radius2*math.cos(theta_small)                                               

    
        y_U =center.y - chord_to_center3
        y_M = y_U - b
            #凹面圆弧端点角度（弧度）
        start_angle = 3*math.pi/2 - half_theta_rad
        end_angle = 3*math.pi/2 + half_theta_rad  
        #下方圆弧的端点角度
        
    y_M2=y_M-5
    y_L = y_M - c
    #底座下半部分的下横线纵坐标
    
    left_point = APoint(center.x - half_chord, chord_y)
    right_point = APoint(center.x + half_chord, chord_y)
    #R<0时左右两端点有变化
    left_pointN = left_point - APoint(1,0)
    right_pointN = right_point + APoint(1,0)
    
    center2 = APoint(center.x, y_U - b - c)
    
    return {
        "radius": radius,
        "radius2": radius2,
        "theta_big": theta_big,
        "theta_small": theta_small,
        "theta": half_theta_rad,  # 半圆心角（弧度）
        "abs_radius": abs(radius),
        "half_chord": half_chord,
        "half_chordN": half_chordN,
        "chord_length": chord_length,
        "chord_center": chord_center,
        "chord_to_center": chord_to_center,
        "chord_y": chord_y,
        "y_U": y_U, "y_M": y_M,"y_M2":y_M2, "y_L": y_L,
        "start_angle": start_angle,
        "end_angle": end_angle,
        "center": center,
        "center2": center2,
        "left_point": left_point,
        "right_point": right_point,
        "left_pointN": left_pointN,
        "right_pointN": right_pointN,
    
        # 返回传入的几何参数以便绘图代码可以直接使用
        "a": a,
        "b": b,
        "c": c
    }


