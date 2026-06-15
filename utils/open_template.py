import time
import os
from utils.com_interface import Autocad, APoint
from .retry_decorator import safe_acad_retry
@safe_acad_retry(3, 1.0, "打开模板")
def _open_template(path: str):
    """打开 AutoCAD 模板"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"模板文件不存在: {path}")
    
    # 创建AutoCAD实例
    acad = Autocad(create_if_not_exists=True)
    time.sleep(0.5)
    acad.app.Documents.Add(path)
  
  