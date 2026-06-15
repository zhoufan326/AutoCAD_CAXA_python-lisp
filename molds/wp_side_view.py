# 标准库导入
import math
import os
import sys

# 添加项目根目录和当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 第三方库导入
from utils.com_interface import APoint, aDouble

# 项目模块导入
from utils import LD, AD
from calculator.arc_angle import calculate_arc_parameter

def draw_side_view(acad, center, diameter, radius):
    """绘制侧视图
    
    Args:
        acad: AutoCAD对象
        diameter: 直径
        radius: 半径
        base: 基准点
        drawing_type: 绘图类型
        
    Returns:
        tuple: 绘制的图形对象 (arc, pline2, pline3)
    """
    chord = diameter
    r = abs(radius)
    #开槽处的矢高减少量
    d_sagitta = r - math.sqrt(r**2 - 0.5**2)

    up, down = [0] * 7, [0] * 7
    # 计算圆弧参数
    start_angle, end_angle, start_point, end_point = calculate_arc_parameter(center, chord, radius, "vertical")

    # 根据半径正负设置中心点和点坐标
    if radius >= 0:
        
        up[0], down[0] = end_point, start_point
        #丸片边厚为3
        up[1], down[1] = APoint(end_point.x-3, chord / 2), APoint(end_point.x-3, -chord / 2)
        up[5], down[5] = APoint(center.x+r-d_sagitta, 0.5), APoint(center.x+r-d_sagitta, -0.5)
        

    else:
       
        chordN = chord + 1 if chord < 10 else chord + 2
        up[0], down[0] = APoint(start_point.x, chordN/2), APoint(end_point.x, -chordN/2)
        #丸片中心厚度为3
        up[1], down[1] = APoint(center.x-r-3, chordN / 2), APoint(center.x-r-3, -chordN / 2)
        up[5], down[5] = APoint(start_point.x, 0.5), APoint(start_point.x, -0.5)
        up[6], down[6] = start_point, end_point
        acad.model.AddLine(up[0], up[6])
        acad.model.AddLine(down[0], down[6])

        # 内口径标注
        dim_point1 = APoint(up[6].x + 0.8*chord, 0)
        line6,dim_obj6 =LD(acad, up[6], down[6], dim_point1)
        dim_obj6.TextOverride = "%%c<>"
        dim_obj6.StyleName = "ZqStandard0.5$0"
    # 最外侧口径标注
    dim_point1 = APoint(up[1].x + 1.5 * chord,0)
    line1,dim_obj1 = LD(acad, up[1], down[1], dim_point1)
    dim_obj1.TextOverride = "%%c<>"
    dim_obj1.StyleName = "ZqStandard0.5"

    
    # 设置标注样式
    acad.ActiveDocument.ActiveDimStyle = acad.ActiveDocument.DimStyles.Item("ZqStandard0.5")
    
    # 绘制圆弧并标注
    theta=math.atan(chord/6/r)
    locate_angle =start_angle+theta
    arc, dim_rad = AD(acad, center, r, start_angle, end_angle, 10, layer="轮廓线", locate_angle=locate_angle)
    dim_rad.StyleName = "ZqStandard0.5$4"
    dim_rad.TextOverride = f"{'凹' if radius < 0 else ''}<> ".strip()
    if radius<0:
        dim_rad.TextPosition = up[0]+APoint(chord/2,-chord/4)
    # 设置点坐标
    base=APoint(up[1].x, 0)
    up[2], down[2] = base + APoint(0, 0.75), base + APoint(0, -0.75)
    up[3], down[3] = base + APoint(1, 0.75), base + APoint(1, -0.75)
    up[4], down[4] = base + APoint(3, 0.5), base + APoint(3, -0.5)
    
    # 小孔口径标注
    locate = APoint(up[2].x - chord/2, up[2].y)
    line2, dim_obj2 = LD(acad, up[2], down[2], locate, 0.02, 0.00)
    dim_obj2.TextOverride = "%%c<>"
    # 绘制线段并标注
    LD(acad, up[0], up[1], APoint(up[1].x, up[1].y + chord))
    
    LD(acad, up[2], up[3], APoint(up[0].x, up[0].y + chord/2))
    
    # 绘制剩余线段
    
    pline2 = acad.model.AddPolyline(aDouble([j for i in [up[3], down[3], down[2], down[1], down[0]] for j in i]))
    pline3 = acad.model.AddPolyline(aDouble([j for i in [up[5], up[4], down[4], down[5]] for j in i]))
    
    return arc, pline2, pline3