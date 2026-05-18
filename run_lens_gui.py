"""
AutoCAD Lens Package - 入口文件（供 PyInstaller 使用）
绝对导入，避免 PyInstaller 打包时相对导入问题
"""
import sys
import os

# 确保包路径在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lens_package.lens_gui import main

if __name__ == "__main__":
    main()
