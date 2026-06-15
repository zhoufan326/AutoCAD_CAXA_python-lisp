#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAD应用工厂 - 支持AutoCAD和CAXA
"""

import os
import win32com.client
from .com_interface import Autocad


def get_cad(app_type=None, create_if_not_exists=True):
    """获取CAD实例（唯一推荐的方法）
    
    Args:
        app_type: 应用类型 ('autocad', 'caxa')
                  如果为None，自动检测运行中的应用，
                  都不运行则使用PREFERRED_CAD环境变量或默认'autocad'
        create_if_not_exists: 应用未运行时是否创建新实例
        
    Returns:
        Autocad: CAD实例
        
    Examples:
        # 自动检测（推荐）
        cad = get_cad()
        
        # 明确指定应用
        cad = get_cad(app_type='caxa')
        cad = get_cad(app_type='autocad')
    """
    if app_type is None:
        # 尝试检测已运行的应用
        if _is_running('AutoCAD.Application'):
            app_type = 'autocad'
        elif _is_running('CAXA.Application'):
            app_type = 'caxa'
        else:
            # 使用环境变量或默认值
            app_type = os.getenv('PREFERRED_CAD', 'autocad').lower()
    
    return Autocad(create_if_not_exists=create_if_not_exists, app_type=app_type)


def _is_running(com_class):
    """检查COM应用是否运行"""
    try:
        win32com.client.GetObject(class_=com_class)
        return True
    except:
        return False


def detect_cad():
    """检测当前运行的CAD应用
    
    Returns:
        str: 'autocad' 或 'caxa' 或 None
    """
    if _is_running('AutoCAD.Application'):
        return 'autocad'
    elif _is_running('CAXA.Application'):
        return 'caxa'
    return None

