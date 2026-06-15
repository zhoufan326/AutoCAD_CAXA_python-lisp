import math
from utils.com_interface import APoint, aDouble, vt_point
from utils import set_layer


def pom_main(acad, parameter):
    """绘制POM夹具主入口"""
    center_h = _draw_pom(acad, parameter)
    if parameter["radius2"] < 0:
        _draw_port(acad, parameter, center_h)


def _draw_pom(acad, parameter):
    """绘制POM夹具主体"""
    B = parameter["base"]
    height = parameter["height"]
    radius = parameter["radius"]
    diameter = parameter["diameter"]
    radius2 = parameter["radius2"]
    thickness = parameter["POM_thickness"]
    A = B + APoint(0, height)

    theta = math.asin(diameter / (2 * abs(radius)))

    center_h = abs(radius) * math.cos(theta)
    if radius > 0:
        center = APoint(A.x + diameter / 2, A.y + center_h)
        start_angle = 1.5 * math.pi - theta
        end_angle = 1.5 * math.pi + theta
    else:
        center = APoint(A.x + diameter / 2, A.y - center_h)
        start_angle = 0.5 * math.pi - theta
        end_angle = 0.5 * math.pi + theta
    arc_center = APoint(0, -radius) + center
    set_layer("轮廓线")
    acad.AddArc(center, abs(radius), start_angle, end_angle)

    C = B + APoint(-0.5, 0)
    D = C + APoint(-1, 1)

    if radius > 0:
        E = A + APoint(-1.5, 6)
        F = A + APoint(diameter / 8 - 1, 6)
        G = A + APoint(diameter / 4 - 1, 6 + diameter / 8)
    else:
        E = A + APoint(-1.5, abs(radius) - center_h + 6)
        F = A + APoint(diameter / 8 - 1, abs(radius) - center_h + 6)
        G = A + APoint(diameter / 4 - 1, abs(radius) - center_h + 6 + diameter / 8)
    if radius2 > 0:
        E = E + APoint(0, -5 + thickness)
        F = F + APoint(0, -5 + thickness)
        G = G + APoint(0, -5 + thickness)

    A1 = A + APoint(diameter, 0)
    B1 = B + APoint(diameter, 0)
    C1 = C + APoint(diameter + 1, 0)
    D1 = D + APoint(diameter + 3, 0)
    E1 = E + APoint(diameter + 3, 0)
    F1 = F + APoint(0.75 * diameter + 2, 0)
    G1 = G + APoint(diameter / 2 + 2, 0)
    if radius2 < 0:
        set_layer("轮廓线")
        pnts = [A, B, C, D, E]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        acad.AddPolyLine(pnts)
        pnts1 = [A1, B1, C1, D1, E1]
        pnts1 = [j for i in pnts1 for j in i]
        pnts1 = aDouble(pnts1)
        acad.AddPolyLine(pnts1)
        acad.AddLine(E, E1)
    else:
        set_layer("轮廓线")
        pnts = [A, B, C, D, E, F, G, G1, F1, E1, D1, C1, B1, A1]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        acad.AddPolyLine(pnts)
        set_layer("标注线")
        DimLineLocation_G = G + APoint(0, 9)
        dim_G_G1 = acad.AddDimRotated(G, G1, DimLineLocation_G, 0)
        dim_G_G1.TextOverride = "%%c<>"

        DimLineLocation_F = G + APoint(0, 18)
        dim_F_F1 = acad.AddDimRotated(F, F1, DimLineLocation_F, 0)
        dim_F_F1.TextOverride = "%%c<>"
        DimLineLocation_F2 = F1 + APoint(0.75 * diameter, 0)
        dim_G1_F1 = acad.AddDimRotated(G1, F1, DimLineLocation_F2, math.radians(90))
        dim_G1_F1.TextPosition = vt_point(DimLineLocation_F2 + APoint(9, 0))

