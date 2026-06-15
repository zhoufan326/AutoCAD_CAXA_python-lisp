#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制带标注的圆模块

本模块提供了一个函数，用于在 AutoCAD 中绘制圆并创建标注，同时支持设置公差。
"""

import math
from utils.com_interface import APoint


def CD(acad, center, radius, angle, leader_length, upper_tolerance=0.0, lower_tolerance=0.0, layer="轮廓线"):
    """绘制圆并创建标注
    
    参数:
        acad: AutoCAD 实例
        center: 圆中心点坐标 (APoint 对象)
        radius: 圆半径
        angle: 角度（弧度），用于确定直径的方向
        leader_length: 引线长度，为点ChordPoint到标准文字定位夹点的距离
        upper_tolerance: 上公差，默认 0.0
        lower_tolerance: 下公差，默认 0.0
        layer: 圆图层名称，默认 "轮廓线"，可设置为 "虚线"
    
    返回:
        tuple: (圆对象, 标注对象)
    """
    try:
        # AutoCAD的AddCircle函数要求半径为正数，取绝对值
        abs_radius = abs(radius)
        
        # 绘制圆并设置图层
        circle = acad.model.AddCircle(center, abs_radius)
        circle.Layer = layer  # 直接设置对象的图层
        circle.Update()
        
        # 创建直径标注并设置图层
        # 计算直径的两个端点
        ChordPoint = APoint(
            center.x + abs_radius * math.cos(angle),
            center.y + abs_radius * math.sin(angle)
        )
        FarChordPoint = APoint(
            center.x + abs_radius * math.cos(angle + math.pi),
            center.y + abs_radius * math.sin(angle + math.pi)
        )
        
        # 使用AddDimDiametric创建直径标注
        dim = acad.model.AddDimDiametric(ChordPoint, FarChordPoint, leader_length)
        dim.Layer = "标注线"  # 直接设置对象的图层     
        # 设置公差（如果有）
        if upper_tolerance != 0.0 or lower_tolerance != 0.0:
            # 如果上公差与下公差相等且都不为0，则使用对称公差
            if upper_tolerance == lower_tolerance and upper_tolerance != 0.0:
                dim.ToleranceDisplay = 2  # 显示对称公差
                dim.ToleranceUpperLimit = upper_tolerance
                dim.ToleranceLowerLimit = lower_tolerance
            else:
                # 否则使用极限公差
                dim.ToleranceDisplay = 1  # 显示极限公差
                dim.ToleranceUpperLimit = upper_tolerance
                dim.ToleranceLowerLimit = lower_tolerance
            
            dim.TolerancePrecision = 3  # 公差精度
            dim.ToleranceHeightScale = 0.7  # 公差文本高度比例
            dim.Update()
        
        return circle, dim
        
    except Exception as e:
        print(f"绘制带标注的圆时发生错误: {e}")
        return None, None


if __name__ == "__main__":
    # 示例用法（仅在有 AutoCAD 的环境下有意义）
    try:
        from utils.com_interface import Autocad
        
        # 连接到 AutoCAD
        acad = Autocad(create_if_not_exists=True)
        
        # 定义参数
        center = APoint(0, 0)
        radius = 30
        angle1 = math.pi  # 垂直向下方向
        
        # 示例1: 使用极限公差（上下公差不相等）
        leader_length1 = 40  # 引线长度
        circle1, dim1 = CD(acad, center, radius, angle1, leader_length1, 0.02, -0.01)
        
        # 示例2: 使用对称公差（上下公差相等）
        center2 = APoint(100, 0)
        angle2 = math.pi  # 垂直向下方向
        leader_length2 = 40  # 引线长度
        circle2, dim2 = CD(acad, center2, radius, angle2, leader_length2, 0.03, 0.03)
        
        if circle1 and dim1 and circle2 and dim2:
            print("圆和标注创建成功")
            print("示例1（极限公差）:")
            print(f"  圆半径: {radius}")
            print(f"  标注值: {dim1.TextOverride or dim1.Measurement:.2f}")
            print(f"  公差类型: {'极限公差'} (上公差: 0.02, 下公差: -0.01)")
            print("示例2（对称公差）:")
            print(f"  圆半径: {radius}")
            print(f"  标注值: {dim2.TextOverride or dim2.Measurement:.2f}")
            print(f"  公差类型: {'对称公差'} (公差: ±0.03)")
            
    except Exception as e:
        print(f"示例运行错误: {e}")
