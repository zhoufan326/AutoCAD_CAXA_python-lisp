#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在 AutoCAD 图纸上添加日期和名称标注模块"""

from datetime import datetime
from pyautocad import APoint, Autocad
from utils import set_layer
from utils.retry_decorator import safe_acad_retry

# 全局 AutoCAD 实例
acad = Autocad(create_if_not_exists=True)

@safe_acad_retry(max_retries=5, delay=1.0, name="添加日期和名称标注")
def date_name(name="XJMJM/R10-Φ10", date=None):
    """在图纸上添加两个日期文本和一个名称文本"""
    set_layer("轮廓线")
    acad.ActiveDocument.ActiveTextStyle = acad.ActiveDocument.TextStyles.Item("宋体")

    # 使用当前日期（如果未提供）
    if date is None:
        date = datetime.now().strftime("%Y/%m/%d")
    
    # 文本位置
    point1 = APoint(70, 81)     # 上日期
    point2 = APoint(-10, -102)  # 下日期
    point3 = APoint(71, -75)   # 名称
        
    # 创建文本
    text1 = acad.model.AddText(date, point1, 2.5)
    text2 = acad.model.AddText(date, point2, 2.5)
    text3 = acad.model.AddText(name, point3, 2.5)
    
    return text1, text2, text3


if __name__ == "__main__":
    """示例用法"""
    try:
        print("已连接到 AutoCAD")
        
        # 示例：添加日期和名称
        result = date_name()
        print("日期和名称文本创建成功" if all(result) else "创建失败")
            
    except Exception as e:
        print(f"示例运行错误: {e}")
