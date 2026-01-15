# drawing_operations.py
import math
from pyautocad import APoint,aDouble

class DrawingOperations:
    def __init__(self, acad, set_layer_func):
        """
        初始化绘图操作类
        
        Args:
            acad: AutoCAD连接对象
            set_layer_func: 设置图层的函数
        """
        self.acad = acad
        self.set_layer = set_layer_func
    
    def draw_main_view(self, geom):
        """绘制主视图"""
        self.set_layer("轮廓线")
        
        # 画弦和直线
        self.acad.model.AddLine(APoint(0, geom["chord_y"]), geom["right_point"])
        self.acad.model.AddLine(APoint(0, geom["a"]), APoint(5, geom["a"]))
        self.acad.model.AddLine(APoint(0, geom["b"]), APoint(5, geom["b"]))
        
        # 创建圆弧
        arc = self.acad.model.AddArc(
            geom["center"], 
            geom["abs_radius"], 
            math.radians(geom["right_angle"]), 
            math.radians(geom["left_angle"])
        )
        
        # 中心小圆弧
        self.acad.model.AddArc(geom["center2"], 4, math.radians(90), math.radians(180))
        
        # 绘制多段线
        self.draw_polylines(geom)
        
        # 虚线
        self.set_layer("虚线")
        self.acad.model.AddLine(APoint(3, geom["b"]), APoint(3, geom["c"]))
        
        return arc
    
    def draw_polylines(self, geom):
        """绘制多段线"""
        # 左侧多段线
        pnts = [
            geom["left_point"], 
            APoint(-geom["half_chord"], geom["a"]),
            APoint(-5, geom["a"]), 
            APoint(-5, geom["b"]), 
            APoint(-9, geom["b"]),
            APoint(-9, geom["c"]),
            APoint(0, geom["c"])
        ]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        
        # 右侧多段线
        pnts2 = [
            geom["right_point"], 
            APoint(geom["half_chord"], geom["a"]),
            APoint(5, geom["a"]), 
            APoint(5, geom["b"]), 
            APoint(9, geom["b"]),
            APoint(9, geom["c"])
        ]
        pnts2 = [j for i in pnts2 for j in i]
        pnts2 = aDouble(pnts2)
        self.acad.model.AddPolyLine(pnts2)
    
    def draw_top_view(self, geom):
        """绘制俯视图"""
        self.set_layer("虚线")
        center_down = APoint(0, -60)
        
        # 中心小圆
        self.acad.model.AddCircle(center_down, 4)
        
        # 中心圆弧
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
                center_down, 
                radius_down2, 
                math.radians(left_angle2), 
                math.radians(right_angle2)
            )
            self.draw_line(arc3.StartPoint[0], arc3.StartPoint[1], 
                          arc3.EndPoint[0], arc3.EndPoint[1])
        else:
            self.set_layer("轮廓线")
            arc3 = self.acad.model.AddArc(
                center_down, 
                radius_down2, 
                math.radians(left_angle2), 
                math.radians(right_angle2)
            )
            self.draw_line(arc3.StartPoint[0], arc3.StartPoint[1], 
                          arc3.EndPoint[0], arc3.EndPoint[1])
        
        # 外圆
        self.set_layer("轮廓线")
        self.acad.model.AddCircle(center_down, geom["half_chord"])
        
        # 标注直径
        self.set_layer("尺寸线")
        self._dimension_top_view(center_down, geom)
    
    def draw_line(self, x1, y1, x2, y2):
        """绘制直线"""
        self.acad.doc.SendCommand(f'_LINE {x1},{y1} {x2},{y2} \n')
    
    def _dimension_top_view(self, center_down, geom):
        """俯视图标注（内部方法）"""
        def dia(center, radius, angle):
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            ChordPoint = center + APoint(x, y)
            FarChordPoint = center - APoint(x, y)
            LeaderLength = 10
            return self.acad.model.AddDimDiametric(ChordPoint, FarChordPoint, LeaderLength)
        
        dia(center_down, geom["half_chord"], math.radians(45))
        dia(center_down, 4, 0)
        dia(center_down, 4, math.radians(90))
    
    def draw_center_line(self, radius):
        """绘制中心线"""
        self.set_layer("中心线")
        sym_line_start = APoint(0, 30)
        sym_line_end = APoint(0, -30)
        sym_line = self.acad.model.AddLine(sym_line_start, sym_line_end)
        sym_line.Color = 1
        
        try:
            sym_line.Linetype = "CENTER"
        except:
            try:
                sym_line.Linetype = "CENTER2"
            except:
                pass
    
    def add_hatching(self, create_hatch_func):
        """添加剖面线"""
        self.set_layer("剖面线")
        create_hatch_func(self.acad, scale=0.5)
    
    def insert_all_blocks(self, geom, insert_block, insert_XJMJM, insert_Zhoufan):
        """插入所有图块"""
        insertionPnt = APoint(geom["center"].x - 180, geom["center"].y - 270)
        insert_block(insertionPnt)
        
        insertionPnt2 = APoint(geom["center"].x - 412, geom["center"].y - 1902)
        insert_XJMJM(insertionPnt2)
        
        self.set_layer("轮廓线")
        insert_Zhoufan(insertionPnt2)