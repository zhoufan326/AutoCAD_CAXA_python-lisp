import math
from utils.com_interface import APoint
#根据圆弧的弦长和角度计算圆弧的起始角和终止角
def calculate_arc_parameter(center,chord_length, radius, direction):
    """计算圆弧的起始角和终止角,
    在autocad绘图的时候按逆时针计算,
    起始角和终止角的计算结果是弧度制,
    这里是按照劣弧计算，优弧需要将起始角和终止角交换一下
    因为角度的计算方式是从x轴正向逆时针计算"""
    half_chord = chord_length / 2
    radius_abs=abs(radius)
    half_theta_rad = math.asin(half_chord / radius_abs)
    if direction == "horizontal":
        if radius > 0:
            start_angle = math.pi/2 - half_theta_rad
            end_angle = math.pi/2 + half_theta_rad
        else:
            start_angle = 1.5*math.pi + half_theta_rad
            end_angle = 1.5*math.pi - half_theta_rad
    elif direction == "vertical":
        if radius > 0:
            start_angle =  - half_theta_rad
            end_angle =  + half_theta_rad
        else:
            start_angle = math.pi - half_theta_rad
            end_angle = math.pi + half_theta_rad
    else:
        raise ValueError("Invalid direction. Use 'horizontal' or 'vertical'.")
    start_point=APoint(center.x+radius_abs*math.cos(start_angle),center.y+radius_abs*math.sin(start_angle))
    end_point=APoint(center.x+radius_abs*math.cos(end_angle),center.y+radius_abs*math.sin(end_angle))
    return start_angle, end_angle,start_point,end_point
