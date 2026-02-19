# 标准库导入
import os
import time
import traceback
from typing import Optional, Any

# 导入重试装饰器
from .retry_decorator import safe_acad_retry


@safe_acad_retry(max_retries=5, delay=1.0, name="保存图形")
def save_drawing(acad: Any, filename: str, save_directory: str = "./output", 
                dwg_version: int = 60, verbose: bool = True) -> Optional[str]:
    """保存AutoCAD图形到指定目录
    
    参数:
        acad: AutoCAD对象
        filename: 文件名（可包含或不包含.dwg扩展名）
        save_directory: 保存目录（默认："./output"）
        dwg_version: 保存的DWG文件版本（默认：60，对应AutoCAD 2010）
        verbose: 是否打印详细信息（默认：True）
        
    返回:
        保存的文件路径（成功）或None（失败）
    """
    # 检查AutoCAD连接状态
    if not acad or not hasattr(acad, 'doc') or not acad.doc or not acad.doc.Name:
        if verbose:
            print("错误: AutoCAD 连接或文档未初始化")
        return None
    
    # 确保文件名以.dwg结尾
    if not filename.endswith('.dwg'):
        filename += '.dwg'
    
    # 创建保存目录
    os.makedirs(save_directory, exist_ok=True)
    filepath = os.path.join(save_directory, filename)
    
    try:
        # 尝试保存
        acad.doc.SaveAs(filepath, dwg_version)
        if verbose:
            print(f"✓ 图形已保存: {filepath}")
        return filepath
    except Exception as error:
        error_str = str(error)
        is_busy_error = any(keyword in error_str for keyword in ['-2147418111', '拒绝接收', '繁忙'])
        
        # 对于非繁忙错误，直接返回None并打印错误信息
        if not is_busy_error:
            if verbose:
                print(f"✗ 保存失败: {error}")
                traceback.print_exc()
            return None
        
        # 对于繁忙错误，抛出异常让装饰器处理重试
        raise


# 兼容类方法的包装函数 - 保持向后兼容（如果需要）
def save_drawing_from_instance(self: Any, save_directory: str = "./output", 
                             dwg_version: int = 60, verbose: bool = True) -> Optional[str]:
    """从类实例调用的保存函数包装器（兼容旧代码）
    
    参数:
        self: 包含acad和filename属性的类实例
        其他参数与save_drawing函数相同
        
    返回:
        保存的文件路径或None
    """
    if not hasattr(self, 'acad') or not hasattr(self, 'filename'):
        if verbose:
            print("错误: 实例缺少必要的acad或filename属性")
        return None
    
    return save_drawing(
        self.acad, self.filename, save_directory, dwg_version, verbose
    )
