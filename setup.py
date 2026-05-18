#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCAD Lens Package - Setup Script
镜片AutoCAD绘图工具包 安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="autocad-lens-package",
    version="1.0.0",
    description="镜片AutoCAD绘图工具包 - AutoCAD Lens Drawing Toolkit",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AutoCAD Lens Package Contributors",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "pyautocad>=1.0.0",
    ],
    packages=find_packages(include=["lens_package", "lens_package.*"]),
    package_data={
        "lens_package": [
            "*.json",
            "icons/*.svg",
            "icons/*.ico",
            "icons/*.png",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "lens-draw=lens_package.draw_lens:main",
            "lens-gui=lens_package.lens_gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    keywords="autocad lens cad drawing",
)
