import os
from typing import Optional, Any

from .retry_decorator import safe_acad_retry

# DWG 文件版本常量（AcSaveAsType 枚举值）
# 60 对应 AutoCAD 2013（DWG 内部版本 AC1027）
# 64 对应 AutoCAD 2018（DWG 内部版本 AC1032）
DWG_VERSION_ACAD_2013 = 60
DWG_VERSION_ACAD_2018 = 64


def _is_busy_error(error: Exception) -> bool:
    """判断异常是否为 AutoCAD 繁忙错误（可重试）"""
    error_str = str(error)
    return any(keyword in error_str for keyword in ['-2147418111', '拒绝接收', '繁忙'])


@safe_acad_retry(max_retries=5, delay=1.0, name="保存图形", should_retry=_is_busy_error)
def save_drawing(acad: Any, filename: str, save_directory: str = "./output",
                dwg_version: int = DWG_VERSION_ACAD_2013, verbose: bool = True) -> Optional[str]:
    """保存AutoCAD图形到指定目录

    参数:
        acad: AutoCAD对象
        filename: 文件名（可包含或不包含.dwg扩展名）
        save_directory: 保存目录（默认："./output"）
        dwg_version: 保存的DWG文件版本（默认：60，对应AutoCAD 2013）
        verbose: 是否打印详细信息（默认：True）

    返回:
        保存的文件路径（成功）或None（失败）
    """
    if not acad or not hasattr(acad, 'doc') or not acad.doc or not acad.doc.Name:
        if verbose:
            print("错误: AutoCAD 连接或文档未初始化")
        return None

    if not filename.endswith('.dwg'):
        filename += '.dwg'

    os.makedirs(save_directory, exist_ok=True)
    filepath = os.path.join(save_directory, filename)

    acad.doc.SaveAs(filepath, dwg_version)
    if verbose:
        print(f"图形已保存: {filepath}")
    return filepath


__version__ = "0.2.0"
