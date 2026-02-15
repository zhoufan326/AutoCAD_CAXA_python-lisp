#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制带标注的圆模块

本模块提供了一个函数，用于在 AutoCAD 中绘制圆并创建标注，同时支持设置公差。
"""

import math
from pyautocad import APoint


def CD(acad, center, radius, locate, upper_tolerance=0.0, lower_tolerance=0.0, layer="轮廓线"):
    """绘制圆并创建标注
    
    参数:
        acad: AutoCAD 实例
        center: 圆中心点坐标 (APoint 对象)
        radius: 圆半径
        locate: 标注线位置坐标 (APoint 对象)
        upper_tolerance: 上公差，默认 0.0
        lower_tolerance: 下公差，默认 0.0
        layer: 圆图层名称，默认 "轮廓线"，可设置为 "虚线"
    
    返回:
        tuple: (圆对象, 标注对象)
    """
    try:
        # 绘制圆并设置图层
        circle = acad.model.AddCircle(center, radius)
        circle.Layer = layer  # 直接设置对象的图层
        circle.Update()
        
        # 创建直径标注并设置图层
        # 计算直径的两个端点（使用与dimension.py中dia函数相同的方式）
        angle = 0  # 水平方向
        p1 = APoint(
            center.x + radius * math.cos(angle),
            center.y + radius * math.sin(angle)
        )
        p2 = APoint(
            center.x + radius * math.cos(angle + math.pi),
            center.y + radius * math.sin(angle + math.pi)
        )
        
        # 计算标注线的位置（参考dimension.py中dia函数的方式）
        # 如果用户未指定locate，则使用默认计算方式
        if locate is None:
            dim_location = APoint(
                center.x + (radius + 10) * math.cos(angle + math.pi/2),
                center.y + (radius + 10) * math.sin(angle + math.pi/2)
            )
        else:
            dim_location = locate
        
        # 使用AddDimRotated替代AddDimAligned（与dimension.py保持一致）
        dim = acad.model.AddDimRotated(p1, p2, dim_location, 0)
        dim.Layer = "标注线"  # 直接设置对象的图层
        dim.TextOverride = "%%c<>'"  # 设置为直径标注
        
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
        from pyautocad import Autocad
        
        # 连接到 AutoCAD
        acad = Autocad(create_if_not_exists=True)
        
        # 定义参数
        center = APoint(0, 0)
        radius = 30
        locate = APoint(0, -40)
        
        # 示例1: 使用极限公差（上下公差不相等）
        circle1, dim1 = CD(acad, center, radius, locate, 0.02, -0.01)
        
        # 示例2: 使用对称公差（上下公差相等）
        center2 = APoint(100, 0)
        circle2, dim2 = CD(acad, center2, radius, APoint(100, -40), 0.03, 0.03)
        
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
