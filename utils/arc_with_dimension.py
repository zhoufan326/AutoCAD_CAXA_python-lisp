#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制带标注的圆弧模块

本模块提供了一个函数，用于在 AutoCAD 中绘制圆弧并创建标注，同时支持设置公差。
"""

import math
from pyautocad import APoint


def AD(acad, center, radius, start_angle, end_angle, locate, upper_tolerance=0.0, lower_tolerance=0.0, layer="轮廓线"):
    """绘制圆弧并创建标注
    
    参数:
        acad: AutoCAD 实例
        center: 圆弧中心点坐标 (APoint 对象)
        radius: 圆弧半径
        start_angle: 圆弧起始角度（弧度）
        end_angle: 圆弧结束角度（弧度）
        locate: 标注线位置坐标 (APoint 对象)
        upper_tolerance: 上公差，默认 0.0
        lower_tolerance: 下公差，默认 0.0
        layer: 圆弧图层名称，默认 "轮廓线"，可设置为 "虚线"
    
    返回:
        tuple: (圆弧对象, 标注对象)
    """
    try:
        # 绘制圆弧并设置图层
        arc = acad.model.AddArc(center, radius, start_angle, end_angle)
        arc.Layer = layer  # 直接设置对象的图层
        arc.Update()
        
        # 创建半径标注并设置图层
        dim = acad.model.AddDimRadial(center, APoint(
            center.x + radius * math.cos((start_angle + end_angle) / 2),
            center.y + radius * math.sin((start_angle + end_angle) / 2)
        ), locate)
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
        
        return arc, dim
        
    except Exception as e:
        print(f"绘制带标注的圆弧时发生错误: {e}")
        return None, None


if __name__ == "__main__":
    # 示例用法（仅在有 AutoCAD 的环境下有意义）
    try:
        from pyautocad import Autocad
        
        # 连接到 AutoCAD
        acad = Autocad(create_if_not_exists=True)
        
        # 定义参数
        center = APoint(0, 0)
        radius = 50
        start_angle = math.radians(30)
        end_angle = math.radians(270)
        locate = APoint(0, -70)
        
        # 示例1: 使用极限公差（上下公差不相等）
        arc1, dim1 = AD(acad, center, radius, start_angle, end_angle, locate, 0.02, -0.01)
        
        # 示例2: 使用对称公差（上下公差相等）
        center2 = APoint(100, 0)
        arc2, dim2 = AD(acad, center2, radius, start_angle, end_angle, APoint(100, -70), 0.03, 0.03)
        
        if arc1 and dim1 and arc2 and dim2:
            print("圆弧和标注创建成功")
            print("示例1（极限公差）:")
            print(f"  圆弧半径: {radius}")
            print(f"  标注值: {dim1.TextOverride or dim1.Measurement:.2f}")
            print(f"  公差类型: {'极限公差'} (上公差: 0.02, 下公差: -0.01)")
            print("示例2（对称公差）:")
            print(f"  圆弧半径: {radius}")
            print(f"  标注值: {dim2.TextOverride or dim2.Measurement:.2f}")
            print(f"  公差类型: {'对称公差'} (公差: ±0.03)")
            
    except Exception as e:
        print(f"示例运行错误: {e}")
