#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoCAD 重试装饰器模块

本模块提供了一个装饰器函数，用于在 AutoCAD 操作失败时自动重试。
"""

import time
from functools import wraps
from typing import Callable, Any, Optional


def safe_acad_retry(
    max_retries: int = 5,
    delay: float = 1.5,
    name: str = "操作",
    should_retry: Optional[Callable[[Exception], bool]] = None
) -> Callable:
    """AutoCAD 安全重试装饰器

    参数:
        max_retries: 最大重试次数，默认 5
        delay: 重试延迟时间（秒），默认 1.5
        name: 操作名称，用于日志显示，默认 "操作"
        should_retry: 可选的回调函数，接收异常对象，返回 True 表示应重试，False 表示直接抛出。
                      默认 None 表示所有异常都重试。

    返回:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if should_retry and not should_retry(e):
                        raise
                    if attempt == max_retries:
                        raise RuntimeError(f"{name} 最终失败 ({max_retries}次尝试): {e}") from e
                    print(f"{name} 失败 (尝试 {attempt}/{max_retries})，{delay:.1f}s 后重试... {e}")
                    time.sleep(delay)
        return wrapper
    return decorator


# 导出公共接口
__all__ = [
    'safe_acad_retry'
]

# 模块版本信息
__version__ = '0.2.0'
__author__ = 'AutoCAD Python Project'

# 模块描述
__description__ = 'AutoCAD 重试装饰器模块'

# 导入时自动执行的初始化代码
def _init_module():
    """模块初始化函数"""
    print(f"重试装饰器模块已加载 (版本: {__version__})")

# 执行模块初始化
_init_module()