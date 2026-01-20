from tracemalloc import start
import math
from pyautocad import APoint, aDouble
from utils import set_layer
class POM:
    
    def __init__(self, acad):
        self.acad = acad
        self.center_h=0
    
    def draw_pom(self, parameter):
        """绘制标准夹具
        parameter（夹具参数）"""
        B = parameter["base"]
        #这里的height是镜片被夹住部分的高度，包括所垫的绒布的厚度。
        height = parameter["height"]
        radius = parameter["radius"]
        diameter = parameter["diameter"]

        A = B + APoint(0, height)

        theta=math.asin(diameter/(2*abs(radius)))
        
        
        self.center_h=abs(radius)*math.cos(theta)
        if radius>0:
            center=APoint(A.x+diameter/2, A.y+self.center_h)
            start_angle=1.5*math.pi-theta
            end_angle=1.5*math.pi+theta
            
        else:
            center=APoint(A.x+diameter/2, A.y-self.center_h)
            start_angle=0.5*math.pi-theta
            end_angle=0.5*math.pi+theta
        arc_center=APoint(0,-radius)+center
        set_layer("轮廓线")
        self.acad.model.AddArc(center, abs(radius), start_angle, end_angle)  

       

        C = B + APoint(-0.5, 0)
        D = C + APoint(-1,1)
        if radius>0:
            E = A + APoint(-1.5,6)
            F = A + APoint(diameter/2-4.2, 6)
        else:#夹具是凹的情况
            E = A + APoint(-1.5,abs(radius)-self.center_h+6)
            F = A + APoint(diameter/2-4.2,abs(radius)-self.center_h+6)


        A1= A + APoint(diameter, 0)    
        B1= B + APoint(diameter, 0)
        C1= C + APoint(diameter+1, 0)
        D1= D + APoint(diameter+3,0)
        E1= E + APoint(diameter+3,0)
        F1= F + APoint(8.4,0)

        set_layer("轮廓线")
        pnts = [A, B, C, D, E, F]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        pnts1 = [A1, B1, C1, D1, E1, F1]
        pnts1 = [j for i in pnts1 for j in i]
        pnts1 = aDouble(pnts1)
        self.acad.model.AddPolyLine(pnts1)

        set_layer("中心线")

        self.acad.model.AddLine(APoint(A.x+diameter/2, A.y-5), APoint(A.x+diameter/2, A.y+5))

        set_layer("标注线")





        dim_list = [None]*10
         #添加左侧参考高度
        DimLineLocation_C2= C + APoint(-9, 0)
        
        dim_list[0] = self.acad.model.AddDimRotated(arc_center, E, DimLineLocation_C2, math.radians(90))
        dim_list[0].TextOverride = "(<>)"
       #添加左侧总高标注
        DimLineLocation_C1= C + APoint(-15, 0)
        dim_list[1] = self.acad.model.AddDimRotated(C, E, DimLineLocation_C1, math.radians(90))
        DimLineLocation_C = C + APoint(-4, 0)
        #添加左侧厚度标注
        dim_list[2] = self.acad.model.AddDimRotated(D, E, DimLineLocation_C, math.radians(90))
        #添加总口径标注
        DimLineLocation_E = E + APoint(0, 25)
        dim_list[3] = self.acad.model.AddDimRotated(E, E1, DimLineLocation_E, 0)

        DimLineLocation_B = B + APoint(0, -15)
        dim_list[4] = self.acad.model.AddDimRotated(B, B1, DimLineLocation_B, 0)
        dim_list[4].TextOverride = "Φ<>"
        dim_list[4].ToleranceDisplay = 2
        dim_list[4].ToleranceUpperLimit = 0.15
        dim_list[4].ToleranceLowerLimit = -0.1
        dim_list[4].TolerancePrecision = 3
        dim_list[4].ToleranceHeightScale = 0.7
        #添加右侧夹持厚度标注height
        DimLineLocation_B1 = B1 + APoint(9,0)
        dim_list[5] = self.acad.model.AddDimRotated(B1, A1, DimLineLocation_B1, math.radians(90))
       
       
        #添加半径标注
        angle_rad = math.radians(80)
        point_x = center.x - radius * math.cos(angle_rad)
        point_y = center.y - radius * math.sin(angle_rad)
        ChordPoint = APoint(point_x, point_y)#ChordPoint - 弦点/圆弧上的点（标注的终点
        dim_list[6] = self.acad.model.AddDimRadial(center, ChordPoint, 10)
        try:
            dim_list[6].StyleName = "ZqStandard$4"# 设置标注样式
            dim_list[6].TextPosition = APoint(-7, -7) + ChordPoint# 标注文字的位置（标注
            dim_list[6].Update()
        except Exception:     
                pass
       
    def draw_port(self, parameter):
        """绘制夹具端口"""
        base = parameter["base"]
        height = parameter["height"]
        A=base + APoint(0, height)
        diameter = parameter["diameter"]
        height = parameter["height"]
        radius = parameter["radius"]
        if radius<0:
            I = A + APoint(diameter/2-2.5, abs(radius)-self.center_h+1)
        else:
            I = A + APoint(diameter/2-2.5, 1)
        
        H = I + APoint(0, 2)
        G = H + APoint(-1.7, 0)
        F = G + APoint(0, 3)
        F1 = F + APoint(8.4, 0)
        G1 = F1 + APoint(0, -3)
        H1 = G1 + APoint(-1.7, 0)
        I1 = H1 + APoint(0, -2)
        set_layer("轮廓线")
        pnts = [F,G,H,I,I1,H1,G1,F1,F]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        self.acad.model.AddLine(H, H1)
        set_layer("标注线")
        DimLineLocation_H = H + APoint(0, 9)
        dim_list = [None]*6
        dim_list[0] = self.acad.model.AddDimRotated(H, H1, DimLineLocation_H, 0)
        dim_list[0].TextOverride = "Φ<>"
        dim_list[0].ToleranceDisplay = 2
        dim_list[0].ToleranceUpperLimit = 0.05
        dim_list[0].ToleranceLowerLimit = -0.03
        dim_list[0].TolerancePrecision = 3
        dim_list[0].ToleranceHeightScale = 0.7
        DimLineLocation_F = F + APoint(0,16)
        dim_list[1] = self.acad.model.AddDimRotated(F, F1, DimLineLocation_F, 0)
        dim_list[1].TextOverride = "Φ<>"
        DimLineLocation_F1 = APoint(F1.x + 8 + diameter/2, F1.y)
        dim_list[2] = self.acad.model.AddDimRotated(I1, F1, DimLineLocation_F1, math.radians(90))
        DimLineLocation_F11 = APoint(F1.x + 2 + diameter/2, F1.y)
        dim_list[3] = self.acad.model.AddDimRotated(G1, F1, DimLineLocation_F11, math.radians(90))
