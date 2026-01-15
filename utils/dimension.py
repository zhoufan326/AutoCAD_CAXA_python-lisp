from pyautocad import Autocad, APoint
import math

# 该模块提供两个函数：date_name 和 dimension
# 目标：保持接口兼容（和原来调用方一致），同时做基础语法修复并封装常见 COM 访问

acad = Autocad(create_if_not_exists=True)


def _get_doc(acad_obj):
    """返回可用的文档对象（ActiveDocument 或 doc），否则 None。"""
    return getattr(acad_obj, 'ActiveDocument', None) or getattr(acad_obj, 'doc', None)


def _safe_set_text_style(acad_obj, style_name: str):
    doc = _get_doc(acad_obj)
    if doc is None:
        return False
    try:
        # 尝试设置 ActiveTextStyle
        doc.ActiveTextStyle = doc.TextStyles.Item(style_name)
        return True
    except Exception:
        # 有时候需要通过 ActiveDocument 访问或样式不存在，忽略错误
        try:
            if getattr(acad_obj, 'ActiveDocument', None) is not None:
                acad_obj.ActiveDocument.ActiveTextStyle = acad_obj.ActiveDocument.TextStyles.Item(style_name)
                return True
        except Exception:
            return False


def date_name(date1="2026/1/1", date2="2026/1/1", name="XJMJM/R10-Φ10"):
    """在图纸上添加两个日期文本和一个名称文本。

    返回创建的文本对象 (text1, text2, text3) 或 (None, None, None) 在失败时。
    """
    try:
        _safe_set_text_style(acad, "宋体")
    except Exception:
        pass

    created = [None, None, None]
    try:
        created[0] = acad.model.AddText(date1, APoint(91, 42), 2.5)
    except Exception:
        created[0] = None

    try:
        created[1] = acad.model.AddText(date2, APoint(10, -141), 2.5)
    except Exception:
        created[1] = None

    try:
        created[2] = acad.model.AddText(name, APoint(97, -113), 2.5)
    except Exception:
        created[2] = None

    return tuple(created)


def dimension(XLine1Point, XLine2Point, a=None, b=None, c=None, center=None, radius=None, center2=None):
    """创建一组标注对象并返回它们的元组。

    返回顺序与原实现相同：
    (dimRotObj, dimRotObjA, dimRotObjB, dimRotObjC, dimRotObj_down, dimRadObj1, dimRadObj2, dimRotObjD)
    不可用的对象以 None 填充。
    """
    # 尝试设置图纸样式（容错）
    try:
        _safe_set_text_style(acad, "ZqStandard")
    except Exception:
        pass

    created = [None] * 8

    try:
        DimLineLocation_up = XLine1Point + APoint(0, 5)
        RotationAngle = math.radians(0)

        A = APoint(XLine1Point.x, a)
        DimLineLocationA = XLine1Point + APoint(-7, 0)
        B = APoint(-9, b)
        DimLineLocationB = XLine1Point + APoint(-1, 0)
        C = APoint(-9, c)
        DimLineLocationC = C + APoint(-3, 0)
        arc_center_point = APoint(0, radius) + center
        D = APoint(center.x, c)

        if XLine2Point.x >= 9:
            DimLineLocationD = APoint(6, 0) + XLine2Point
        elif 0 < XLine2Point.x < 9:
            DimLineLocationD = APoint(15, 0)
        else:
            DimLineLocationD = APoint(0, 0)

        # 主标注
        try:
            created[0] = acad.model.AddDimRotated(XLine1Point, XLine2Point, DimLineLocation_up, RotationAngle)
            created[0].TextOverride = "Φ<>"
        except Exception:
            created[0] = None

        # 其它标注
        try:
            created[1] = acad.model.AddDimRotated(XLine1Point, A, DimLineLocationA, math.radians(90))
        except Exception:
            created[1] = None

        try:
            created[2] = acad.model.AddDimRotated(A, B, DimLineLocationB, math.radians(90))
        except Exception:
            created[2] = None

        try:
            created[3] = acad.model.AddDimRotated(C, B, DimLineLocationC, math.radians(90))
        except Exception:
            created[3] = None

        try:
            created[7] = acad.model.AddDimRotated(arc_center_point, D, DimLineLocationD, math.radians(90))
            created[7].TextOverride = "(<>)"
        except Exception:
            created[7] = None

        try:
            created[4] = acad.model.AddDimRotated(C, APoint(9, c), C + APoint(0, -8), RotationAngle)
            try:
                created[4].Update()
            except Exception:
                pass
        except Exception:
            created[4] = None

        try:
            angle_rad = math.radians(70)
            point_x = center.x + radius * math.cos(angle_rad)
            point_y = center.y + radius * math.sin(angle_rad)
            ChordPoint = APoint(point_x, point_y)
            created[5] = acad.model.AddDimRadial(center, ChordPoint, 14)
            try:
                created[5].StyleName = "ZqStandard$4"
                created[5].Update()
            except Exception:
                try:
                    created[5].Update()
                except Exception:
                    pass
        except Exception:
            created[5] = None

        try:
            angle_rad2 = math.radians(135)
            point_x2 = center2.x + 4 * math.cos(angle_rad2)
            point_y2 = center2.y + 4 * math.sin(angle_rad2)
            ChordPoint2 = APoint(point_x2, point_y2)
            created[6] = acad.model.AddDimRadial(center2, ChordPoint2, 7)
            try:
                created[6].TextPosition = APoint(5.5, -5.5) + ChordPoint2
            except Exception:
                pass
        except Exception:
            created[6] = None

    except Exception as e:
        # 总体异常不会中止流程，记录后返回已有对象
        print(f"dimension: 发生异常: {e}")

    return tuple(created)


if __name__ == "__main__":
    # 简单示例（仅在有 AutoCAD 的环境下有意义）
    try:
        date_name()
    except Exception:
        pass
