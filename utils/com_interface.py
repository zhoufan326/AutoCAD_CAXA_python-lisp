#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoCAD COM接口直接包装
直接使用win32com.client替代pyautocad库
"""

import win32com.client
from win32com.client import constants
import pythoncom
import time


class APoint(tuple):
    """坐标点类 - 直接使用COM接口
    
    用法示例:
        p = APoint(10, 20)
        p.x  # 10
        p.y  # 20
        p + APoint(5, 5)  # APoint(15, 25)
    """
    
    def __new__(cls, x, y, z=0.0):
        """创建点坐标对象
        
        Args:
            x: X坐标
            y: Y坐标
            z: Z坐标，默认0
        """
        return super(APoint, cls).__new__(cls, (float(x), float(y), float(z)))
    
    @property
    def x(self):
        """X坐标"""
        return self[0]
    
    @property
    def y(self):
        """Y坐标"""
        return self[1]
    
    @property
    def z(self):
        """Z坐标"""
        return self[2]
    
    def __add__(self, other):
        """向量加法"""
        if isinstance(other, (tuple, list)) and len(other) >= 2:
            z = self.z + (other[2] if len(other) > 2 else 0)
            return APoint(self.x + other[0], self.y + other[1], z)
        return NotImplemented
    
    def __sub__(self, other):
        """向量减法"""
        if isinstance(other, (tuple, list)) and len(other) >= 2:
            z = self.z - (other[2] if len(other) > 2 else 0)
            return APoint(self.x - other[0], self.y - other[1], z)
        return NotImplemented
    
    def __repr__(self):
        if self.z != 0:
            return f"APoint({self.x}, {self.y}, {self.z})"
        return f"APoint({self.x}, {self.y})"


def aDouble(points):
    """将点列表转换为COM兼容的VT_R8数组
    
    Args:
        points: APoint列表或扁平坐标列表 [x1,y1,x2,y2,...]
        
    Returns:
        win32com兼容的数组对象
        
    例子:
        pnts = [APoint(0,0), APoint(10,0), APoint(10,10)]
        coords = aDouble(pnts)
        
        或者:
        coords = aDouble([0,0, 10,0, 10,10])
    """
    if isinstance(points, (list, tuple)):
        # 展开APoint对象为扁平列表
        flat_list = []
        for p in points:
            if isinstance(p, APoint):
                flat_list.extend([p.x, p.y])
            elif isinstance(p, (tuple, list)):
                flat_list.extend(p[:2])
            else:
                flat_list.append(float(p))
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, tuple(flat_list))
    return points


def vt_point(point):
    """将点坐标转换为COM兼容的VARIANT数组（VT_ARRAY | VT_R8）
    
    AutoCAD COM API 要求点参数以 SAFEARRAY of doubles 格式传递，
    部分方法（如 AddArc）不能直接接受 tuple/APoint，需要用此函数包装。
    
    Args:
        point: APoint 或 (x, y) / (x, y, z) 格式的点
        
    Returns:
        可用于COM调用的 VARIANT 对象
    """
    x = float(point[0])
    y = float(point[1])
    z = float(point[2]) if len(point) > 2 else 0.0
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))


class Autocad:
    """CAD COM接口包装类
    
    直接使用win32com.client连接到AutoCAD或CAXA应用
    
    支持的应用类型：
        - 'autocad': AutoCAD应用
        - 'caxa': CAXA应用（国产CAD）
    """
    
    # COM应用对象映射表
    APP_CLASSES = {
        'autocad': 'AutoCAD.Application',
        'caxa': 'CAXA.Application',
    }
    
    def __init__(self, create_if_not_exists=True, app_type='autocad'):
        """初始化CAD连接
        
        Args:
            create_if_not_exists: 如果应用未运行，是否创建新实例
            app_type: 应用类型，'autocad' 或 'caxa'，默认 'autocad'
        """
        self.create_if_not_exists = create_if_not_exists
        self.app_type = app_type.lower()
        self.app = None
        self.doc = None
        self.model = None
        self._connect()
    
    def _connect(self):
        """连接到CAD COM对象"""
        if self.app_type not in self.APP_CLASSES:
            raise ValueError(f"不支持的应用类型: {self.app_type}。支持的类型: {', '.join(self.APP_CLASSES.keys())}")
        
        app_class = self.APP_CLASSES[self.app_type]
        
        try:
            # 尝试连接到已运行的实例
            self.app = win32com.client.GetObject(class_=app_class)
        except:
            if self.create_if_not_exists:
                # 创建新的应用实例
                try:
                    self.app = win32com.client.Dispatch(app_class)
                    self.app.Visible = True
                except Exception as e:
                    raise RuntimeError(f"无法连接或创建{self.app_type.upper()}实例: {e}")
            else:
                raise RuntimeError(f"{self.app_type.upper()}未运行，且create_if_not_exists=False")
        
        # 获取当前文档（处理不同应用的差异）
        try:
            if self.app_type == 'autocad':
                if self.app.Documents.Count > 0:
                    self.doc = self.app.ActiveDocument
                    self.model = self.doc.ModelSpace
            elif self.app_type == 'caxa':
                # CAXA的文档获取方式可能不同
                if hasattr(self.app, 'ActiveDocument'):
                    self.doc = self.app.ActiveDocument
                    if hasattr(self.doc, 'ModelSpace'):
                        self.model = self.doc.ModelSpace
                elif hasattr(self.app, 'Documents') and self.app.Documents.Count > 0:
                    self.doc = self.app.Documents(1)  # CAXA使用1-based索引
                    if hasattr(self.doc, 'ModelSpace'):
                        self.model = self.doc.ModelSpace
        except:
            self.doc = None
            self.model = None
    
    def open_document(self, path):
        """打开AutoCAD文档
        
        Args:
            path: 文档路径
            
        Returns:
            打开的文档对象
        """
        try:
            self.doc = self.app.Documents.Open(path)
            self.model = self.doc.ModelSpace
            return self.doc
        except Exception as e:
            raise RuntimeError(f"无法打开文档 {path}: {e}")
    
    def new_document(self, template=None):
        """创建新文档
        
        Args:
            template: 模板路径（可选）
            
        Returns:
            创建的文档对象
        """
        try:
            if template:
                self.doc = self.app.Documents.Add(template)
            else:
                self.doc = self.app.Documents.Add()
            self.model = self.doc.ModelSpace
            return self.doc
        except Exception as e:
            raise RuntimeError(f"无法创建新文档: {e}")
    
    def save(self):
        """保存当前文档"""
        if self.doc:
            self.doc.Save()
        else:
            raise RuntimeError("没有打开的文档")
    
    def close(self):
        """关闭当前文档"""
        if self.doc:
            self.doc.Close(False)
            self.doc = None
            self.model = None
    
    def prompt(self, message):
        """在命令行显示消息"""
        if self.app:
            self.app.StatusBar.DisplayString = message
    
    @property
    def drawing(self):
        """别名：获取当前文档"""
        return self.doc
    
    def send_command(self, command):
        """发送命令到AutoCAD
        
        Args:
            command: 命令字符串
        """
        if self.doc:
            self.doc.SendCommand(command + "\n")
        else:
            raise RuntimeError("没有打开的文档")

    # ── 便捷绘图方法（自动处理点坐标转换）──

    def _p(self, pt):
        """将点转为COM兼容格式"""
        return vt_point(pt)

    def _pts(self, points):
        """将点列表转为aDouble格式"""
        return aDouble(points)

    def AddLine(self, pt1, pt2):
        return self.model.AddLine(self._p(pt1), self._p(pt2))

    def AddArc(self, center, radius, start_angle, end_angle):
        return self.model.AddArc(self._p(center), radius, start_angle, end_angle)

    def AddCircle(self, center, radius):
        return self.model.AddCircle(self._p(center), radius)

    def AddText(self, text, pt, height):
        return self.model.AddText(text, self._p(pt), height)

    def AddPolyLine(self, points):
        return self.model.AddPolyLine(self._pts(points))

    def AddDimRotated(self, pt1, pt2, dim_line_loc, angle):
        return self.model.AddDimRotated(self._p(pt1), self._p(pt2), self._p(dim_line_loc), angle)

    def AddDimRadial(self, center, chord_point, leader_length):
        return self.model.AddDimRadial(self._p(center), self._p(chord_point), leader_length)


# 为了兼容现有代码，提供常用的常量别名
try:
    AcViewport = constants.acViewport
    AcModelSpace = constants.acModelSpace
    AcPaperSpace = constants.acPaperSpace
except:
    # 如果constants不可用，提供默认值
    AcViewport = 0
    AcModelSpace = 1
    AcPaperSpace = 2


# ==================== 使用示例 ====================

# 示例1: 连接到AutoCAD (默认)
# ------
# acad = Autocad(create_if_not_exists=True)  # 默认是AutoCAD
# 或者显式指定:
# acad = Autocad(create_if_not_exists=True, app_type='autocad')
# 
# point = APoint(10, 20)
# line = acad.model.AddLine(point, APoint(100, 100))


# 示例2: 连接到CAXA (国产CAD)
# ------
# caxa = Autocad(create_if_not_exists=True, app_type='caxa')
# 
# # CAXA使用相同的接口
# point = APoint(10, 20)
# line = caxa.model.AddLine(point, APoint(100, 100))
# caxa.save()


# 示例3: 创建可兼容多CAD的工具函数
# ------
# def create_cad_instance(cad_type='autocad'):
#     """工厂函数 - 创建CAD实例"""
#     return Autocad(create_if_not_exists=True, app_type=cad_type)
# 
# # 使用环境变量或配置来决定使用哪个CAD
# import os
# preferred_cad = os.getenv('PREFERRED_CAD', 'autocad')
# cad = create_cad_instance(preferred_cad)

