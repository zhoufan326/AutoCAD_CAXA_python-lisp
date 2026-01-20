import math
from pyautocad import APoint, aDouble
from utils import set_layer

def draw_cu(self, parameter):
      """绘制标准夹具
      parameter（夹具参数）"""
      base = parameter["base"]
      diameter = parameter["diameter"]
      POM_thickness = parameter["POM_thickness"]
      
      
      
      A = base + APoint(0, 2.5)
      B = A + APoint(-POM_thickness, 0)
      C = B + APoint(0, 2.5)
      D = C + APoint(2*POM_thickness+diameter, 0)
      E = D + APoint(0, -2.5)
      F = E + APoint(-POM_thickness, 0)
      G = F + APoint(0, -2.5)
      set_layer("轮廓线")
      pnts = [A, B, C, D, E, F, G, base, A]
      pnts = [j for i in pnts for j in i]
      pnts = aDouble(pnts)
      self.acad.model.AddPolyLine(pnts)
      
      set_layer("中心线")
      
      self.acad.model.AddLine(APoint(A.x+diameter/2, A.y-5), APoint(A.x+diameter/2, A.y+5))
      set_layer("标注线")
     
      
      
      
      
      dim_list = [None]*6
      #添加左侧总高标注
      DimLineLocation_C1= C + APoint(-9, 0)
      dim_list[1] = self.acad.model.AddDimRotated(C, base, DimLineLocation_C1, 0)
      DimLineLocation_C = C + APoint(-4, 0)
      #添加左侧厚度标注
      dim_list[2] = self.acad.model.AddDimRotated(C, B, DimLineLocation_C, math.radians(90))
      DimLineLocation_D = D + APoint(0, 25)
      #添加总口径标注
      dim_list[3] = self.acad.model.AddDimRotated(D, C, DimLineLocation_D, 0)
      dim_list[3].TextOverride = "Φ<>"
      DimLineLocation_G = G + APoint(0, -11)
      dim_list[4] = self.acad.model.AddDimRotated(base, G, DimLineLocation_G, 0)
      dim_list[4].TextOverride = "Φ<>"
      dim_list[4].ToleranceDisplay = 2
      dim_list[4].ToleranceUpperLimit = -0.01
      dim_list[4].ToleranceLowerLimit = 0.06
      dim_list[4].TolerancePrecision = 3
      dim_list[4].ToleranceHeightScale = 0.7
def draw_port(self, parameter):
      """绘制夹具端口"""
      base = parameter["base"]
      diameter = parameter["diameter"]
      Cu_thickness = parameter["Cu_thickness"]
      base2 = base + APoint(diameter/2-2.5, Cu_thickness)
      A = base2 + APoint(0, 2)
      B = A + APoint(-1.7, 0)
      C = B + APoint(0, 2.5)
      D = C + APoint(8.4, 0)
      E = D + APoint(0, -2.5)
      F = E + APoint(-1.7, 0)
      G = F + APoint(0, -2)
      set_layer("轮廓线")
      pnts = [A, B, C, D, E, F, G, base2, A]
      pnts = [j for i in pnts for j in i]
      pnts = aDouble(pnts)
      self.acad.model.AddPolyLine(pnts)
      self.acad.model.AddLine(A, F)
      set_layer("标注线")
      DimLineLocation_F = F + APoint(0, 9)
      dim_list = [None]*6
      dim_list[0] = self.acad.model.AddDimRotated(A, F, DimLineLocation_F, 0)
      dim_list[0].TextOverride = "Φ<>"
      dim_list[0].ToleranceDisplay = 2
      dim_list[0].ToleranceUpperLimit = 0.05
      dim_list[0].ToleranceLowerLimit = -0.03
      dim_list[0].TolerancePrecision = 3
      dim_list[0].ToleranceHeightScale = 0.7
      DimLineLocation_D = D + APoint(0,16)
      dim_list[1] = self.acad.model.AddDimRotated(C, D, DimLineLocation_D, 0)
      dim_list[1].TextOverride = "Φ<>"
      DimLineLocation_D = APoint(D.x + 8 + diameter/2, D.y)
      dim_list[2] = self.acad.model.AddDimRotated(E, D, DimLineLocation_D, math.radians(90))
      DimLineLocation_D = APoint(D.x + 2 + diameter/2, D.y)
      dim_list[3] = self.acad.model.AddDimRotated(G, D, DimLineLocation_D, math.radians(90))