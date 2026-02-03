# drawing_operations.py
import math
from pyautocad import APoint, aDouble
import time
class DrawingOperations:
    def __init__(self, acad, set_layer_func):
      
        self.acad = acad
        self.set_layer = set_layer_func


    def draw_views(self, geom, drawing_type="XJMJM"):
        """绘制所有视图"""
        #------绘制主视图------#
        self.draw_main_view(geom,drawing_type=drawing_type)
        #------绘制俯视图------#
        if drawing_type=="XJMJM" or drawing_type=="XPMJM":
            self.draw_top_view(geom)#只有这两类绘制俯视图

##---------main view-------------#    
    def draw_main_view(self, geom,drawing_type=None):
        """绘制主视图
        """
        radius = geom["radius"]
        chord_length = geom["chord_length"]
        if (drawing_type=="XJMJM" or drawing_type=="GPMXJ") and (abs(radius)<11 or chord_length<20):
            
            self._draw_main_view_WP(geom)
        else:   
  
            if radius > 0:
                self._draw_main_view_positive_radius(geom)
            elif radius < 0:
                self._draw_main_view_negative_radius(geom)    
        


        
        self.set_layer("轮廓线")
        # 中心小圆弧，r固定为4
        self.acad.model.AddArc(geom["center2"], 4, math.radians(90), math.radians(180))
        
         # 绘制底座
        self.draw_bottom(geom,drawing_type=drawing_type)
          # 中心线
        self.draw_center_line(geom)
        
        
        print("缩放到范围...")
       
        self.acad.doc.SendCommand("_.zoom _e ")
        time.sleep(1.0)  # 增加等待时间
             
      
    def _draw_main_view_WP(self, geom,drawing_type="XJMJM"):
        "绘制小口径成型丸片的底座"
        self.set_layer("轮廓线")
        point=[None]*10
        if geom["radius"]<0:
            left_point=geom["left_pointN"]
            right_point=geom["right_pointN"]
        else:
            left_point=geom["left_point"]
            right_point=geom["right_point"]
        point[0]=APoint(left_point.x, left_point.y)
        point[1]=APoint(left_point.x, left_point.y+2)
        point[2]=APoint(-0.75, left_point.y+2)
        point[3]=APoint(-0.75, left_point.y+3)
        point[4]=APoint(0.75, left_point.y+3)
        point[5]=APoint(0.75, left_point.y+2)
        point[6]=APoint(right_point.x, left_point.y+2)
        point[7]=APoint(right_point.x, left_point.y)
        point[8]=APoint(left_point.x, left_point.y)
        point[9]=APoint(0, left_point.y)
        pnts=[point[0],point[1],point[2],point[3],point[4],point[5],point[6],point[7],point[8],point[9]]
     
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        self.acad.model.AddLine(point[6]+APoint(-0.75,0), point[6])

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
        """绘制主视图R<0
        """
        self.set_layer("轮廓线")
       
        # 画弦和直线，统一剖面线到左侧，所以这里绘制右侧直线
        self.acad.model.AddLine( geom["left_point"], geom["right_point"])
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_U"]), APoint(geom["center"].x + 5, geom["y_U"]))
        self.acad.model.AddLine(APoint(geom["center"].x, geom["y_M"]), APoint(geom["center"].x + 5, geom["y_M"]))
        self.acad.model.AddLine(APoint(geom["center"].x, geom["chord_y"]-geom["a"]), APoint(geom["center"].x+geom["half_chordN"], geom["chord_y"]-geom["a"]))
        
        # 创建圆弧,只有左侧有剖面线，因此只需要绘制左侧的圆弧
        center=geom["center"]
        arc = self.acad.model.AddArc(
            center, 
            geom["abs_radius"], 
            math.radians(geom["left_angle"]), 
            math.radians(270)
        )
        #创建下方圆弧
        radius2=geom["radius2"]
       
        arc_down = self.acad.model.AddArc(
            center, radius2, math.pi*1.5+geom["theta_small"], math.pi*1.5+geom["theta_big"])#右半边的圆弧
        
        arc_down2=self.acad.model.AddArc(
            center, radius2, math.pi*1.5-geom["theta_big"],math.pi*1.5-geom["theta_small"])#左半边的圆弧
        
        point_l=geom["left_pointN"]
        point_r=geom["right_pointN"]

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
        """绘制俯视图,
        1. 绘制中心小圆,
        2. 绘制中心圆弧(优弧，并标注弦长),
        3. 标注直径,
        由于俯视图不常用，所以直接将绘图与标注集成在一起。
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
        chord_to_center = radius_down2*math.cos(half_theta_rad2)
        l = APoint(-half_chord2, chord_to_center)+center_down
        r = APoint(half_chord2, chord_to_center)+center_down

        right_angle2 = math.pi-half_theta_rad2
        left_angle2 = math.pi+half_theta_rad2
        
        if geom["half_chord"]+1 >= 9:
            self.set_layer("虚线")
            arc3 = self.acad.model.AddArc( center_down, radius_down2, left_angle2, right_angle2)
            # self.acad.doc.SendCommand(f'_LINE {arc3.StartPoint[0]},{arc3.StartPoint[1]} {arc3.EndPoint[0]},{arc3.EndPoint[1]} \n')
            line1=self.acad.model.AddLine(l, r)
            # 设置line1的线型比例为0.2
            line1.LinetypeScale = 0.2
        else:
            self.set_layer("轮廓线")
            arc3 = self.acad.model.AddArc(center_down, radius_down2, left_angle2, right_angle2)
            line1=self.acad.model.AddLine(l, r)
        # 给 line1 添加线性标注
        dim1 = self.acad.model.AddDimAligned(l, r,APoint(l.x, l.y + 7) )
        dim2 = self.acad.model.AddDimRotated(
            l, 
            APoint((l.x + r.x) / 2, center_down.y - 9),
            APoint(l.x -geom["half_chord"]-5, l.y), 
            math.radians(90)
        )
        # 给标注文本增加括号
        dim2.TextOverride = "(<>)"
            
        
        # 主圆（外圆）
        self.set_layer("轮廓线")
        self.acad.model.AddCircle(center_down, geom["half_chord"])
        if radius < 0:
        # 负半径特有：绘制额外的外圆
        # 外圆半径 = half_chord + 1，与主圆共享同一中心点
           
            self.set_layer("轮廓线")
            self.acad.model.AddCircle(center_down, geom["half_chord"]+1)
            self.set_layer("标注线")
            self.dia(center_down, geom["half_chord"]+1, math.radians(70))
        
        self.set_layer("标注线")
        self.dia(center_down, geom["half_chord"], math.radians(45)) 
        self.dia(center_down, 4, 0) 
        if geom["chord_length"] >= 32:
            self.dia(center_down, 9, math.radians(135),1)   
        else:
            self.dia(center_down, 9, math.radians(135),12)
        return arc3, line1, dim1, dim2

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
        center_line_start = APoint(geom["center"].x, geom["y_L"]+60)
        center_line_end = APoint(geom["center"].x, geom["y_U"]-50)
        center_line = self.acad.model.AddLine(center_line_start, center_line_end)
        center_line.Color = 1
        
        try:
            center_line.Linetype = "CENTER2"
            # 虚线通常需要较小的比例
            center_line.LinetypeScale = 0.1  # 使虚线更密集
        except:
            try:
                center_line.Linetype = "CENTER"
                center_line.LinetypeScale = 0.1
            except:
                pass
    
    
    
       