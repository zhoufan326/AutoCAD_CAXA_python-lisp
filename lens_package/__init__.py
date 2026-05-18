"""
AutoCAD Lens Drawing Package
=============================
镜片AutoCAD绘图工具包 - 用于在AutoCAD中绘制镜片图形

本包提供完整的镜片参数输入GUI和AutoCAD绘图功能，
支持多镜片绘制、参数同步、公差标注等特性。
"""

__version__ = "1.0.0"
__author__ = "AutoCAD Lens Package Contributors"
__description__ = "AutoCAD Lens Drawing Toolkit - 镜片AutoCAD绘图工具包"

from . import draw_lens
from . import lens_gui

# 方便顶层导入
from .draw_lens import DrawLens, draw_multiple_lenses
from .lens_gui import LensParamsGUI, main as gui_main

__all__ = [
    'DrawLens',
    'draw_multiple_lenses',
    'LensParamsGUI',
    'gui_main',
    'draw_lens',
    'lens_gui',
]
