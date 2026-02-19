#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
标注模块

本模块提供 AutoCAD 标注相关的功能。
"""

from .dia import dia

# 导出公共接口
__all__ = [
    'dia'
]

# 模块版本信息
__version__ = '1.0.0'
__author__ = 'AutoCAD Python Project'

# 模块描述
__description__ = 'AutoCAD 标注功能模块'

# 导入时自动执行的初始化代码（可选）
def _init_module():
    """模块初始化函数"""
    print(f"标注模块已加载 (版本: {__version__})")

# 执行模块初始化
_init_module()