#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注样式工具函数
根据镜片外径D值返回相应的标注参数
"""

def get_dimension_params(D):
    """
    根据镜片外径D值获取相应的标注参数
    
    参数:
        D: 镜片外径
        
    返回:
        tuple: (text_height, hatch_scale, dim_style_name)
    """
    # 直接使用公式计算text_height和hatch_scale，不使用选择语句
    text_height = D / 10.0        # S1、S2标签文字高度 = D/10
    hatch_scale = D / 50.0         # 剖面线比例 = D/50
    
    # 保持标注样式名称的选择逻辑
    if D < 10:
        dim_style_name = "0.7-5：1"  # 标注样式名称
    elif 10 <= D < 12.5:
        dim_style_name = "0.875-4：1"
    elif 12.5 <= D < 25:
        dim_style_name = "1.75-2：1"
    elif 25 <= D < 50:
        dim_style_name = "3.5-1：1"
    elif 50 <= D < 75:
        dim_style_name = "5.5-1：1.5"
    elif 75 <= D < 100:
        dim_style_name = "7-1：2"
    elif 100 <= D < 200:
        dim_style_name = "14-1：4"
    elif 200 <= D < 250:
        dim_style_name = "16.5-1：5"
    elif 250 <= D < 500:
        dim_style_name = "35-1：10"
    else:
        dim_style_name = "35-1：10"
    
    return text_height, hatch_scale, dim_style_name