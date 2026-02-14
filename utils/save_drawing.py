# 标准库导入
import os
import time
import traceback
from typing import Optional, Any


class DrawingSaver:
    """AutoCAD图形保存工具类"""
    
    # DWG版本映射
    DWG_VERSIONS = {
        "AutoCAD 2010": 60,
        "AutoCAD 2013": 61,
        "AutoCAD 2018": 62,
        "AutoCAD 2021": 63
    }
    
    @staticmethod
    def _is_acad_busy_error(error: Exception) -> bool:
        """检查是否是AutoCAD繁忙或拒绝接收的错误
        
        参数:
            error: 异常对象
            
        返回:
            bool: 是否是繁忙错误
        """
        error_str = str(error)
        return any(keyword in error_str for keyword in ['-2147418111', '拒绝接收', '繁忙'])
    
    @staticmethod
    def _validate_acad_connection(acad: Any, verbose: bool = True) -> bool:
        """验证AutoCAD连接状态
        
        参数:
            acad: AutoCAD对象
            verbose: 是否打印错误信息
            
        返回:
            bool: 连接是否有效
        """
        if not acad or not hasattr(acad, 'doc') or not acad.doc:
            if verbose:
                print("错误: AutoCAD 连接未初始化")
            return False
            
        if not acad.doc.Name:
            if verbose:
                print("错误: AutoCAD 文档未打开")
            return False
            
        return True
    
    @staticmethod
    def _prepare_filepath(filename: str, save_directory: str) -> str:
        """准备文件路径，确保目录存在
        
        参数:
            filename: 文件名
            save_directory: 保存目录
            
        返回:
            str: 完整的文件路径
        """
        # 确保文件名以.dwg结尾
        if not filename.endswith('.dwg'):
            filename += '.dwg'
        
        # 创建保存目录
        os.makedirs(save_directory, exist_ok=True)
        
        # 生成完整文件路径
        filepath = os.path.join(save_directory, filename)
        os.makedirs(os.path.dirname(filepath) or save_directory, exist_ok=True)
        
        return filepath


def save_drawing(acad: Any, filename: str, save_directory: str = "./output", 
                max_retries: int = 5, retry_delay: float = 1.0,
                check_connection: bool = True, dwg_version: int = 60,
                verbose: bool = True) -> Optional[str]:
    """保存AutoCAD图形到指定目录
    
    参数:
        acad: AutoCAD对象
        filename: 文件名（可包含或不包含.dwg扩展名）
        save_directory: 保存目录（默认："./output"）
        max_retries: 保存失败时的最大重试次数（默认：5）
        retry_delay: 重试间隔时间（默认：1.0秒）
        check_connection: 是否检查AutoCAD连接状态（默认：True）
        dwg_version: 保存的DWG文件版本（默认：60，对应AutoCAD 2010）
        verbose: 是否打印详细信息（默认：True）
        
    返回:
        保存的文件路径（成功）或None（失败）
    """
    # 检查AutoCAD连接状态
    if check_connection and not DrawingSaver._validate_acad_connection(acad, verbose):
        return None
    
    # 准备文件路径
    filepath = DrawingSaver._prepare_filepath(filename, save_directory)
    
    # 尝试保存，如果AutoCAD繁忙则重试
    for retry_count in range(max_retries):
        try:
            acad.doc.SaveAs(filepath, dwg_version)
            if verbose:
                print(f"✓ 图形已保存: {filepath}")
            return filepath
        except Exception as error:
            # 检查是否是AutoCAD繁忙错误
            if DrawingSaver._is_acad_busy_error(error):
                if retry_count < max_retries - 1:
                    if verbose:
                        print(f"  AutoCAD繁忙，{retry_delay}秒后重试 ({retry_count + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                    continue
                else:
                    if verbose:
                        print(f"✗ 保存失败：AutoCAD持续繁忙（已尝试{max_retries}次）")
            else:
                if verbose:
                    print(f"✗ 保存失败: {error}")
                    traceback.print_exc()
            break
    
    return None


# 兼容类方法的包装函数 - 保持向后兼容
def save_drawing_from_instance(self: Any, save_directory: str = "./output", 
                             max_retries: int = 5, retry_delay: float = 1.0,
                             check_connection: bool = True, dwg_version: int = 60,
                             verbose: bool = True) -> Optional[str]:
    """从类实例调用的保存函数包装器
    
    参数:
        self: 包含acad和filename属性的类实例
        save_directory: 保存目录
        max_retries: 最大重试次数
        retry_delay: 重试间隔时间
        check_connection: 是否检查连接
        dwg_version: DWG文件版本
        verbose: 是否打印详细信息
        
    返回:
        保存的文件路径或None
    """
    # 验证实例属性
    if not hasattr(self, 'acad'):
        if verbose:
            print("错误: 实例没有acad属性")
        return None
    
    if not hasattr(self, 'filename'):
        if verbose:
            print("错误: 实例没有filename属性")
        return None
    
    # 调用核心保存函数
    return save_drawing(
        self.acad,
        self.filename,
        save_directory,
        max_retries,
        retry_delay,
        check_connection,
        dwg_version,
        verbose
    )
