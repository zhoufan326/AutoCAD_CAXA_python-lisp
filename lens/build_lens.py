#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lens Drawing Tool - EXE Build Script
将 lens/ + utils/ 打包为独立可执行文件

使用方法:
    python build_lens.py

依赖:
    pip install pyinstaller

输出:
    dist/Lens_V{version}.exe
"""

import os
import sys
import shutil
import subprocess

PROJECT_VERSION = "0.2.1"


def build_exe():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    utils_dir = os.path.join(project_root, "utils")

    try:
        import PyInstaller
        print(f"[OK] PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("[ERR] 未安装 PyInstaller，请执行: pip install pyinstaller")
        sys.exit(1)

    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")
    spec_file = os.path.join(project_root, "lens_exe.spec")

    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)

    exe_name = f"Lens_V{PROJECT_VERSION}"

    if os.path.exists(spec_file):
        print("使用 lens_exe.spec 构建...")
        cmd = ["pyinstaller", spec_file, "--noconfirm", "--clean"]
    else:
        print("使用命令行参数构建...")
        main_script = os.path.join(script_dir, "lens_gui.py")

        cmd = [
            "pyinstaller",
            f"--name={exe_name}",
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--clean",
            f"--paths={script_dir}",
            f"--paths={project_root}",
            f"--add-data={os.path.join(script_dir, 'lens_gui_data.json')};lens",
            f"--add-data={os.path.join(script_dir, 'params_storage.json')};lens",
            f"--add-data={utils_dir};utils",
            f"--add-data={os.path.join(project_root, '新图样.dwt')};.",
            f"--hidden-import=utils",
            f"--hidden-import=pyautocad",
            main_script,
        ]

        ico_path = os.path.join(script_dir, "icons", "Lens.ico")
        if os.path.exists(ico_path):
            cmd.append(f"--icon={ico_path}")
            print(f"[OK] 使用图标: {ico_path}")
        else:
            print("[WARN] 未找到 Lens.ico 图标文件，将使用默认图标")

    print(f"\n开始构建 {exe_name}...")
    print(f"命令: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print(f"\n[OK] 构建成功!")

        onefile_exe = os.path.join(dist_dir, f"{exe_name}.exe")
        if os.path.exists(onefile_exe):
            size_mb = os.path.getsize(onefile_exe) / (1024 * 1024)
            print(f"  输出文件: {onefile_exe}")
            print(f"  文件大小: {size_mb:.1f} MB")
    else:
        print(f"\n[ERR] 构建失败 (返回码: {result.returncode})")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
