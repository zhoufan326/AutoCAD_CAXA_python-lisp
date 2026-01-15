# geometry.py
import math
from pyautocad import APoint

def calculate_geometry(radius, chord_length, a=3, b=6, c=25):
    """计算所有几何参数 
    a为模子的厚度,b为底座上半部分的高度,c为底座下半部分的高度。"""
    # 边界情况检查
    if abs(radius) <= 0:
        raise ValueError("半径不能为0")
    if chord_length > 2 * abs(radius):
        raise ValueError("弦长不能大于直径")
        
    half_chord = chord_length / 2
    half_theta_rad = math.asin(half_chord / abs(radius))
    half_theta_deg = math.degrees(half_theta_rad)


    #------重要参数--------#
     

    
    
    #此处计算弦距离圆心的垂直高度。    
    chord_height = radius * math.cos(half_theta_rad)#注意一下，这里弦高本身就可以是复制

    if radius > 0:
        # 球面模的圆心位置  #A4纸210*297
        center = APoint(0, 0)
        #弦的纵坐标
        chord_y = center.y + chord_height
        #此处计算剩余横线的纵坐标 
        #y_U为上横线的纵坐标，y_M为中横线的纵坐标，y_L为下横线的纵坐标。

        # 根据半径正负设置不同的中横线位置和角度
    
        y_U = chord_y - a
        y_M = y_U - b
        
        #凸面圆弧端点角度

        
        right_angle = 90 - half_theta_deg
        left_angle = 90 + half_theta_deg
    
    else: 

        center = APoint(0, 0)+APoint(0, -2*chord_height)
        chord_y = center.y + chord_height#弦的纵坐标，此处chord_height为负值
        
        y_U = center.y - math.sqrt(radius**2 - 5**2)-a
            #凹面圆弧底座上半部分的上横线纵坐标
        y_M = y_U - b
            #凹面圆弧底座上半部分的中横线纵坐标

            #凹面圆弧端点角度
        left_angle = 270 - half_theta_deg
        right_angle = 270 + half_theta_deg  


        #下方圆弧的端点角度
        
    y_M2=y_M-5
    y_L = y_M - c
    #底座下半部分的下横线纵坐标
    
    left_point = APoint(center.x - half_chord, chord_y)
    right_point = APoint(center.x + half_chord, chord_y)
    
    center2 = APoint(center.x, y_U - b - c)
    
    return {
        "radius": radius,
        "abs_radius": abs(radius),
        "half_chord": half_chord,
        "chord_length": chord_length,
        "chord_y": chord_y,
        "y_U": y_U, "y_M": y_M,"y_M2":y_M2, "y_L": y_L,
        "right_angle": right_angle,
        "left_angle": left_angle,
        "center": center,
        "center2": center2,
        "left_point": left_point,
        "right_point": right_point
    ,
        # 返回传入的几何参数以便绘图代码可以直接使用
        "a": a,
        "b": b,
        "c": c
    }

def generate_filename(radius, chord_length, drawing_type):
    """生成文件名（返回安全的单个文件名，不包含路径分隔符）。"""
    # 使用下划线替代可能的路径分隔符，保证在 join 时不会创建额外目录
    safe_type = str(drawing_type).replace('/', '_').replace('\\', '_')
    if radius < 0:
        return f"{safe_type}_-R{abs(radius):.3f}-Φ {chord_length:.3f}"
    else:
        return f"{safe_type}_R{radius:.3f}-Φ {chord_length:.3f}"
