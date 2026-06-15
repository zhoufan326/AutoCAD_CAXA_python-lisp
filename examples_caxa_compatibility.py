#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoCAD/CAXA 兼容性使用示例

只需三种用法：
1. 自动检测（推荐）
2. 明确指定
3. 环境变量配置
"""

from utils import get_cad, detect_cad, APoint


# ==================== 用法1: 自动检测 ====================
def example_auto_detect():
    """自动检测运行中的CAD应用 - 最简单"""
    print("\n=== 用法1: 自动检测 ===")
    
    running = detect_cad()
    if running:
        print(f"✓ 检测到 {running.upper()} 正在运行")
    else:
        print("✗ 未检测到CAD应用，将创建AutoCAD实例")
    
    # 自动选择已运行的应用或创建AutoCAD
    cad = get_cad()
    print(f"✓ 已连接到 {cad.app_type.upper()}")


# ==================== 用法2: 明确指定 ====================
def example_explicit():
    """明确指定使用哪个CAD"""
    print("\n=== 用法2: 明确指定 ===")
    
    # 使用AutoCAD
    try:
        cad = get_cad(app_type='autocad')
        print(f"✓ 已连接到 AutoCAD")
    except Exception as e:
        print(f"✗ AutoCAD 未运行: {e}")
    
    # 使用CAXA
    try:
        cad = get_cad(app_type='caxa')
        print(f"✓ 已连接到 CAXA")
    except Exception as e:
        print(f"✗ CAXA 未运行: {e}")


# ==================== 用法3: 环境变量 ====================
def example_environment():
    """通过环境变量指定CAD应用
    
    设置方法（运行脚本前）：
    
    Windows CMD:
        set PREFERRED_CAD=caxa
        python this_script.py
    
    Windows PowerShell:
        $env:PREFERRED_CAD = 'caxa'
        python this_script.py
    
    Linux/Mac:
        export PREFERRED_CAD=caxa
        python this_script.py
    """
    print("\n=== 用法3: 环境变量配置 ===")
    print(__doc__)


# ==================== 实际使用示例 ====================
def example_drawing():
    """实际绘图示例"""
    print("\n=== 实际绘图 ===")
    
    try:
        cad = get_cad()  # 自动检测或使用环境变量
        
        if not cad.model:
            print("✗ 未找到模型空间")
            return
        
        # 绘制矩形
        p1 = APoint(0, 0)
        p2 = APoint(100, 0)
        p3 = APoint(100, 50)
        p4 = APoint(0, 50)
        
        cad.model.AddLine(p1, p2)
        cad.model.AddLine(p2, p3)
        cad.model.AddLine(p3, p4)
        cad.model.AddLine(p4, p1)
        
        print("✓ 矩形绘制成功")
        
    except Exception as e:
        print(f"✗ 绘制失败: {e}")


# ==================== 项目中如何使用 ====================
def example_project_integration():
    """在项目中集成的建议方式"""
    print("\n=== 项目集成 ===")
    print("""
    在你的项目中，只需要改 2 个地方：
    
    1. 替换导入（工具函数）：
       from utils.com_interface import Autocad  # 旧
       from utils import get_cad              # 新
    
    2. 替换创建实例（工具函数）：
       cad = Autocad(create_if_not_exists=True)  # 旧
       cad = get_cad()                           # 新
    
    其他代码完全不变，自动支持AutoCAD和CAXA！
    
    可选：通过环境变量来选择默认应用
       set PREFERRED_CAD=caxa
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("AutoCAD/CAXA 兼容性使用示例")
    print("=" * 60)
    
    example_auto_detect()
    example_explicit()
    example_environment()
    example_project_integration()
    example_drawing()
    
    print("\n" + "=" * 60)

