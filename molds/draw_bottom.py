# draw_bottom.py - 绘制底座模块
import math
from pydoc import locate
from pyautocad import APoint, aDouble
from utils import AD,LD


def bottom(self):
    """绘制底座部分
    """
    
    #连接轴的宽度
    width_Connect=10
    #底座的上宽度和下宽度
    width_Up=18
    width_Low=18
    if (abs(self.radius) < 11 or self.chord_length < 18):
        width_Connect=6
       
       
    left = [0] * 5
    right = [0] * 5
    
    if self.drawing_type in ("XJMJM", "XPMJM"):
        left[0] = APoint(self.center.x - width_Connect/2, self.y_connect)
        left[1] = APoint(self.center.x - width_Connect/2, self.y_Up)
        left[2] = APoint(self.center.x - width_Up/2, self.y_Up)
        left[3] = APoint(self.center.x - width_Low/2, self.y_Low)
        locate1=left[1]+APoint(-7, 0)
        line1,dim1 = LD(self.acad, left[0], left[1], locate1)
        line12=self.acad.model.AddLine(left[1], left[2])
        line12.Layer = "轮廓线"
        locate2=left[2]+APoint(-1, 0)
        line2,dim2 = LD(self.acad, left[2], left[3], locate2)

        right[0] = APoint(self.center.x + 5, self.y_connect)
        right[1] = APoint(self.center.x + 5, self.y_Up)
        right[2] = APoint(self.center.x + 9, self.y_Up)
        right[3] = APoint(self.center.x + 9, self.y_Low)
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
        width_Connect=10
        width_Up=14
        width_Low=10
        self.acad.model.AddLine(APoint(0, self.y_Up2), APoint(width_Up/2, self.y_Up2))
        
        left[0] = APoint(self.center.x - width_Connect/2, self.y_connect)
        left[1] = APoint(self.center.x - width_Connect/2, self.y_Up)
        left[2] = APoint(self.center.x - width_Up/2, self.y_Up)
        left[3] = APoint(self.center.x - width_Up/2, self.y_Up2)
        left[4] = APoint(self.center.x - width_Low/2, self.y_Low)
        line1,dim1 = LD(self.acad, left[0], left[1], left[0]-APoint(-7, 0))
        self.acad.model.AddLine(left[1], left[2])
        locate2=left[2]-APoint(-7, 0)
        line2,dim2 = LD(self.acad, left[2], left[3], locate2)
        locate3=left[4]-APoint(-7, 0)
        line3,dim3 = LD(self.acad, left[3], left[4], locate3)
        
        right[0] = APoint(self.center.x + width_Connect/2, self.y_connect)
        right[1] = APoint(self.center.x + width_Connect/2, self.y_Up)
        right[2] = APoint(self.center.x + width_Up/2, self.y_Up)
        right[3] = APoint(self.center.x + width_Up/2, self.y_Low)
        right[4] = APoint(self.center.x + width_Low/2, self.y_Low)
        lowpoint = right[4]
        self.acad.model.AddLine(APoint(self.center.x, self.y_connect), right[0])
        self.acad.model.AddLine(APoint(self.center.x, self.y_Up), right[1])
        self.acad.model.AddLine(APoint(self.center.x, self.y_Up2), right[3])
        
        # 使用多段线连接右侧5个点
        poly_points = [j for i in right[:5] for j in i]
        poly_points = aDouble(poly_points)
        polyline = self.acad.model.AddPolyLine(poly_points)
        polyline.Layer = "轮廓线"
        

        # 添加锥度标注
        arrow_pnt = APoint((width_Up+width_Low)/2, (self.y_Low + self.y_Up) / 2)
        baseline_pnt = APoint((width_Up+width_Low)/2+10, (self.y_Low + self.y_Up) / 2 - 5)
        
        pnts_array = np.array([arrow_pnt, baseline_pnt]).flatten()
        leader = self.acad.model.AddMLeader(pnts_array, 0)
        leader.DoglegLength = 8
        leader.LandingGap = 3
        leader.TextString = "锥度1：10"
        leader.Layer = "标注线"
        
        line4,dim4 = LD(self.acad, left[2], right[2], right[4]-APoint(0, 5),0.15,-0.05)  
        if dim4 is not None:
            dim4.TextOverride = "%%C<>"
            dim4.Update()
    
    # 使用AD函数绘制底部圆槽
    arc, dim_arc = AD(self.acad, self.center2, 4, math.pi/2, math.pi, 7,locate_angle=0.75*math.pi)
    dim_arc.TextPosition = APoint(self.center2.x + 3, self.center2.y - 3)

    #连接轴直径标注
    if self.b != 0: 
        dim5_locate=right[0]+APoint(14,-4)
        dim5 = self.acad.model.AddDimAligned(left[0],right[0], dim5_locate)
        dim5.TextOverride = "%%c<>"
        dim5.TextPosition = right[0]+APoint(10,  -4)
       
        dim5.Layer = "标注线"
    #总高标注
    self.arc_center_point = self.center + APoint(0, self.radius)
    dim_total = self.acad.model.AddDimRotated(self.arc_center_point, lowpoint, self.right_pointN+APoint(5, 0),math.pi/2)
    dim_total.TextOverride = "(<>)"   
    dim_total.Layer = "标注线"
    
    if self.radius <0:  
        dim_total2 = self.acad.model.AddDimRotated(self.right_pointN, lowpoint, self.right_pointN+APoint(15,0),math.pi/2)
        dim_total2.TextOverride = "(<>)"
        dim_total2.Layer = "标注线"