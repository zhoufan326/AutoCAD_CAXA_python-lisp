#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""绘制中心线模块

本模块提供了一个函数，用于在 AutoCAD 中绘制中心线，支持设置线型和线型比例。
"""

from pyautocad import APoint
from .layer import set_layer


def CL(self, point1, point2):
    """绘制中心线
    
    参数:
        self: DrawingOperations 实例（包含 acad 对象）
        point1: 中心线起点坐标 (APoint 对象)
        point2: 中心线终点坐标 (APoint 对象)
    
    返回:
        line: 创建的直线对象
    """
    try:
        # 设置中心线图层
        set_layer("中心线")
        
        # 绘制中心线
        center_line = self.acad.model.AddLine(point1, point2)
        center_line.Color = 1
        center_line.Linetype = "CENTER"
        center_line.LinetypeScale = 0.1  # 使虚线更密集
        
        return center_line
        
    except Exception as e:
        print(f"绘制中心线失败: {e}")
        return None


if __name__ == "__main__":
    # 测试代码需要手动设置acad实例
    print("CL函数测试: 请在实际环境中使用DrawingOperations实例调用此函数")