import math
from utils.com_interface import APoint, aDouble
from utils import set_layer

def draw_pom(self, parameter):
    """绘制POM夹具壳"""
    base3 = parameter["base"]
    diameter = parameter["diameter"]
    POM_thickness = parameter["POM_thickness"]
    POM_height = parameter["POM_height"]
    A = base3 + APoint(0, POM_height)
    B = A + APoint(-POM_thickness, 0)
    C = B + APoint(0, -POM_height+1)
    D = C + APoint(1, -1)
    set_layer("轮廓线")
    pnts = [A, B, C, D, base3, A]
    pnts = [j for i in pnts for j in i]
    pnts = aDouble(pnts)
    self.acad.model.AddPolyLine(pnts)
    
    base4=base3+APoint(diameter, 0)
    A1 = base4 + APoint(0, POM_height)
    B1 = A1 + APoint(POM_thickness, 0)
    C1 = B1 + APoint(0, -POM_height+1)
    D1 = C1 + APoint(-1, -1)
    set_layer("轮廓线")
    pnts2 = [A1, B1, C1, D1, base4, A1]
    pnts2 = [j for i in pnts2 for j in i]
    pnts2 = aDouble(pnts2)
    self.acad.model.AddPolyLine(pnts2)
    self.acad.model.AddLine(A, A1)
    self.acad.model.AddLine(base4, base3)


    Mid = APoint((A.x + A1.x) / 2, (A.y + A1.y) / 2 + 1)
    MId2 = APoint((base3.x + base4.x) / 2, (base3.y + base4.y) / 2 - 1)
    centerline=self.acad.model.AddLine(Mid, MId2)
    centerline.Layer="中心线"
    centerline.LinetypeScale=10
    
    
    
    set_layer("标注线")
    DimLineLocation_A = A + APoint(0, 9)
    dim_list = [None]*6
    dim_list[0] = self.acad.model.AddDimRotated(A, A1, DimLineLocation_A, 0)
    dim_list[0].TextOverride = "%%c<>"
    dim_list[0].ToleranceDisplay = 2
    dim_list[0].ToleranceUpperLimit = 0.05
    dim_list[0].ToleranceLowerLimit = 0
    dim_list[0].TolerancePrecision = 3
    dim_list[0].ToleranceHeightScale = 0.7
    DimLineLocation_D1 = D1 + APoint(0,-9)
    dim_list[1] = self.acad.model.AddDimRotated(D1, D, DimLineLocation_D1, 0)
    dim_list[1].TextOverride = "%%c<>"
    DimLineLocation_C = C + APoint(0, -9)
    dim_list[2] = self.acad.model.AddDimRotated(B, C, DimLineLocation_C, 0)
    DimLineLocation_D = D + APoint(0, -19)
    dim_list[3] = self.acad.model.AddDimRotated(B,  D, DimLineLocation_D, 0)
    DimLineLocation_B = B + APoint(0, 19)
    dim_list[4] = self.acad.model.AddDimRotated(B,  B1, DimLineLocation_B, 0)
    dim_list[4].TextOverride = "%%c<>"


    return centerline