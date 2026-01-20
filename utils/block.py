import time
from pyautocad import APoint

def insert_block(acad, insertionPnt, block_name, max_retries=3, retry_delay=1.5):
    """插入图块到AutoCAD模型空间
    
    参数:
        acad: AutoCAD连接对象
        insertionPnt: 插入点坐标
        block_name: 图块文件路径
        max_retries: 最大重试次数
        retry_delay: 重试延迟时间（秒）
    """
    model = getattr(acad, 'model', None)
    if model is None:
        raise RuntimeError("未连接到 AutoCAD model")
    
    for attempt in range(1, max_retries + 1):
        try:
            RetVal = model.InsertBlock(insertionPnt, block_name, 1, 1, 1, 0)
            return RetVal
        except Exception as e:
            error_str = str(e)
            is_busy = ('-2147418111' in error_str or 
                       '拒绝接收' in error_str or 
                       '2147352567' in error_str or
                       '-2147418111' in error_str)
            
            if is_busy and attempt < max_retries:
                print(f"  插入图块繁忙，{attempt}/{max_retries}，{retry_delay:.1f}s 后重试...")
                time.sleep(retry_delay)
                retry_delay *= 1.2
                continue
            else:
                print(f"  插入图块失败: {e}")
                raise
    
    return None