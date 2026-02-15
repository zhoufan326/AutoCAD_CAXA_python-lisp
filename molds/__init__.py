# Draw module initialization
from .geometry import calculate_geometry
from .drawing_operations import DrawingOperations
from .Tool_calculation import SwingMachineToolingCalculator
from .dimension import dia, dimension, date_name
"""整个模块用于处理绘图相关的功能，包括几何计算、文件命名生成以及绘图操作和工具计算。"""
__all__ = [
    'calculate_geometry',
    'DrawingOperations',
    'SwingMachineToolingCalculator',
    'dia',
    'dimension',
    'date_name'
]