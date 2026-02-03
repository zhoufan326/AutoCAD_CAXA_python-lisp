import os
import time
from pyautocad import Autocad
from .safe_acad_operation import safe_acad_operation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")
def initial_connection(self, acad=None, template_path=DEFAULT_TEMPLATE_PATH):
        """
        初始化 FixtureOperations 类
        
        参数:
            acad: AutoCAD 连接对象，如果为 None 则自动创建
        """
        if acad is None:
            self.acad = Autocad(create_if_not_exists=True)
            print("等待 AutoCAD 初始化...")
            time.sleep(1.5)
        else:
            self.acad = acad

        if template_path:
            template_path = os.path.normpath(template_path)
            if os.path.exists(template_path):
                print(f"使用模板: {template_path}")
                
                def load_template():
                    self.acad.app.Documents.Add(template_path)
                
                safe_acad_operation(load_template, "模板加载", max_retries=3, retry_delay=1.5)
                print("模板加载成功，等待文档准备就绪...")
                time.sleep(1.5)
        