#----------------------绘制中心线-------------#
        set_layer("中心线")
    
        line = acad.AddLine(APoint(A.x+diameter/2, A.y-5), APoint(A.x+diameter/2, A.y+10))
        line.LinetypeScale = 0.1
        
        set_layer("标注线")
        acad.app.ActiveDocument.ActiveDimStyle = acad.app.ActiveDocument.DimStyles.Item("ZqStandard")
        
        dim_list = [None]*10
         #添加左侧参考高度
        DimLineLocation_C2= C + APoint(-4, 0)
        
        dim_list[0] = acad.AddDimRotated(arc_center, E, DimLineLocation_C2, math.radians(90))
        dim_list[0].TextOverride = "(<>)"
       #添加左侧总高标注
        DimLineLocation_C1= C + APoint(-15, 0)
        dim_list[1] = acad.AddDimRotated(C, E, DimLineLocation_C1, math.radians(90))
        DimLineLocation_C = C + APoint(-10, 0)
        #添加左侧厚度标注
        dim_list[2] = acad.AddDimRotated(D, E, DimLineLocation_C, math.radians(90))
        #添加总口径标注
        DimLineLocation_E = E + APoint(0, 25)
        dim_list[3] = acad.AddDimRotated(E, E1, DimLineLocation_E, 0)
        dim_list[3].TextOverride = "%%c<>"
        DimLineLocation_B = B + APoint(0, -30)
        dim_list[4] = acad.AddDimRotated(B, B1, DimLineLocation_B, 0)
        dim_list[4].TextOverride = "%%c<>"
        dim_list[4].ToleranceDisplay = 2
        dim_list[4].ToleranceUpperLimit = 0.15
        dim_list[4].ToleranceLowerLimit = -0.1
        dim_list[4].TolerancePrecision = 3
        dim_list[4].ToleranceHeightScale = 0.7
        DimLineLocation_down = B + APoint(0, -10)
        dim_list[7] = acad.AddDimRotated(B, C, DimLineLocation_down, 0)
       
        #添加右侧夹持厚度标注height
        DimLineLocation_B1 = B1 + APoint(9,0)
        dim_list[5] = acad.AddDimRotated(B1, A1, DimLineLocation_B1, math.radians(90))
        dim_list[5].TextPosition = vt_point(DimLineLocation_B1 + APoint(0, -6))
       
       
        #添加半径标注
        ChordPoint = center + APoint(0,-radius)#ChordPoint - 弦点/圆弧上的点（标注的终点
        dim_list[6] = acad.AddDimRadial(center, ChordPoint, 10)
        try:
            
            dim_list[6].StyleName = "ZqStandard"# 设置标注样式
            # 添加前缀：凹（半径<0）或凸（半径>0）
            if radius < 0:
                dim_list[6].TextOverride = "凹<>"
            else:
                dim_list[6].TextOverride = "凸<>"
            dim_list[6].TextPosition = vt_point(APoint(-7, -7) + ChordPoint)
            dim_list[6].DimForceLine = 0
            dim_list[6].Update()
        except Exception:     
                pass
    
    return center_h


def _draw_port(acad, parameter, center_h):
    """绘制夹具端口"""
    base = parameter["base"]
    height = parameter["height"]
    A = base + APoint(0, height)
    diameter = parameter["diameter"]
    radius = parameter["radius"]
    if radius < 0:
        I = A + APoint(diameter / 2 - 2.5, abs(radius) - center_h + 1)
    else:
        I = A + APoint(diameter / 2 - 2.5, 1)

    H = I + APoint(0, 2)
    G = H + APoint(-1.7, 0)
    F = G + APoint(0, 3)
    F1 = F + APoint(8.4, 0)
    G1 = F1 + APoint(0, -3)
    H1 = G1 + APoint(-1.7, 0)
    I1 = H1 + APoint(0, -2)
    set_layer("轮廓线")
    pnts = [F, G, H, I, I1, H1, G1, F1, F]
    pnts = [j for i in pnts for j in i]
    pnts = aDouble(pnts)
    acad.AddPolyLine(pnts)
    acad.AddLine(H, H1)
    set_layer("标注线")
    DimLineLocation_H = H + APoint(0, 9)
    dim_list = [None] * 6
    dim_list[0] = acad.AddDimRotated(H, H1, DimLineLocation_H, 0)
    dim_list[0].TextOverride = "Φ<>"
    dim_list[0].ToleranceDisplay = 2
    dim_list[0].ToleranceUpperLimit = 0.05
    dim_list[0].ToleranceLowerLimit = -0.03
    dim_list[0].TolerancePrecision = 3
    dim_list[0].ToleranceHeightScale = 0.7
    DimLineLocation_F = F + APoint(0, 16)
    dim_list[1] = acad.AddDimRotated(F, F1, DimLineLocation_F, 0)
    dim_list[1].TextOverride = "Φ<>"
    DimLineLocation_F1 = APoint(F1.x + 8 + diameter / 2, F1.y)
    dim_list[2] = acad.AddDimRotated(I1, F1, DimLineLocation_F1, math.radians(90))
    DimLineLocation_F11 = APoint(F1.x + 2 + diameter / 2, F1.y)
    dim_list[3] = acad.AddDimRotated(G1, F1, DimLineLocation_F11, math.radians(90))
