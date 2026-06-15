#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在 AutoCAD 图纸上添加日期和名称标注模块"""

from datetime import datetime
from utils.com_interface import APoint
from utils import set_layer
from utils.retry_decorator import safe_acad_retry


@safe_acad_retry(max_retries=5, delay=1.0, name="添加日期和名称标注")
def date_name(acad, name="XJMJM/R10-Φ10", date=None):
    """在图纸上添加两个日期文本和一个名称文本
    
    Args:
        acad: Autocad 实例
        name: 图纸名称
        date: 日期字符串，默认使用当天
    """
    set_layer("轮廓线")
    acad.app.ActiveDocument.ActiveTextStyle = acad.app.ActiveDocument.TextStyles.Item("宋体")

    # 使用当前日期（如果未提供）
    if date is None:
        date = datetime.now().strftime("%Y/%m/%d")
    
    # 文本位置
    point1 = APoint(70, 81)     # 上日期
    point2 = APoint(-10, -102)  # 下日期
    point3 = APoint(71, -75)   # 名称
        
    # 创建文本
    text1 = acad.AddText(date, point1, 2.5)
    text2 = acad.AddText(date, point2, 2.5)
    text3 = acad.AddText(name, point3, 2.5)
    
    return text1, text2, text3


if __name__ == "__main__":
    """示例用法"""
    try:
        from utils.com_interface import Autocad
        print("已连接到 AutoCAD")
        acad = Autocad(create_if_not_exists=True)
        
        # 示例：添加日期和名称
        result = date_name(acad)
        print("日期和名称文本创建成功" if all(result) else "创建失败")
            
    except Exception as e:
        print(f"示例运行错误: {e}")
