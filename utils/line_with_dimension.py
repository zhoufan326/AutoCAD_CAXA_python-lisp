#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制带标注的直线模块

本模块提供了一个函数，用于在 AutoCAD 中绘制两点间的直线并创建对齐标注，同时支持设置公差。
"""

from pyautocad import APoint
from .retry_decorator import safe_acad_retry


@safe_acad_retry(max_retries=5, delay=1.0, name="绘制带标注的直线")
def LD(acad, point1, point2, locate, upper_tolerance=0.0, lower_tolerance=0.0, line_layer="轮廓线",dim_type="Aligned",dim_angle=0):
    """绘制两点间的直线并创建对齐标注
    
    参数:
        acad: AutoCAD 实例
        point1: 直线起点坐标 (APoint 对象)
        point2: 直线终点坐标 (APoint 对象)
        locate: 标注线位置坐标 (APoint 对象)
        upper_tolerance: 上公差，默认 0.0
        lower_tolerance: 下公差，默认 0.0
        line_layer: 直线图层名称，默认 "轮廓线"，可设置为 "虚线"
        dim_type: 标注类型，默认 "Aligned"，可设置为 "Rotated"
        dim_angle: 标注角度，默认 0，仅在 dim_type 为 "Rotated" 时有效
        
    返回:
        tuple: (直线对象, 标注对象)
    """
    try:
        # 检查acad对象是否有效
        if acad is None:
            print("绘制带标注的直线时发生错误: acad对象为None")
            return None, None
            
        # 检查acad.model是否可用
        if not hasattr(acad, 'model'):
            print("绘制带标注的直线时发生错误: acad.model不可用")
            return None, None
            
        # 不通过ActiveLayer，直接绘制直线并设置图层
        line = acad.model.AddLine(point1, point2)
        line.Layer = line_layer  # 直接设置对象的图层
        line.Update()
        
        # 创建标注并设置图层
        if dim_type == "Aligned":
            dim = acad.model.AddDimAligned(point1, point2, locate)
        elif dim_type == "Rotated":
            dim = acad.model.AddDimRotated(point1, point2, locate, dim_angle)
            
            
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
        
        return line, dim
        
    except Exception as e:
        print(f"绘制带标注的直线时发生错误: {e}")
        return None, None


if __name__ == "__main__":
    # 示例用法（仅在有 AutoCAD 的环境下有意义）
    try:
        from pyautocad import Autocad
        
        # 连接到 AutoCAD
        acad = Autocad(create_if_not_exists=True)
        
        # 定义点坐标
        point1 = APoint(0, 0)
        point2 = APoint(100, 50)
        
        # 示例1: 使用极限公差（上下公差不相等）
        locate1 = APoint(50, 30)
        line1, dim1 = LD(acad, point1, point2, locate1, 0.02, -0.01)
        
        # 示例2: 使用对称公差（上下公差相等）
        point3 = APoint(0, 100)
        point4 = APoint(100, 150)
        locate2 = APoint(50, 130)
        line2, dim2 = LD(acad, point3, point4, locate2, 0.03, 0.03)
        
        if line1 and dim1 and line2 and dim2:
            print("直线和标注创建成功")
            print("示例1（极限公差）:")
            print(f"  直线长度: {line1.Length:.2f}")
            print(f"  标注值: {dim1.TextOverride or dim1.Measurement:.2f}")
            print(f"  公差类型: {'极限公差'} (上公差: 0.02, 下公差: -0.01)")
            print("示例2（对称公差）:")
            print(f"  直线长度: {line2.Length:.2f}")
            print(f"  标注值: {dim2.TextOverride or dim2.Measurement:.2f}")
            print(f"  公差类型: {'对称公差'} (公差: ±0.03)")
            
    except Exception as e:
        print(f"示例运行错误: {e}")
