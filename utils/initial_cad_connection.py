from utils.com_interface import Autocad
import time
from .retry_decorator import safe_acad_retry

@safe_acad_retry(max_retries=5, delay=1.0, name="初始化AutoCAD实例")
def _initialize_acad():
    """初始化并验证AutoCAD实例"""
    acad = Autocad(create_if_not_exists=True)
    time.sleep(0.5)  # 增加初始化延迟  
    return acad
