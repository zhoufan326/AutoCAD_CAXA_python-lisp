from pyautocad import Autocad, APoint
import math
import numpy as np
import comtypes
from datetime import datetime

comtypes.npsupport.enable()
# 启用COM类型支持
#comtypes 库在使用 numpy 数组作为参数时，需要先启用 numpy 互操作性支持。
"""
AutoCAD标注模块

提供两个主要函数：
- date_name: 添加日期和名称文本
- dimension: 添加图形标注
"""

acad = Autocad(create_if_not_exists=True)


def _get_doc(acad_obj):
    """获取AutoCAD文档对象"""
    return getattr(acad_obj, 'ActiveDocument', None) or getattr(acad_obj, 'doc', None)


def _safe_set_text_style(acad_obj, style_name: str):
    """安全设置文本样式"""
    doc = _get_doc(acad_obj)
    if not doc:
        return False
    
    try:
        doc.ActiveTextStyle = doc.TextStyles.Item(style_name)
        return True
    except Exception:
        # 备用方案：有时候需要通过 ActiveDocument 访问或样式不存在
        # try:
        #     if getattr(acad_obj, 'ActiveDocument', None) is not None:
        #         acad_obj.ActiveDocument.ActiveTextStyle = acad_obj.ActiveDocument.TextStyles.Item(style_name)
        #         return True
        # except Exception:
        #     return False
        return False

###——————————添加文本————————————#####

def date_name( name="XJMJM/R10-Φ10",date="2026/1/1"):
    """在图纸上添加两个日期文本和一个名称文本。

    返回创建的文本对象 (text1, text2, text3) 或 (None, None, None) 在失败时。
    """
    point1=APoint(70, 81)#上日期位置
    point2=APoint(-10, -102)#下日期位置
    point3=APoint(101, -75)#名称位置
    current_date = datetime.now()
    date= current_date.strftime("%Y/%m/%d")
    try:
        _safe_set_text_style(acad, "宋体")
    except Exception:
        pass

    # 下面开始创建文本
    created = [None, None, None]
    try:
        created[0] = acad.model.AddText(date, point1, 2.5)
    except Exception:
        created[0] = None

    try:
        created[1] = acad.model.AddText(date, point2, 2.5)
    except Exception:
        created[1] = None

    try:
        created[2] = acad.model.AddText(name, point3, 2.5)
        created[2].Alignment = 2#居中对齐
        created[2].TextAlignmentPoint = point3
        created[2].Update()
    except Exception:
        created[2] = None

    return tuple(created)


def dimension(geom=None,drawing_type=None):
    """创建一组标注对象并返回它们的元组。

    参数:
    geom: 包含标注几何信息的字典
    drawing_type: 图纸类型，默认"XJMJM"

    返回顺序与原实现相同：
    (dimRotObj, dimRotObjA, dimRotObjB, dimRotObjC, dimRotObj_down, dimRadObj1, dimRadObj2, dimRotObjD)
    不可用的对象以 None 填充。
    """
    # 尝试设置图纸样式（容错）
    try:
        _safe_set_text_style(acad, "ZqStandard")
    except Exception:
        pass
    
    created = [None] * 18#设置标注对象，18个标注对象，每个标注对象对应一个标注线

    try:
        RotationAngle = math.radians(0) # 旋转角默认设置为0
#------------计算标注用到的点坐标-----------------#
        # A、B、C三个点分别代表小写字母a、b、c三条线段的下端点
        A = APoint(-5, geom["y_U"])
        Ar= APoint(5, geom["y_U"])
        if drawing_type=="XJMJM" or drawing_type=="XPMJM":
            B = APoint(-9, geom["y_M"])
            C = APoint(-9, geom["y_L"])
            Cr = APoint(9, geom["y_L"])
        else:
            B = APoint(-7, geom["y_M"])
            C = APoint(-5, geom["y_L"])
        
        # D点表示底座中心最低点的位置
        D = APoint(geom["center"].x, geom["y_L"])
        arc_center_point = APoint(0, geom["radius"]) + geom["center"]# 上圆弧的中心点  

        
