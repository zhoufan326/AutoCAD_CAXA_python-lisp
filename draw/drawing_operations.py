# drawing_operations.py
import math
from pyautocad import APoint, aDouble

class DrawingOperations:
    def __init__(self, acad, set_layer_func):
      
        self.acad = acad
        self.set_layer = set_layer_func


    def draw_views(self, geom, drawing_type="XJMJM"):
        """绘制所有视图"""
        self.draw_main_view(geom,drawing_type=drawing_type)
        
       

        if drawing_type=="XJMJM" or drawing_type=="XPMJM":
            self.draw_top_view(geom)#只有这两类绘制俯视图

    
    def draw_main_view(self, geom,drawing_type="XJMJM"):
        """绘制主视图
        type: 主视图类型，默认"XJMJM"
        
        """
        radius = geom["radius"]
        
        if radius > 0:
            self._draw_main_view_positive_radius(geom)
            
        elif radius < 0:
            self._draw_main_view_negative_radius(geom)
            

        self.set_layer("轮廓线")
        # 中心小圆弧，r固定为4
        self.acad.model.AddArc(geom["center2"], 4, math.radians(90), math.radians(180))
         # 绘制多段线
        self.draw_bottom(geom,drawing_type=drawing_type)
        
       
        
        # 中心线
        self.draw_center_line(geom)


    def _draw_main_view_positive_radius(self, geom):
        """绘制正半径主视图（凸圆弧）"""
        self.set_layer("轮廓线")
        self.draw_polylines_positive(geom)
        # self.draw_polylines(geom)


        # 画直线，对于凸圆弧，只画对称轴右侧的线
        self.acad.model.AddLine(APoint(geom["center"].x, geom["chord_y"]), geom["right_point"])
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_U"]), APoint(geom["center"].x + 5, geom["y_U"]))
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_M"]), APoint(geom["center"].x + 5, geom["y_M"]))
       
        
        # 创建圆弧
        arc = self.acad.model.AddArc(
            geom["center"], 
            geom["abs_radius"], 
            math.radians(geom["right_angle"]), 
            math.radians(geom["left_angle"])
        )#逆时针绘制圆弧，因此先右后左
        
        return arc
    
    def _draw_main_view_negative_radius(self, geom):
        """绘制负半径主视图（凹圆弧）
        
        待实现：负半径时的凹圆弧绘制逻辑
        需要根据凹圆弧的几何特性调整绘图参数和顺序
        """
        self.set_layer("轮廓线")
       
        # 画弦和直线
        self.acad.model.AddLine( geom["left_point"], geom["right_point"])
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_U"]), APoint(geom["center"].x + 5, geom["y_U"]))
        #统一剖面线到左侧
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_M"]), APoint(geom["center"].x + 5, geom["y_M"]))
        # self.acad.model.AddLine(APoint(geom["center"].x-9, geom["y_L"]), APoint(geom["center"].x + 9, geom["y_L"]))
        

        
        # 创建圆弧,只有左侧有剖面线，因此只需要绘制左侧的圆弧
        arc = self.acad.model.AddArc(
            geom["center"], 
            geom["abs_radius"], 
            math.radians(geom["left_angle"]), 
            math.radians(270)
        )
        #创建下方圆弧
        half_theta_radB = math.asin((geom["half_chord"]+1) / geom["abs_radius"])
        arc_down = self.acad.model.AddArc(geom["center"]-APoint(0, geom["a"]), geom["abs_radius"], 
          
            math.pi*1.5+math.asin(5/ geom["abs_radius"]), math.pi*1.5+half_theta_radB)#右半边的圆弧
        arc_down2=self.acad.model.AddArc(
            geom["center"]-APoint(0, geom["a"]), geom["abs_radius"], 

            math.pi*1.5-half_theta_radB,math.pi*1.5-math.asin(5/ geom["abs_radius"]))#左半边的圆弧
        point_l=geom["left_point"]-APoint(1,0)
        point_r=geom["right_point"]+APoint(1,0)

  #绘制两条连接圆弧的竖线
        self.acad.doc.SendCommand(f'_LINE {arc_down2.StartPoint[0]},{arc_down2.StartPoint[1]} {point_l.x},{point_l.y} \n')

        self.acad.doc.SendCommand(f'_LINE {point_r.x},{point_r.y} {arc_down.EndPoint[0]},{arc_down.EndPoint[1]} \n')
        
        self.draw_polylines_N(geom)
        # self.draw_polylines(geom)
        
        

        
        return arc, arc_down, arc_down2
        
    
    def draw_polylines_positive(self, geom):
        """绘制多段线
         radius > 0    
        """
    
        pnts = [
            APoint(geom["left_point"].x, geom["left_point"].y),
            APoint(geom["left_point"].x, geom["y_U"]),
            APoint(geom["center"].x-5, geom["y_U"]), 
            
        ]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        
        # 右侧多段线
        pnts2 = [
            APoint(geom["right_point"].x, geom["right_point"].y), 
            APoint(geom["right_point"].x, geom["y_U"]),
            APoint(geom["center"].x+5, geom["y_U"]), 
            
        ]

        pnts2 = [j for i in pnts2 for j in i]
        pnts2 = aDouble(pnts2)
        self.acad.model.AddPolyLine(pnts2)
    
    def draw_polylines_N(self, geom):
        """绘制多段线
         radius < 0    
        """
        
        pnts = [APoint(geom["left_point"].x, geom["left_point"].y),
             APoint(geom["left_point"].x-1, geom["left_point"].y), 
             
             ]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        
        # 右侧多段线
        pnts2 = [APoint(geom["right_point"].x, geom["right_point"].y), 
              APoint(geom["right_point"].x+1, geom["right_point"].y), 
           
             ]

        pnts2 = [j for i in pnts2 for j in i]
        pnts2 = aDouble(pnts2)
        self.acad.model.AddPolyLine(pnts2)

    def draw_bottom(self, geom,drawing_type):
        """绘制底座部分
        """
      
        if drawing_type=="XJMJM" or drawing_type=="XPMJM":
            B = APoint(geom["center"].x-9, geom["y_M"])
            C = APoint(geom["center"].x-9, geom["y_L"])
       
            pnts = [
                APoint(geom["center"].x-5, geom["y_U"]), 
                APoint(geom["center"].x-5, geom["y_M"]), 
                B,
                C,
                APoint(geom["center"].x+9, geom["y_L"]),
                APoint(geom["center"].x+9, geom["y_M"]),
                APoint(geom["center"].x+5, geom["y_M"]),
                APoint(geom["center"].x+5, geom["y_U"]),  
            ]
            pnts = [j for i in pnts for j in i]
            pnts = aDouble(pnts)
            self.acad.model.AddPolyLine(pnts)

             # 虚线
            self.set_layer("虚线")
            self.acad.model.AddLine(APoint(3, geom["y_M"]), APoint(3, geom["y_L"]))
            # ---------当模子不是精磨和抛光模时---------
        else:
            self.acad.model.AddLine(APoint(0, geom["y_M2"]), APoint(7, geom["y_M2"]))

            B = APoint(geom["center"].x-7, geom["y_M"])
            B2=APoint(geom["center"].x-7, geom["y_M2"])
            C = APoint(geom["center"].x-5, geom["y_L"])
            pnts2 = [
                APoint(geom["center"].x-5, geom["y_U"]), 
                APoint(geom["center"].x-5, geom["y_M"]), 
                B,B2, C,
                APoint(geom["center"].x+5, geom["y_L"]),
                APoint(geom["center"].x+7, geom["y_M"]-5),
                APoint(geom["center"].x+7, geom["y_M"]),
                #这三点是B,B2,C的对称点
                APoint(geom["center"].x+5, geom["y_M"]),
                APoint(geom["center"].x+5, geom["y_U"]),  
            ]
            pnts2 = [j for i in pnts2 for j in i]
            pnts2 = aDouble(pnts2)
            self.acad.model.AddPolyLine(pnts2)

           
    




    def draw_top_view(self, geom):
        """绘制俯视图
        """
        radius = geom["radius"]
        
        # 中心点（用于俯视图），使用 geometry 中计算的 center2
        center_down = APoint(0,-40)+geom["center2"]
        # 中心小圆
        self.acad.model.AddCircle(center_down, 4)
        
        # 中心圆弧,优弧
        radius_down2 = 9
        chord_length2 = 6
        half_chord2 = chord_length2 / 2
        half_theta_rad2 = math.asin(half_chord2 / radius_down2)
        half_theta_deg2 = math.degrees(half_theta_rad2)
        right_angle2 = 90 - half_theta_deg2
        left_angle2 = 90 + half_theta_deg2
        
        if geom["half_chord"] >= 9:
            self.set_layer("虚线")
            arc3 = self.acad.model.AddArc( 
                center_down, radius_down2, 
                math.radians(left_angle2),  math.radians(right_angle2))
            self.acad.doc.SendCommand(f'_LINE {arc3.StartPoint[0]},{arc3.StartPoint[1]} {arc3.EndPoint[0]},{arc3.EndPoint[1]} \n')
        else:
            self.set_layer("轮廓线")
            arc3 = self.acad.model.AddArc(
                center_down, radius_down2, 
                math.radians(left_angle2), math.radians(right_angle2))
            self.acad.doc.SendCommand(f'_LINE {arc3.StartPoint[0]},{arc3.StartPoint[1]} {arc3.EndPoint[0]},{arc3.EndPoint[1]} \n')
        
        # 主圆（外圆）
        self.set_layer("轮廓线")
        self.acad.model.AddCircle(center_down, geom["half_chord"])
        if radius < 0:
        # 负半径特有：绘制额外的外圆
        # 外圆半径 = half_chord + 1，与主圆共享同一中心点
           
            self.set_layer("轮廓线")
            self.acad.model.AddCircle(center_down, geom["half_chord"]+1)
            self.set_layer("尺寸线")
            self.dia(center_down, geom["half_chord"]+1, math.radians(70))
        
        self.set_layer("尺寸线")
        self.dia(center_down, geom["half_chord"], math.radians(45)) 
        self.dia(center_down, 4, 0) 
        if geom["chord_length"] >= 32:
            self.dia(center_down, 9, math.radians(135),1)   
        else:
            self.dia(center_down, 9, math.radians(135),12)   
    # 标注直径    
    def dia(self, center, radius, angle, leader_length=10): 
            """标注直径, center: 圆心, radius: 半径, angle: 角度"""
            x = radius * math.cos(angle) 
            y = radius * math.sin(angle) 


            ChordPoint = center + APoint(x, y) 
            FarChordPoint = center - APoint(x, y) 
            return self.acad.model.AddDimDiametric(ChordPoint, FarChordPoint, leader_length) 
        
    
    
    def draw_center_line(self, geom):
        """绘制中心线"""
        self.set_layer("中心线")
        sym_line_start = APoint(geom["center"].x, geom["y_L"]+60)
        sym_line_end = APoint(geom["center"].x, geom["y_U"]-30)
        sym_line = self.acad.model.AddLine(sym_line_start, sym_line_end)
        sym_line.Color = 1
        
        try:
            sym_line.Linetype = "CENTER2"
        except:
            try:
                sym_line.Linetype = "CENTER"
            except:
                pass
    
    
    
       