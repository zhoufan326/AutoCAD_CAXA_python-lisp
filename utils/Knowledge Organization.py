from pyautocad import Autocad, APoint, aDouble
import math
import numpy as np
import comtypes
import os
import time
from datetime import datetime

comtypes.npsupport.enable()
"""
AutoCAD操作方法知识库

本文件集中整理了AutoCAD的常用操作方法，包括：
1. CAD连接与基本操作
2. 绘图设置
3. 基本图形绘制
4. 标注方法
5. 辅助功能
"""

# ------------------------------
# 1. CAD连接与基本操作
# ------------------------------

def connect_to_autocad(create_if_not_exists=True):
    """连接到AutoCAD应用程序
    
    参数:
        create_if_not_exists: 如果AutoCAD未运行，是否创建新实例
    返回:
        AutoCAD对象
    """
    return Autocad(create_if_not_exists=create_if_not_exists)

def load_template(acad, template_path):
    """加载AutoCAD模板
    
    参数:
        acad: AutoCAD对象
        template_path: 模板文件路径
    """
    if template_path and os.path.exists(template_path):
        print(f"使用模板: {template_path}")
        for _ in range(3):
            try:
                acad.app.Documents.Add(template_path)
                time.sleep(1.5)
                break
            except Exception as e:
                if '繁忙' in str(e) or '2147418111' in str(e):
                    time.sleep(1.5)
                    continue

def save_drawing(acad, filename, save_directory="output"):
    """保存图形到指定目录
    
    参数:
        acad: AutoCAD对象
        filename: 文件名
        save_directory: 保存目录
    返回:
        文件路径或None（保存失败）
    """
    os.makedirs(save_directory, exist_ok=True)
    
    if not filename.endswith('.dwg'):
        filename += '.dwg'
    
    filepath = os.path.join(save_directory, filename)
    os.makedirs(os.path.dirname(filepath) or save_directory, exist_ok=True)
    
    # 尝试保存，如果AutoCAD繁忙则重试
    for _ in range(5):
        try:
            acad.doc.SaveAs(filepath, 60)
            print(f"保存成功: {filepath}")
            return filepath
        except Exception as error:
            error_str = str(error)
            if '-2147418111' in error_str or '拒绝接收' in error_str:
                time.sleep(1)
                continue
            else:
                break

def zoom_to_extents(acad):
    """缩放到图形范围
    
    参数:
        acad: AutoCAD对象
    """
    print("缩放到范围...")
    acad.doc.SendCommand("_.zoom _e ")
    time.sleep(1.0)  # 增加等待时间

