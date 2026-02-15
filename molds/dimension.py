#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""尺寸标注模块

本模块提供了在 AutoCAD 中创建模具尺寸标注的功能，包括：
- 日期和名称标注
- 各种尺寸标注（直径、半径、长度等）

主要函数：
- date_name: 创建日期和名称标注
- dimension: 创建尺寸标注对象
"""

import numpy as np
from pyautocad import APoint
import math

# 全局 AutoCAD 实例（由调用方提供）
# 用途：作为后备机制，当函数调用时未提供acad实例或实例失效时使用
# 默认值为None，使用时需确保已初始化
acad = None


def _safe_set_text_style(acad_instance, style_name):
    """安全设置文字样式
    
    参数:
        acad_instance: AutoCAD 实例
        style_name: 文字样式名称
    """
    try:
        if style_name in acad_instance.ActiveDocument.TextStyles:
            acad_instance.ActiveDocument.ActiveTextStyle = acad_instance.ActiveDocument.TextStyles.Item(style_name)
    except Exception:
        pass


def dia(acad_instance, center, radius, angle, offset=0):
    """创建直径标注
    
    参数:
        acad_instance: AutoCAD 实例
        center: 中心点
        radius: 半径
        angle: 角度（弧度）
        offset: 偏移量（可选）
    
    返回:
        标注对象
    """
    _safe_set_text_style(acad_instance, "ZqStandard")
    
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
    dim = acad_instance.model.AddDimRotated(p1, p2, dim_location, 0)
    dim.TextOverride = "%%c<>'"
    
    return dim


def date_name(drawing_type="XJMJM"):
    """创建日期和名称标注
    
    参数:
        drawing_type: 图纸类型
    
    返回:
        tuple: 日期标注对象和名称标注对象
    """
    # 显式声明使用全局acad变量作为后备机制
    global acad
    
    from datetime import datetime
    
    # 创建日期标注
    now = datetime.now()
    date_text = f"{now.year}-{now.month:02d}-{now.day:02d}"
    
    # 使用全局acad变量进行操作，作为参数传入失败时的后备机制
    _safe_set_text_style(acad, "ZqStandard")
    date_text_obj = acad.model.AddText(date_text, APoint(10, 5), 3.5)
    
    # 创建名称标注
    name_text = "黄天"
    name_text_obj = acad.model.AddText(name_text, APoint(25, 5), 3.5)
    
    return date_text_obj, name_text_obj


def dimension(geom=None, drawing_type="XJMJM"):
    """创建一组标注对象并返回它们的元组。

    参数:
        geom: 包含标注几何信息的字典
        drawing_type: 图纸类型，默认"XJMJM"

    返回顺序与原实现相同：
    (dimRotObj, dimRotObjA, dimRotObjB, dimRotObjC, dimRotObj_down, dimRadObj1, dimRadObj2, dimRotObjD)
    不可用的对象以 None 填充。
    """
    # 显式声明使用全局acad变量作为后备机制
    global acad
    
    # 使用全局acad变量进行操作，作为参数传入失败时的后备机制
    _safe_set_text_style(acad, "ZqStandard")
    created = [None] * 18  # 18个标注对象

    try:
        # 提取变量
        y_U, y_M, y_L = geom["y_U"], geom["y_M"], geom["y_L"]
        radius = geom["radius"]
        center = geom["center"]
        left_point, right_point = geom["left_point"], geom["right_point"]
        b, a = geom["b"], geom["a"]
        left_pointN, right_pointN = geom.get("left_pointN"), geom.get("right_pointN")
        center2 = geom.get("center2")
        chord_length = geom.get("chord_length", 0)
        
        # 检查是否为小口径底座（与draw_main_view.py中的条件一致）
        is_small_caliber_base = (drawing_type in ("XJMJM", "GPMXJ")) and (abs(radius) < 11 or chord_length < 18)
        
        # 旋转角默认设置为0度
#------------计算标注用到的点坐标-----------------#
        # A、B、C三个点分别代表小写字母a、b、c三条线段的下端点
        A = APoint(-5, y_U)
        Ar = APoint(5, y_U)
        if drawing_type in ("XJMJM", "XPMJM"):
            B = APoint(-9, y_M)
            C = APoint(-9, y_L)
            Cr = APoint(9, y_L)
        else:
            B = APoint(-7, y_M)
            C = APoint(-5, y_L)
        
        # D点表示底座中心最低点的位置
        D = APoint(center.x, y_L)
        arc_center_point = APoint(0, radius) + center  # 上圆弧的中心点  

        
        #------------计算标注线的定位点-----------------#
        # 上口径标注线位置
        if radius <= 0:
            DimLineLocation_up = left_point + APoint(0, 1.5)
            DimLineLocation_up2 = left_point + APoint(0, 6)
        else:
            DimLineLocation_up = center + APoint(0, radius + 1.5)
        
        # 圆弧中心到底座最低端参考高度的定位点（模子右侧）
        if right_point.x >= 9:
            DimLineLocation_D = right_point + APoint(6, 0)
        elif 0 < right_point.x < 9:
            DimLineLocation_D = APoint(15, 0)

        
        # --------上口径标注----------#
        # 上口径标注已在draw_main_view.py中使用LD函数创建
        #----------连接轴直径标注----------#
        if b != 0: 
            DimLineLocation_A = A + APoint(0, -4)
            created[10] = acad.model.AddDimAligned(Ar, A, DimLineLocation_A)
            created[10].TextOverride = "%%c<>'"
        # 纵向线段标注
        # 纵向线段标注已在draw_main_view.py中使用LD函数创建
        
        DimLineLocation_B = B + APoint(-1, 0)
        created[2] = acad.model.AddDimRotated(A, B, DimLineLocation_B, math.radians(90))
        
        if drawing_type in ("XJMJM", "XPMJM"):
            DimLineLocation_C = C + APoint(-3, 0)
            DimLineLocation_Cr = Cr + APoint(0, -14)
            created[3] = acad.model.AddDimRotated(C, B, DimLineLocation_C, math.radians(90))
             # 下口径标注（底座直径标注）
            created[4] = acad.model.AddDimAligned(Cr, C, DimLineLocation_Cr)
            created[4].TextOverride = "%%c<>'"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = -0.02
            created[4].ToleranceLowerLimit = 0.04
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
            created[4].Update()
        elif drawing_type in ("GPMXJ", "JZM", "JZM_KC", "GPMJX"):# 添加小尾锥标注
            DimLineLocation_C = C + APoint(-9, 0)
            DimLineLocation_C2 = C + APoint(-13, 0)
            created[3] = acad.model.AddDimAligned(B+APoint(0, -5), B, DimLineLocation_C)
            created[13] = acad.model.AddDimRotated(B+APoint(0, -5),  C, DimLineLocation_C2, math.radians(90))            
            # 添加锥度标注
            arrow_pnt = APoint(6, (y_L + y_M) / 2)
            baseline_pnt = APoint(10, (y_L + y_M) / 2 - 5)
            pnts_array = np.array([arrow_pnt, baseline_pnt]).flatten()
            
            leader = acad.model.AddMLeader(pnts_array, 0)
            leader.DoglegLength = 8
            leader.LandingGap = 3
            leader.TextString = "锥度1：10"
            created[14] = leader
            if drawing_type in ("JZM_KC", "GPMJX"):
                # 添加开槽标注
                arrow_pnt2 = APoint(0, radius) + center
                baseline_pnt2 = arrow_pnt2 + APoint(25, 15)
                pnts_array2 = np.array([arrow_pnt2, baseline_pnt2]).flatten()
                
                leader2 = acad.model.AddMLeader(pnts_array2, 0)
                leader2.DoglegLength = 8
                leader2.LandingGap = 3
                leader2.TextString = "开槽"
                created[15] = leader2
                
                # --------下口径标注------#（底座直径标注）
            created[4] = acad.model.AddDimAligned(B+APoint(0, -5), APoint(7, y_M-5), APoint(0, y_L-14))
              
            created[4].Update()
            created[4].TextOverride = "Φ<>'"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = 0.15
            created[4].ToleranceLowerLimit = -0.05
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
                            
        #-------对应右侧定位点D,圆弧中点到模子最低点的参考高度
        
            created[7] = acad.model.AddDimAligned(arc_center_point, D, DimLineLocation_D)
            created[7].TextOverride = "(<>)"
        #-------------凹模额外加一个总高标注------------#
        if radius <0:  
            created[8] = acad.model.AddDimAligned(right_point, D, DimLineLocation_D+APoint(5,0))
            created[8].TextOverride = "(<>)"
        
        # 圆弧半径标注 - 仅在非小口径底座情况下执行
        if not is_small_caliber_base:
            angle_rad = math.radians(80)
            chord_point = APoint(
                center.x + radius * math.cos(angle_rad),
                center.y + radius * math.sin(angle_rad)
            )
            
            created[5] = acad.model.AddDimRadial(center, chord_point, 20 if radius > 0 else 35)
            created[5].TextPosition = chord_point + APoint(17, 17) if radius > 0 else chord_point + APoint(27, 27)
            created[5].StyleName = "ZqStandard$4"
            created[5].Update()
        
        # 第二个圆弧半径标注
        angle_rad2 = math.radians(135)
        chord_point2 = APoint(
            center2.x + 4 * math.cos(angle_rad2),
            center2.y + 4 * math.sin(angle_rad2)
        )
        
        created[6] = acad.model.AddDimRadial(center2, chord_point2, 10)
        created[6].TextPosition = chord_point2 + APoint(7.5, -7.5)

    except Exception as error:
        # 总体异常不会中止流程，记录后返回已有对象
        print(f"dimension: 发生异常: {error}")

    return tuple(created)


if __name__ == "__main__":
    # 简单示例（仅在有 AutoCAD 的环境下有意义）
    try:
        date_name()
    except Exception:
        pass