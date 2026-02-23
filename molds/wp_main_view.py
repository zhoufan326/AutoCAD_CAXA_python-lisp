# 标准库导入
import math
import os
import sys

# 添加项目根目录和当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 第三方库导入
from pyautocad import APoint

# 项目模块导入
from utils import CD,CL

def draw_main_view(acad, radius, center, chord):
    """绘制主视图
    
    Args:
        acad: AutoCAD对象
       
        radius: 半径
        center: 中心点
        chord: 弦长
    """
    
    center2 = center + APoint(4 * chord, 0)
    CD(acad, center2, 1.5/2, math.pi/12, 2)  # 中心小圆
    CD(acad, center2, chord/2, -math.pi/4, 5)  # 内圆
    x_offset = math.sqrt((chord/2) ** 2 - 0.25)  #开槽处的横坐标偏移
    if radius <= 0:
        chordN = chord + 1 if chord < 10 else chord + 2
        CD(acad, center2, chordN/2, math.pi/3, 5)  # 外圆
        x_offset = math.sqrt((chordN/2) ** 2 - 0.25)
            
    # 绘制水平线
    acad.model.AddLine(APoint(center2.x - x_offset, center2.y + 0.5), APoint(center2.x + x_offset, center2.y + 0.5))
    acad.model.AddLine(APoint(center2.x - x_offset, center2.y - 0.5), APoint(center2.x + x_offset, center2.y - 0.5))
    # 绘制中心线
    CL(acad, center2 + APoint(1.5*chord/2, 0), center2- APoint(1.5*chord/2, 0))
    CL(acad, center2 + APoint(0, 1.5*chord/2), center2- APoint(0, 1.5*chord/2))
    return center2