#------------下面计算标注线的定位点-----------------#
        if geom["radius"] <= 0:
            DimLineLocation_up = geom["left_point"] + APoint(0, 1.5)
            DimLineLocation_up2 = geom["left_point"] + APoint(0, 6)
        else:
            DimLineLocation_up = geom["center"] + APoint(0, geom["radius"]+1.5)
        #圆弧中心，到底座最低端参考高度的定位点
        #该定位点在模子右侧
        if geom["right_point"].x >= 9:
            DimLineLocation_D = APoint(6, 0) + geom["right_point"]
        elif 0 < geom["right_point"].x < 9:
            DimLineLocation_D = APoint(15, 0)

        
        # --------上口径标注----------#

        created[0] = acad.model.AddDimRotated(geom["left_point"], geom["right_point"], DimLineLocation_up, RotationAngle)
        created[0].TextOverride = "Φ<>"
        if geom["radius"] <= 0:
            #此时的口径标注使用半标注
            created[0].StyleName = "ZqStandard$0"
            #再增加一个外口径标注
            L_point = geom["left_pointN"]
            R_point = geom["right_pointN"] 
            created[9] = acad.model.AddDimRotated(L_point, R_point, DimLineLocation_up2, RotationAngle)
            created[9].TextOverride = "Φ<>"  
        #----------连接轴直径标注----------#
        if not geom["b"]==0: 
            DimLineLocation_A = A + APoint(0, -4)
            created[10] = acad.model.AddDimRotated(Ar, A, DimLineLocation_A, RotationAngle)
            created[10].TextOverride = "Φ<>"  
        # --------纵向线段标注----------#
        DimLineLocation_thick = geom["left_point"] + APoint(-8, 0)#A点的标注线位置，从模子最左侧偏移-8mm，向上偏移0mm    
        created[1] = acad.model.AddDimRotated(geom["left_point"], geom["left_point"] - APoint(0, geom["a"]), DimLineLocation_thick, math.radians(90))
        DimLineLocation_B = B + APoint(-1, 0)
        created[2] = acad.model.AddDimRotated(A, B, DimLineLocation_B, math.radians(90))       
        if drawing_type=="XJMJM" or drawing_type=="XPMJM":
            DimLineLocation_C = C + APoint(-3, 0)
            DimLineLocation_Cr = Cr + APoint(0, -7)
            created[3] = acad.model.AddDimRotated(C, B, DimLineLocation_C, math.radians(90))
             #------------ --------下口径标注--------------------#（底座直径标注）
            created[4] = acad.model.AddDimRotated(Cr, C, DimLineLocation_Cr, 0)
            created[4].TextOverride = "Φ<>"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = -0.02
            created[4].ToleranceLowerLimit = 0.04
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
            created[4].Update()
        elif drawing_type=="GPMXJ" or drawing_type=="JZM" or drawing_type=="JZM_KC" or drawing_type=="GPMJX":#添加小尾锥的标注
            DimLineLocation_C = C + APoint(-9, 0)
            DimLineLocation_C2 = C + APoint(-13, 0)
            created[3] = acad.model.AddDimRotated(B+APoint(0, -5), B, DimLineLocation_C, math.radians(90))                 
            created[13] = acad.model.AddDimRotated(B+APoint(0, -5),  C, DimLineLocation_C2, math.radians(90))            
            #插入多段线
            ArrowPnt = APoint(6, (geom["y_L"]+geom["y_M"])/2)
            BaselinePnt = APoint(10, (geom["y_L"]+geom["y_M"])/2-5)
            PntsArray = np.array([ArrowPnt, BaselinePnt])
            PntsArray = PntsArray.reshape(1, PntsArray.shape[0] * PntsArray.shape[1])[0]
            created[14] = acad.model.AddMLeader(PntsArray, 0)
                        # ArrowPnt 箭头位置；
                        # BaselinePnt 基线位置 ；
                        # 1 表示多重引线的索引号，为正整数。
                # MLeaderObj.ArrowheadSize = 2  # 指箭头高度；此项将覆盖系统变量DIMASZ的值。
            created[14].DoglegLength = 8
            created[14].LandingGap = 3  # 基线端点到文字起点的距离
            created[14].TextString = "锥度1：10"
            if drawing_type=="JZM_KC" or drawing_type=="GPMJX":
               
                ArrowPnt2 = APoint(geom["radius"],0)+geom["center"]
                BaselinePnt2 = ArrowPnt2 + APoint(10, -20)
                PntsArray2 = np.array([ArrowPnt2, BaselinePnt2])
                PntsArray2 = PntsArray2.reshape(1, PntsArray2.shape[0] * PntsArray2.shape[1])[0]
                created[15] = acad.model.AddMLeader(PntsArray2, 0)
                            # ArrowPnt 箭头位置；
                            # BaselinePnt 基线位置 ；
                            # 1 表示多重引线的索引号，为正整数。
                    # MLeaderObj.ArrowheadSize = 2  # 指箭头高度；此项将覆盖系统变量DIMASZ的值。
                created[15].DoglegLength = 8
                created[15].LandingGap = 3  # 基线端点到文字起点的距离
                created[15].TextString = "开槽"
                # --------下口径标注----------#（底座直径标注）
            created[4] = acad.model.AddDimRotated(B+APoint(0, -5), APoint(7, geom["y_M"]-5), APoint(0, geom["y_L"]-14), RotationAngle)
              
            created[4].Update()
            created[4].TextOverride = "Φ<>"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = 0.15
            created[4].ToleranceLowerLimit = -0.05
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
                           
        #-------对应右侧定位点D,圆弧中点到模子最低点的参考高度
        
            created[7] = acad.model.AddDimRotated(arc_center_point, D, DimLineLocation_D, math.radians(90))
            created[7].TextOverride = "(<>)"          
        #-------------凹模额外加一个总高标注------------#
        if geom["radius"] <0:
  
            created[8] = acad.model.AddDimRotated(geom["right_point"], D, DimLineLocation_D+APoint(5,0), math.radians(90))
            created[8].TextOverride = "(<>)"
       
        #---------圆弧半径标注----------#
        angle_rad = math.radians(80)
        point_x = geom["center"].x + geom["radius"] * math.cos(angle_rad)
        point_y = geom["center"].y + geom["radius"] * math.sin(angle_rad)
        ChordPoint = APoint(point_x, point_y)#ChordPoint - 弦点/圆弧上的点（标注的终点）,14 - 标注文字的位置偏移距离（14个单位）
        if geom["radius"] > 0:
            created[5] = acad.model.AddDimRadial(geom["center"], ChordPoint, 20)
        else:
            created[5] = acad.model.AddDimRadial(geom["center"], ChordPoint, 35)
           
           
        if geom["radius"] > 0:
            created[5].TextPosition = APoint(17, 17) + ChordPoint# 标注文字的位置（标注文字的中心位置）
        else:
            created[5].TextPosition = APoint(27, 27) + ChordPoint# 标注文字的位置（标注文字的中心位置）
        created[5].StyleName = "ZqStandard$4"# 设置标注样式
        created[5].Update()
        angle_rad2 = math.radians(135)
        point_x2 = geom["center2"].x + 4 * math.cos(angle_rad2)
        point_y2 = geom["center2"].y + 4 * math.sin(angle_rad2)
        ChordPoint2 = APoint(point_x2, point_y2)
        created[6] = acad.model.AddDimRadial(geom["center2"], ChordPoint2, 10)       
     
        created[6].TextPosition = APoint(7.5, -7.5) + ChordPoint2

    except Exception as error:
        # 总体异常不会中止流程，记录后返回已有对象
        print(f"dimension: 发生异常: {error}")

    return tuple(created)


if __name__ == "__main__":
    # 简单示例（仅在有 AutoCAD 的环境下有意义）
    try:
        date_name()
    except Exception:
        pass