def retry_operation(operation, operation_name, max_retries=3, retry_delay=1.0):
    """重试操作直到成功或达到最大重试次数
    
    参数:
        operation: 要执行的操作（lambda函数）
        operation_name: 操作名称（用于打印日志）
        max_retries: 最大重试次数
        retry_delay: 重试延迟时间（秒）
    返回:
        操作结果
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            print(f"✓ {operation_name}成功")
            return result
        except Exception as e:
            error_str = str(e)
            if '繁忙' in error_str or '-2147418111' in error_str:
                print(f"{operation_name}失败（AutoCAD繁忙），{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                continue
            else:
                print(f"{operation_name}失败: {e}")
                break
    return None

# ------------------------------
# 2. 绘图设置
# ------------------------------

def set_layer(acad, layer_name):
    """设置当前图层
    
    参数:
        acad: AutoCAD对象
        layer_name: 图层名称
    """
    acad.model.SetLayer(layer_name)

def _safe_set_text_style(acad_obj, style_name):
    """安全设置文本样式
    
    参数:
        acad_obj: AutoCAD对象
        style_name: 文本样式名称
    返回:
        是否设置成功
    """
    doc = _get_doc(acad_obj)
    if not doc:
        return False
    
    try:
        doc.ActiveTextStyle = doc.TextStyles.Item(style_name)
        return True
    except Exception:
        return False

def _get_doc(acad_obj):
    """获取AutoCAD文档对象
    
    参数:
        acad_obj: AutoCAD对象
    返回:
        文档对象或None
    """
    return getattr(acad_obj, 'ActiveDocument', None) or getattr(acad_obj, 'doc', None)

# ------------------------------
# 3. 基本图形绘制
# ------------------------------

def draw_line(acad, start_point, end_point):
    """绘制直线
    
    参数:
        acad: AutoCAD对象
        start_point: 起点（APoint对象）
        end_point: 终点（APoint对象）
    返回:
        直线对象
    """
    return acad.model.AddLine(start_point, end_point)

def draw_arc(acad, center, radius, start_angle, end_angle):
    """绘制圆弧
    
    参数:
        acad: AutoCAD对象
        center: 圆心（APoint对象）
        radius: 半径
        start_angle: 起始角度（弧度）
        end_angle: 结束角度（弧度）
    返回:
        圆弧对象
    """
    return acad.model.AddArc(center, radius, start_angle, end_angle)

def draw_circle(acad, center, radius):
    """绘制圆
    
    参数:
        acad: AutoCAD对象
        center: 圆心（APoint对象）
        radius: 半径
    返回:
        圆对象
    """
    return acad.model.AddCircle(center, radius)

def draw_polyline(acad, points):
    """绘制多段线
    
    参数:
        acad: AutoCAD对象
        points: 点列表（APoint对象列表）
    返回:
        多段线对象
    """
    pnts = [j for i in points for j in i]
    pnts = aDouble(pnts)
    return acad.model.AddPolyLine(pnts)

def draw_center_line(acad, x, y_start, y_end, line_type="CENTER2", color=1, linetype_scale=0.1):
    """绘制中心线
    
    参数:
        acad: AutoCAD对象
        x: x坐标
        y_start: 起始y坐标
        y_end: 结束y坐标
        line_type: 线型
        color: 颜色
        linetype_scale: 线型比例
    返回:
        中心线对象
    """
    center_line_start = APoint(x, y_start)
    center_line_end = APoint(x, y_end)
    center_line = acad.model.AddLine(center_line_start, center_line_end)
    center_line.Color = color
    
    try:
        center_line.Linetype = line_type
        center_line.LinetypeScale = linetype_scale
    except:
        try:
            center_line.Linetype = "CENTER"
            center_line.LinetypeScale = linetype_scale
        except:
            pass
    
    return center_line

# ------------------------------
# 4. 标注方法
# ------------------------------

def add_rotated_dimension(acad, extension_line_start, extension_line_end, dimension_line_location, rotation_angle):
    """添加旋转标注
    
    参数:
        acad: AutoCAD对象
        extension_line_start: 第一条尺寸界线的起点
        extension_line_end: 第二条尺寸界线的起点
        dimension_line_location: 尺寸线位置
        rotation_angle: 旋转角度（弧度）
    返回:
        标注对象
    """
    return acad.model.AddDimRotated(extension_line_start, extension_line_end, dimension_line_location, rotation_angle)

def add_radial_dimension(acad, center, chord_point, leader_length=14):
    """添加半径标注
    
    参数:
        acad: AutoCAD对象
        center: 圆心
        chord_point: 圆弧上的点
        leader_length: 引出线长度
    返回:
        标注对象
    """
    return acad.model.AddDimRadial(center, chord_point, leader_length)

def add_diametric_dimension(acad, chord_point, far_chord_point, leader_length=10):
    """添加直径标注
    
    参数:
        acad: AutoCAD对象
        chord_point: 第一个弦点
        far_chord_point: 第二个弦点
        leader_length: 引出线长度
    返回:
        标注对象
    """
    return acad.model.AddDimDiametric(chord_point, far_chord_point, leader_length)

def add_aligned_dimension(acad, extension_line_start, extension_line_end, dimension_line_location):
    """添加对齐标注
    
    参数:
        acad: AutoCAD对象
        extension_line_start: 第一条尺寸界线的起点
        extension_line_end: 第二条尺寸界线的起点
        dimension_line_location: 尺寸线位置
    返回:
        标注对象
    """
    return acad.model.AddDimAligned(extension_line_start, extension_line_end, dimension_line_location)

def add_multileader(acad, arrow_point, baseline_point, text_string="", dogleg_length=8, landing_gap=3):
    """添加多重引线标注
    
    参数:
        acad: AutoCAD对象
        arrow_point: 箭头位置
        baseline_point: 基线位置
        text_string: 文本内容
        dogleg_length: 折线长度
        landing_gap: 基线端点到文字起点的距离
    返回:
        多重引线对象
    """
    # 准备点数组
    PntsArray = np.array([arrow_point, baseline_point])
    PntsArray = PntsArray.reshape(1, PntsArray.shape[0] * PntsArray.shape[1])[0]
    
    # 创建多重引线
    mleader = acad.model.AddMLeader(PntsArray, 0)
    mleader.DoglegLength = dogleg_length
    mleader.LandingGap = landing_gap
    mleader.TextString = text_string
    
    return mleader

def date_name(acad, name="XJMJM/R10-Φ10", date_format="%Y/%m/%d"):
    """在图纸上添加日期和名称文本
    
    参数:
        acad: AutoCAD对象
        name: 名称文本
        date_format: 日期格式
    返回:
        创建的文本对象元组
    """
    point1 = APoint(70, 81)  # 上日期位置
    point2 = APoint(-10, -102)  # 下日期位置
    point3 = APoint(101, -75)  # 名称位置
    current_date = datetime.now().strftime(date_format)
    
    # 尝试设置文本样式
    try:
        _safe_set_text_style(acad, "宋体")
    except Exception:
        pass
    
    created = [None, None, None]
    
    # 创建文本对象
    try:
        created[0] = acad.model.AddText(current_date, point1, 2.5)
    except Exception:
        created[0] = None
    
    try:
        created[1] = acad.model.AddText(current_date, point2, 2.5)
    except Exception:
        created[1] = None
    
    try:
        created[2] = acad.model.AddText(name, point3, 2.5)
        created[2].Alignment = 2  # 居中对齐
        created[2].TextAlignmentPoint = point3
        created[2].Update()
    except Exception:
        created[2] = None
    
    return tuple(created)

def create_dimension(acad, geom, drawing_type="XJMJM"):
    """创建完整的图形标注
    
    参数:
        acad: AutoCAD对象
        geom: 包含标注几何信息的字典
        drawing_type: 图纸类型
    返回:
        创建的标注对象元组
    """
    # 尝试设置文本样式
    try:
        _safe_set_text_style(acad, "ZqStandard")
    except Exception:
        pass
    
    created = [None] * 18  # 18个标注对象
    
    try:
        # 提取几何参数
        y_U = geom["y_U"]
        y_M = geom["y_M"]
        y_L = geom["y_L"]
        radius = geom["radius"]
        center = geom["center"]
        left_point = geom["left_point"]
        right_point = geom["right_point"]
        b = geom["b"]
        a = geom["a"]
        
        # 可选参数
        left_pointN = geom.get("left_pointN")
        right_pointN = geom.get("right_pointN")
        center2 = geom.get("center2")
        
        RotationAngle = math.radians(0)  # 默认旋转角为0
        
        # 计算标注用到的点坐标
        A = APoint(-5, y_U)
        Ar = APoint(5, y_U)
        
        if drawing_type == "XJMJM" or drawing_type == "XPMJM":
            B = APoint(-9, y_M)
            C = APoint(-9, y_L)
            Cr = APoint(9, y_L)
        else:
            B = APoint(-7, y_M)
            C = APoint(-5, y_L)
        
        D = APoint(center.x, y_L)
        arc_center_point = APoint(0, radius) + center  # 上圆弧的中心点
        
        # 计算标注线的定位点
        if radius <= 0:
            DimLineLocation_up = left_point + APoint(0, 1.5)
            DimLineLocation_up2 = left_point + APoint(0, 6)
        else:
            DimLineLocation_up = center + APoint(0, radius + 1.5)
        
        # 右侧定位点
        if right_point.x >= 9:
            DimLineLocation_D = APoint(6, 0) + right_point
        elif 0 < right_point.x < 9:
            DimLineLocation_D = APoint(15, 0)
        
        # 上口径标注
        created[0] = add_rotated_dimension(acad, left_point, right_point, DimLineLocation_up, RotationAngle)
        created[0].TextOverride = "Φ<>'"
        
        if radius <= 0:
            # 使用半标注
            created[0].StyleName = "ZqStandard$0"
            # 添加外口径标注
            L_point = left_pointN
            R_point = right_pointN
            created[9] = add_rotated_dimension(acad, L_point, R_point, DimLineLocation_up2, RotationAngle)
            created[9].TextOverride = "Φ<>'"
        
        # 连接轴直径标注
        if not b == 0:
            DimLineLocation_A = A + APoint(0, -4)
            created[10] = add_rotated_dimension(acad, Ar, A, DimLineLocation_A, RotationAngle)
            created[10].TextOverride = "Φ<>'"
        
        # 纵向线段标注
        DimLineLocation_thick = left_point + APoint(-8, 0)
        created[1] = add_rotated_dimension(acad, left_point, left_point - APoint(0, a), DimLineLocation_thick, math.radians(90))
        
        if drawing_type == "XJMJM" or drawing_type == "XPMJM":
            DimLineLocation_B = B + APoint(-1, 0)
            DimLineLocation_C = C + APoint(-3, 0)
            DimLineLocation_Cr = Cr + APoint(0, -7)
            
            created[2] = add_rotated_dimension(acad, A, B, DimLineLocation_B, math.radians(90))
            created[3] = add_rotated_dimension(acad, C, B, DimLineLocation_C, math.radians(90))
            
            # 下口径标注（底座直径标注）
            created[4] = add_rotated_dimension(acad, Cr, C, DimLineLocation_Cr, 0)
            created[4].TextOverride = "Φ<>'"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = -0.02
            created[4].ToleranceLowerLimit = 0.04
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
            created[4].Update()
        else:
            DimLineLocation_C = C + APoint(-9, 0)
            DimLineLocation_C2 = C + APoint(-13, 0)
            
            created[3] = add_rotated_dimension(acad, B + APoint(0, -5), B, DimLineLocation_C, math.radians(90))
            created[13] = add_rotated_dimension(acad, B + APoint(0, -5), C, DimLineLocation_C2, math.radians(90))
            
            # 插入锥度多段线
            ArrowPnt = APoint(6, (y_L + y_M) / 2)
            BaselinePnt = APoint(10, (y_L + y_M) / 2 - 5)
            created[14] = add_multileader(acad, ArrowPnt, BaselinePnt, "锥度1：10", 8, 3)
            
            # 插入开槽多段线
            if drawing_type == "JZM_KC" or drawing_type == "GPMJX":
                ArrowPnt2 = APoint(0, radius) + center
                BaselinePnt2 = ArrowPnt2 + APoint(25, 15)  # 调整文字位置到右侧
                created[15] = add_multileader(acad, ArrowPnt2, BaselinePnt2, "开槽", 8, 3)
            
            # 底座直径标注
            created[4] = add_rotated_dimension(acad, B + APoint(0, -5), APoint(7, y_M - 5), APoint(0, y_L - 14), RotationAngle)
            created[4].Update()
            created[4].TextOverride = "Φ<>'"
            created[4].ToleranceDisplay = 2
            created[4].ToleranceUpperLimit = 0.15
            created[4].ToleranceLowerLimit = -0.05
            created[4].TolerancePrecision = 3
            created[4].ToleranceHeightScale = 0.7
        
        # 圆弧中点到底座最低端参考高度
        if right_point.x >= 9 or (0 < right_point.x < 9):
            created[7] = add_rotated_dimension(acad, arc_center_point, D, DimLineLocation_D, math.radians(90))
            created[7].TextOverride = "(<>)'"
        
        # 凹模额外加一个总高标注
        if radius < 0:
            if right_point.x >= 9 or (0 < right_point.x < 9):
                created[8] = add_rotated_dimension(acad, right_point, D, DimLineLocation_D + APoint(5, 0), math.radians(90))
                created[8].TextOverride = "(<>)'"
        
        # 圆弧半径标注
        angle_rad = math.radians(80)
        point_x = center.x + radius * math.cos(angle_rad)
        point_y = center.y + radius * math.sin(angle_rad)
        ChordPoint = APoint(point_x, point_y)
        
        if radius > 0:
            created[5] = add_radial_dimension(acad, center, ChordPoint, 20)
        else:
            created[5] = add_radial_dimension(acad, center, ChordPoint, 35)
        
        if radius > 0:
            created[5].TextPosition = APoint(17, 17) + ChordPoint
        else:
            created[5].TextPosition = APoint(27, 27) + ChordPoint
        
        created[5].StyleName = "ZqStandard$4"
        created[5].Update()
        
        # 中心小圆弧半径标注
        if center2:
            angle_rad2 = math.radians(135)
            point_x2 = center2.x + 4 * math.cos(angle_rad2)
            point_y2 = center2.y + 4 * math.sin(angle_rad2)
            ChordPoint2 = APoint(point_x2, point_y2)
            created[6] = add_radial_dimension(acad, center2, ChordPoint2, 10)
            created[6].TextPosition = APoint(7.5, -7.5) + ChordPoint2
            
    except Exception as error:
        print(f"创建标注时发生异常: {error}")
    
    return tuple(created)

# ------------------------------
# 5. 辅助功能
# ------------------------------

def print_to_pdf(acad, pdf_path):
    """将DWG文件打印为PDF
    
    参数:
        acad: AutoCAD对象
        pdf_path: PDF输出路径
    返回:
        是否打印成功
    """
    if not getattr(acad, 'doc', None):
        print("错误: 未找到 AutoCAD 文档")
        return False
    
    try:
        # 创建打印配置
        plot_config = acad.doc.PlotConfigurations.Add(f"PDF_Plot_{os.path.basename(pdf_path)}", "Model")
        
        # 设置打印配置
        plot_config.ConfigName = "DWG to PDF.pc3"
        plot_config.PaperSize = "A4"
        plot_config.UseStandardScale = True
        plot_config.StandardScale = 1
        plot_config.PlotType = 3
        plot_config.PlotToFile = True
        plot_config.PlotFile = pdf_path
        plot_config.CenterPlot = True
        plot_config.PlotRotation = 0
        
        # 执行打印
        retry_operation(
            lambda: acad.doc.Plot.PlotToDevice(plot_config.ConfigName, plot_config.Name),
            "执行打印"
        )
        
        # 删除临时打印配置
        plot_config.Delete()
        print(f"✓ PDF 文件已创建: {pdf_path}")
        return True
        
    except Exception as e:
        print(f"错误: 打印为PDF失败 - {e}")
        return False

def create_hatch(acad, internal_x=-3, internal_y=None, hatch_style=0):
    """创建剖面线
    
    参数:
        acad: AutoCAD对象
        internal_x: 内部点x坐标
        internal_y: 内部点y坐标
        hatch_style: 剖面线样式
    返回:
        剖面线对象
    """
    # 这里需要根据实际情况实现剖面线创建逻辑
    # 当前仅为占位符
    print(f"创建剖面线，内部点: ({internal_x}, {internal_y})")
    # 实际实现需要使用 acad.model.AddHatch 方法
    return None

# ------------------------------
# 示例用法
# ------------------------------

if __name__ == "__main__":
    """示例用法"""
    try:
        # 连接到AutoCAD
        acad = connect_to_autocad()
        
        # 绘制一个简单的矩形
        print("绘制矩形...")
        p1 = APoint(0, 0)
        p2 = APoint(100, 0)
        p3 = APoint(100, 50)
        p4 = APoint(0, 50)
        
        # 设置图层
        set_layer(acad, "轮廓线")
        
        # 绘制矩形四条边
        draw_line(acad, p1, p2)
        draw_line(acad, p2, p3)
        draw_line(acad, p3, p4)
        draw_line(acad, p4, p1)
        
        # 绘制中心线
        set_layer(acad, "中心线")
        draw_center_line(acad, 50, -10, 60)
        
        # 添加标注
        set_layer(acad, "标注线")
        dim = add_rotated_dimension(acad, p1, p2, APoint(50, -5), 0)
        dim.TextOverride = "100"
        
        # 缩放到范围
        zoom_to_extents(acad)
        
        print("示例绘制完成！")
        
    except Exception as e:
        print(f"示例运行失败: {e}")