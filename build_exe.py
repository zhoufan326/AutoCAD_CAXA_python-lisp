#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCAD Lens Package - EXE Build Script
使用 PyInstaller 将镜片绘图工具打包为独立的 Windows 可执行文件

使用方法:
    python build_exe.py

依赖:
    pip install pyinstaller

输出:
    dist/Lens/ 目录下的 Lens.exe 可执行文件
"""

import os
import sys
import shutil
import subprocess


def build_exe():
    """使用 PyInstaller 构建可执行文件"""
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "lens_package", "icons", "Lens.svg")
    
    # 检查 PyInstaller 是否可用
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("✗ 未安装 PyInstaller，请执行: pip install pyinstaller")
        sys.exit(1)
    
    # 清理旧的构建产物
    dist_dir = os.path.join(script_dir, "dist")
    build_dir = os.path.join(script_dir, "build")
    spec_file = os.path.join(script_dir, "lens_exe.spec")
    
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    # 使用 .spec 文件构建（会自动处理图标）
    if os.path.exists(spec_file):
        print("使用 lens_exe.spec 构建...")
        cmd = ["pyinstaller", spec_file, "--noconfirm", "--clean"]
    else:
        print("使用命令行参数构建...")
        # 主入口文件
        main_script = os.path.join(script_dir, "lens_package", "lens_gui.py")
        
        # 构建命令
        cmd = [
            "pyinstaller",
            "--name=Lens",
            "--onefile",           # 单文件模式
            "--windowed",          # 无控制台窗口（GUI 模式）
            "--noconfirm",
            "--clean",
            f"--add-data={os.path.join(script_dir, 'lens_package', 'lens_gui_data.json')};lens_package",
            f"--add-data={os.path.join(script_dir, 'lens_package', 'params_storage.json')};lens_package",
            f"--add-data={os.path.join(script_dir, 'lens_package', 'icons')};lens_package/icons",
            f"--hidden-import=pyautocad",
            f"--hidden-import=lens_package.draw_lens",
            f"--hidden-import=lens_package.utils",
            f"--hidden-import=lens_package.utils.layer",
            f"--hidden-import=lens_package.utils.hatch",
            f"--hidden-import=lens_package.utils.retry",
            f"--hidden-import=lens_package.utils.scale_select",
            f"--hidden-import=lens_package.utils.retry_decorator",
            main_script,
        ]
        
        # 添加图标（仅当有 .ico 文件时）
        ico_path = os.path.join(script_dir, "lens_package", "icons", "Lens.ico")
        if os.path.exists(ico_path):
            cmd.append(f"--icon={ico_path}")
            print(f"✓ 使用图标: {ico_path}")
        else:
            print("⚠ 未找到 Lens.ico 图标文件，将使用默认图标")
            print("  提示: 可将 Lens.svg 转换为 Lens.ico 后放入 icons/ 目录")
    
    # 执行构建
    print(f"\n开始构建...")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print(f"\n✓ 构建成功!")
        
        # 查找生成的可执行文件
        exe_path = os.path.join(dist_dir, "Lens", "Lens.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"  输出文件: {exe_path}")
            print(f"  文件大小: {size_mb:.1f} MB")
        else:
            onefile_exe = os.path.join(dist_dir, "Lens.exe")
            if os.path.exists(onefile_exe):
                size_mb = os.path.getsize(onefile_exe) / (1024 * 1024)
                print(f"  输出文件: {onefile_exe}")
                print(f"  文件大小: {size_mb:.1f} MB")
    else:
        print(f"\n✗ 构建失败 (返回码: {result.returncode})")
        sys.exit(1)


def convert_svg_to_ico():
    """尝试将 SVG 图标转换为 ICO 格式（需要 cairosvg 和 PIL）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(script_dir, "lens_package", "icons", "Lens.svg")
    ico_path = os.path.join(script_dir, "lens_package", "icons", "Lens.ico")
    
    if os.path.exists(ico_path):
        return True
    
    print("尝试将 Lens.svg 转换为 Lens.ico...")
    
    try:
        # 方法1: 使用 cairosvg + PIL
        from PIL import Image
        import cairosvg
        
        # SVG → PNG (内存)
        png_data = cairosvg.svg2png(url=svg_path, output_width=256, output_height=256)
        
        # PNG → ICO
        with open("_temp_lens_icon.png", "wb") as f:
            f.write(png_data)
        
        img = Image.open("_temp_lens_icon.png")
        img.save(ico_path, format="ICO", sizes=[(256, 256)])
        os.remove("_temp_lens_icon.png")
        
        print(f"✓ 图标已转换: {ico_path}")
        return True
        
    except ImportError:
        print("  ⚠ 需要安装 cairosvg 和 Pillow:")
        print("     pip install cairosvg Pillow")
        print("  或者手动将 Lens.svg 转换为 Lens.ico")
        return False
    except Exception as e:
        print(f"  ⚠ 图标转换失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  AutoCAD Lens Package - EXE 构建工具")
    print("=" * 60)
    print()
    
    convert_svg_to_ico()
    build_exe()
