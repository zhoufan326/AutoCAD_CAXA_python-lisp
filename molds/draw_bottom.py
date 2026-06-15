# draw_bottom.py - 绘制底座模块
import math
import numpy as np
from pydoc import locate
from utils.com_interface import APoint, aDouble
from utils import AD,LD


def draw_bottom(self):
    """绘制底座部分
    """
      
    left = [0] * 5
    right = [0] * 5
    
    if self.drawing_type in ("XJMJM", "XPMJM"):
        left[0] = APoint(self.center.x - self.width_Connect/2, self.y_connect)
        left[1] = APoint(self.center.x - self.width_Connect/2, self.y_Up)
        left[2] = APoint(self.center.x - self.width_Up/2, self.y_Up)
        left[3] = APoint(self.center.x - self.width_Low/2, self.y_Low)
        locate1=left[1]+APoint(-7, 0)
        line1,dim1 = LD(self.acad, left[0], left[1], locate1)
        line12=self.acad.model.AddLine(left[1], left[2])
        line12.Layer = "轮廓线"
        locate2=left[2]+APoint(-1, 0)
        line2,dim2 = LD(self.acad, left[2], left[3], locate2)

        right[0] = APoint(self.center.x + self.width_Connect/2, self.y_connect)
        right[1] = APoint(self.center.x + self.width_Connect/2, self.y_Up)
        right[2] = APoint(self.center.x + self.width_Up/2, self.y_Up)
        right[3] = APoint(self.center.x + self.width_Low/2, self.y_Low)
        lowpoint = right[3]
        #绘制右侧非剖面的轮廓直线
        self.acad.model.AddLine(APoint(self.center.x, self.y_connect), right[0])
        self.acad.model.AddLine(APoint(self.center.x, self.y_Up), right[1])

        # 使用多段线连接右侧4个点
        poly_points = [j for i in right[:4] for j in i]
        poly_points = aDouble(poly_points)
        polyline = self.acad.model.AddPolyLine(poly_points)
        polyline.Layer = "轮廓线"
        #底座下方线段及标注
        locate3=right[3]+APoint(0, -17)
        line3,dim3 = LD(self.acad, left[3], right[3], locate3,-0.02,0.04)
        if dim3 is not None:
            dim3.TextOverride = "%%c<>"
            dim3.Update()
        
        line4 = self.acad.model.AddLine(APoint(3, self.y_Up), APoint(3, self.y_Low))
        line4.Layer = "虚线"

    else:
        self.width_Up=14
        self.width_Low=10
        
        left[0] = APoint(self.center.x - self.width_Connect/2, self.y_connect)
        left[1] = APoint(self.center.x - self.width_Connect/2, self.y_Up)
        left[2] = APoint(self.center.x - self.width_Up/2, self.y_Up)
        self.acad.model.AddLine(left[1], left[2])
        left[3] = APoint(self.center.x - self.width_Up/2, self.y_Up2)
        left[4] = APoint(self.center.x - self.width_Low/2, self.y_Low)
        
        locate1=left[1]+APoint(-7, 0)
        locate2=left[2]+APoint(-7, 0)
        locate3=left[4]+APoint(-7, 0)
        line1,dim1 = LD(self.acad, left[0], left[1], locate1)
        line2,dim2 = LD(self.acad, left[2], left[3], locate2)
        line3,dim3 = LD(self.acad, left[3], left[4], locate3,dim_type="Rotated",dim_angle=math.pi/2)
        
        right[0] = APoint(self.center.x + self.width_Connect/2, self.y_connect)
        right[1] = APoint(self.center.x + self.width_Connect/2, self.y_Up)
        right[2] = APoint(self.center.x + self.width_Up/2, self.y_Up)
        right[3] = APoint(self.center.x + self.width_Up/2, self.y_Up2)
        right[4] = APoint(self.center.x + self.width_Low/2, self.y_Low)
        lowpoint = right[4]

        
        # 使用多段线连接右侧5个点
        poly_points = [j for i in right[:5] for j in i]
        poly_points = aDouble(poly_points)
        polyline = self.acad.model.AddPolyLine(poly_points)
        polyline.Layer = "轮廓线"
        
        locate4=right[4]-APoint(0, 15)
        dim4 = self.acad.model.AddDimAligned(left[3], right[3], locate4)
        dim4.TextOverride = "%%C<>"
        dim4.Layer = "标注线"
        dim4.Update()
        
        locate5=right[4]+APoint(0, -8)
        line5,dim5 = LD(self.acad, left[4], right[4], locate5,-0.02,0.04)
        dim5.TextOverride = "%%c<>"
        dim5.Update()


        # 添加锥度标注
        arrow_pnt = APoint((self.width_Up+self.width_Low)/4, (self.y_Low + self.y_Up) / 2)
        baseline_pnt = APoint((self.width_Up+self.width_Low)/4+10, (self.y_Low + self.y_Up) / 2 - 5)
        
        pnts_array = np.array([arrow_pnt, baseline_pnt]).flatten()
        pnts_array = aDouble(pnts_array)
        leader = self.acad.model.AddMLeader(pnts_array, 0)
        leader.DoglegLength = 8
        leader.LandingGap = 3
        leader.TextString = "锥度1：10"
        leader.Layer = "标注线"
        
        #绘制右侧非剖面的轮廓直线
        self.acad.model.AddLine(APoint(self.center.x, self.y_connect), right[0])
        self.acad.model.AddLine(APoint(self.center.x, self.y_Up), right[1])
        self.acad.model.AddLine(APoint(self.center.x, self.y_Up2), right[3])
        
    # 使用AD函数绘制底部圆槽
    arc, dim_arc = AD(self.acad, self.center2, 4, math.pi/2, math.pi, 7,locate_angle=0.75*math.pi)
    dim_arc.TextPosition = APoint(self.center2.x + 3, self.center2.y - 3)

    #连接轴直径标注
    if self.b != 0: 
        dim_connect_locate=right[0]+APoint(14,-4)
        dim_connect = self.acad.model.AddDimAligned(left[0],right[0], dim_connect_locate)
        dim_connect.TextOverride = "%%c<>"
        dim_connect.TextPosition = right[0]+APoint(10,  -4)
       
        dim_connect.Layer = "标注线"
    #总高标注
    self.arc_center_point = self.center + APoint(0, self.radius)
    dim_total = self.acad.model.AddDimRotated(self.arc_center_point, lowpoint, self.right_pointN+APoint(5, 0),math.pi/2)
    dim_total.TextOverride = "(<>)"   
    dim_total.Layer = "标注线"
    
    if self.radius <0:  
        dim_total2 = self.acad.model.AddDimRotated(self.right_pointN, lowpoint, self.right_pointN+APoint(15,0),math.pi/2)
        dim_total2.TextOverride = "(<>)"
        dim_total2.Layer = "标注线"
