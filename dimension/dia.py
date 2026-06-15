import math
from utils.com_interface import APoint

def dia(acad_instance, center, radius, angle, leader_length, offset=0):
    """创建直径标注
    
    参数:
        acad_instance: AutoCAD 实例
        center: 中心点
        radius: 半径
        angle: 角度（弧度）
        leader_length: 引线长度，为点ChordPoint到标准文字定位夹点的距离
        offset: 偏移量（可选）
    
    返回:
        标注对象
    """
    
    # 计算直径的两个端点
    p1 = APoint(
        center.x + radius * math.cos(angle),
        center.y + radius * math.sin(angle)
    )
    p2 = APoint(
        center.x + radius * math.cos(angle + math.pi),
        center.y + radius * math.sin(angle + math.pi)
    )
    
    # 计算标注线的位置
    dim_location = APoint(
        center.x + (radius + offset) * math.cos(angle + math.pi/2),
        center.y + (radius + offset) * math.sin(angle + math.pi/2)
    )
    
    # 创建直径标注
    dim = acad_instance.model.AddDimDiametric(p1, p2, leader_length)
    dim.Layer = "标注线"  # 直接设置对象的图层
    
    
    return dim