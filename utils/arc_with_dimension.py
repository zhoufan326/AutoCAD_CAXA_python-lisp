#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制带标注的圆弧模块

本模块提供了一个函数，用于在 AutoCAD 中绘制圆弧并创建标注，同时支持设置公差和标注样式。
"""

import math
from pydoc import locate
from pyautocad import APoint
from .retry_decorator import safe_acad_retry


def _get_dimension_style(dim_style):
    """获取正确的标注样式名称"""
    return dim_style if dim_style.endswith('$4') else dim_style + '$4'


def _setup_tolerance(dim, upper_tolerance, lower_tolerance):
    """设置标注公差"""
    if upper_tolerance != 0.0 or lower_tolerance != 0.0:
        is_symmetric = upper_tolerance == lower_tolerance and upper_tolerance != 0.0
        dim.ToleranceDisplay = 2 if is_symmetric else 1
        dim.ToleranceUpperLimit = upper_tolerance
        dim.ToleranceLowerLimit = lower_tolerance
        dim.TolerancePrecision = 3
        dim.ToleranceHeightScale = 0.7


@safe_acad_retry(max_retries=5, delay=1.0, name="绘制带标注的圆弧")
def AD(acad, center, radius, start_angle, end_angle, leader_length=20, 
       upper_tolerance=0.0, lower_tolerance=0.0, layer="轮廓线", dim_style="ZqStandard", locate_angle=None):
    """绘制圆弧并创建标注
    
    参数:
        acad: AutoCAD 实例
        center: 圆弧中心点坐标 (APoint 对象),radius: 圆弧半径
        start_angle: 圆弧起始角度（弧度）,end_angle: 圆弧结束角度（弧度）
        leader_length: 标注线长度，默认 20
        upper_tolerance: 上公差，默认 0.0,lower_tolerance: 下公差，默认 0.0
        layer: 圆弧图层名称，默认 "轮廓线"
        dim_style: 标注样式名称，默认 "ZqStandard"，会自动添加$4作为半径子样式
        locate_angle: 标注点角度（弧度），默认使用圆弧中点
    
    返回:
        tuple: (圆弧对象, 标注对象)
    """
    try:
        
        abs_radius = abs(radius)
        
        # 绘制圆弧
        arc = acad.model.AddArc(center, abs_radius, start_angle, end_angle)
        arc.Layer = layer
        arc.Update()
        
        # 计算弦点角度（使用指定角度或圆弧中点）
        if locate_angle is None:
            locate_angle = (start_angle + end_angle) / 2
    
        # 计算弦点坐标
        locate_point = APoint(
            center.x + abs_radius * math.cos(locate_angle),
            center.y + abs_radius * math.sin(locate_angle)
        )
        
     
        dim = acad.model.AddDimRadial(center, locate_point, leader_length)
        dim.Layer = "标注线"
        dim.StyleName = _get_dimension_style(dim_style)
        
        # 设置公差
        _setup_tolerance(dim, upper_tolerance, lower_tolerance)
        
        dim.Update()
        return arc, dim
        
    except Exception as e:
        print(f"绘制带标注的圆弧时发生错误: {e}")
        return None, None


def demo():
    """演示函数 - 展示模块功能"""
    try:
        from pyautocad import Autocad
        
        acad = Autocad(create_if_not_exists=True)
        
        # 示例1: 使用默认样式和极限公差（默认弦点角度）
        center1 = APoint(0, 0)
        radius = 50
        start_angle = math.radians(30)
        end_angle = math.radians(270)
        
        arc1, dim1 = AD(acad, center1, radius, start_angle, end_angle, 70, 0.02, -0.01)
        
        # 示例2: 使用自定义样式和对称公差（默认弦点角度）
        center2 = APoint(100, 0)
        arc2, dim2 = AD(acad, center2, radius, start_angle, end_angle, 70, 0.03, 0.03, dim_style="MY_STYLE")
        
        # 示例3: 使用不同标注线长度（默认弦点角度）
        center3 = APoint(200, 0)
        arc3, dim3 = AD(acad, center3, radius, start_angle, end_angle, 80, 0.01, 0.01)
        
        # 示例4: 使用指定弦点角度（90度）
        center4 = APoint(300, 0)
        locate_angle = math.radians(90)  # 指定弦点角度为90度
        arc4, dim4 = AD(acad, center4, radius, start_angle, end_angle, 70, 0.02, 0.02, locate_angle=locate_angle)
        
        # 示例5: 使用短标注线长度
        center5 = APoint(400, 0)
        arc5, dim5 = AD(acad, center5, radius, start_angle, end_angle, 40, 0.01, -0.01)
        
        if all([arc1, dim1, arc2, dim2, arc3, dim3, arc4, dim4, arc5, dim5]):
            print("所有圆弧和标注创建成功")
            print(f"示例1 - 样式: {dim1.StyleName}, 长度: {dim1.TextOverride}, 公差: +{dim1.ToleranceUpperLimit}/-{dim1.ToleranceLowerLimit}")
            print(f"示例2 - 样式: {dim2.StyleName}, 长度: {dim2.TextOverride}, 对称公差: ±{dim2.ToleranceUpperLimit}")
            print(f"示例3 - 样式: {dim3.StyleName}, 长度: {dim3.TextOverride}, 对称公差: ±{dim3.ToleranceUpperLimit}")
            print(f"示例4 - 样式: {dim4.StyleName}, 长度: {dim4.TextOverride}, 对称公差: ±{dim4.ToleranceUpperLimit}, 弦点角度: {math.degrees(locate_angle):.0f}°")
            print(f"示例5 - 样式: {dim5.StyleName}, 长度: {dim5.TextOverride}, 公差: +{dim5.ToleranceUpperLimit}/-{dim5.ToleranceLowerLimit}")
            return True
        else:
            print("部分圆弧或标注创建失败")
            return False
            
    except Exception as e:
        print(f"演示运行错误: {e}")
        return False


if __name__ == "__main__":
    demo()
