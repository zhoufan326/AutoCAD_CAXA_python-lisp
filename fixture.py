
import math
import os
import time
from typing import Optional
from pyautocad import APoint, aDouble, Autocad
from utils import set_layer, create_hatch, insert_block, date_name
from fixture_pom import draw_pom
from pom import POM
from fixture_cu import draw_cu, draw_port
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")

def safe_acad_operation(operation, operation_name="AutoCAD操作", max_retries=3, retry_delay=1.5, backoff=1.5):
    """执行 AutoCAD 操作并在遇到繁忙/拒绝错误时重试。

    参数:
        operation: 要执行的可调用对象
        operation_name: 日志中显示的操作名称
        max_retries: 最多尝试次数（至少1）
        retry_delay: 首次重试延迟（秒）
        backoff: 每次重试时延迟的乘数

    返回:
        operation() 的返回值，或在失败时抛出最后一次异常。
    """
    if max_retries < 1:
        max_retries = 1

    busy_indicators = ("-2147418111", "拒绝接收", "繁忙", "2147352567")
    delay = float(retry_delay)
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exc = e
            msg = str(e)
            is_busy = any(ind in msg for ind in busy_indicators)

            if is_busy and attempt < max_retries:
                print(f"  {operation_name} 繁忙，{attempt}/{max_retries}，{delay:.1f}s 后重试...")
                time.sleep(delay)
                delay *= backoff
                continue

            print(f"  {operation_name} 失败: {e}")
            raise

    # 如果循环结束（不太可能），抛出最后的异常
    raise last_exc

class FixtureOperations:
      # ==================== 创建 AutoCAD 连接 ====================
    def __init__(self, acad=None, template_path=DEFAULT_TEMPLATE_PATH):
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
        self.set_layer=set_layer  
        self.draw_pom=draw_pom
        self.draw_cu=draw_cu
        self.draw_port=draw_port



    def save_drawing(self, parameter, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
        if not self.acad or not self.acad.doc:
            print("错误: AutoCAD 文档未初始化")
            return None
        
        if not self.acad.doc.Name:
            print("错误: AutoCAD 文档未打开")
            return None
        diameter=parameter["diameter"]
        type=parameter["type"]
        radius=parameter["radius"]
        height=parameter.get("height", 0)
        os.makedirs(save_directory, exist_ok=True)
        if type=="XSZJ" or type=="XSZJ_POM":
            self.filename = f"XSZJ_{diameter:.2f}mm.dwg"
            if radius is not None and radius != 0:
                self.filename = f"XSZJ_R{radius:.3f}mm-Φ{diameter:.2f}.dwg"
        elif type=="XJJK":
            self.filename = f"XJJK_Φ{diameter:.2f}mm-H{height:.2f}mm.dwg"
        else:
            self.filename = f"{type}_Φ{diameter:.2f}mm.dwg"
        if not self.filename.endswith('.dwg'):
            self.filename += '.dwg'
        filepath = os.path.join(save_directory, self.filename)
        parent_dir = os.path.dirname(filepath) or save_directory
        os.makedirs(parent_dir, exist_ok=True)
        
        for attempt in range(5):
            try:
                self.acad.doc.SaveAs(filepath, 60)
                print(f"保存成功: {filepath}")
                return filepath
            except Exception as error:
                error_str = str(error)
                if '-2147418111' in error_str or '拒绝接收' in error_str or '2147352567' in error_str:
                    print(f"AutoCAD 繁忙，等待重试... (尝试 {attempt + 1}/5)")
                    time.sleep(1)
                    continue
                else:
                    print(f"保存失败: {error}")
                    break
        
        return None
           
    def main(self,parameter,type: str = "XSZJ",designer_name: str = "默认设计师"):
        """主函数"""
        if type=="XSZJ" or type=="XSZJ_POM":
            if type=="XSZJ_POM":
                pom_obj=POM(self.acad)
                pom_obj.draw_pom(parameter)
                pom_obj.draw_port(parameter)
            else:
                self.draw_cu(parameter)
                self.draw_port(parameter)
        #设置名称
            self.set_layer("轮廓线")
            if parameter["radius"] is not None and parameter["radius"] != 0:
                date_name( name=f"XSZJ / R{parameter['radius']:.3f}-Φ{parameter['diameter']:.2f}")
            else:
                date_name( name=f"XSZJ / Φ{parameter['diameter']:.2f}")
            print("缩放到范围...")
            safe_acad_operation(
            lambda: self.acad.doc.SendCommand("_.zoom _e "),
            "缩放到范围",
            max_retries=3,
            retry_delay=0.8
            )
        elif type=="XJJK" :
            
            self.draw_pom(parameter)
            self.set_layer("轮廓线")
            date_name( name=f"XJJK / Φ{parameter['diameter']:.0f}-H{parameter['height']:.0f}")
   
        print("缩放到范围...")
        safe_acad_operation(
        lambda: self.acad.doc.SendCommand("_.zoom _e "),
        "缩放到范围",
        max_retries=3,
        retry_delay=0.8
        )
        time.sleep(1.0)  # 增加等待时间

        self.set_layer("剖面线")
        
        base=parameter["base"]   
        diameter=parameter["diameter"]
        if type=="XSZJ":
            internal_x=base.x+1
            internal_y=base.y+1
        # 使用 safe_acad_operation 为 create_hatch 添加重试机制，避免 AutoCAD 繁忙导致的失败
            time.sleep(0.5)
            safe_acad_operation(lambda: create_hatch(self.acad, internal_x, internal_y),
                    operation_name="创建填充1", max_retries=3, retry_delay=1.0)
            time.sleep(0.5)
            safe_acad_operation(lambda: create_hatch(self.acad, internal_x+diameter-2, internal_y),
                    operation_name="创建填充2", max_retries=3, retry_delay=1.0)
        elif type=="XJJK" or type=="XSZJ_POM":
            internal_x=base.x-1
            internal_y=base.y+1
            time.sleep(0.5)
            safe_acad_operation(lambda: create_hatch(self.acad, internal_x, internal_y),
                    operation_name="创建填充1", max_retries=3, retry_delay=1.0)
            time.sleep(0.5)
            safe_acad_operation(lambda: create_hatch(self.acad, internal_x+diameter+2, internal_y),
                    operation_name="创建填充2", max_retries=3, retry_delay=1.0)
        
        
        self.set_layer("轮廓线")

        print("插入图块...")
        insertionPnt = APoint(-187, -110)
        insertionPnt2 = APoint(-187, -110)
        
        base_path = os.path.join(BASE_DIR, "blocks")
        block_configs = [
        (insertionPnt, os.path.join(base_path, "A4图框.dwg")),
        (insertionPnt2, os.path.join(base_path, f"{type}.dwg")),
        (insertionPnt2, os.path.join(base_path, f"{designer_name}.dwg"))
            ]       
        block_results = []
        for i, config in enumerate(block_configs, 1):
                print(f"  插入第 {i}/3 个图块...")
                result = insert_block(self.acad, *config)
                block_results.append(result)
                time.sleep(1.5)
       
if __name__ == "__main__":
    designer_name = "周凡"
    
    params_list = [
        {   "type":"XSZJ_POM",
            "base": APoint(0, 0),
            "diameter":10.8,
            "POM_thickness": 1.5,
            "Cu_thickness": 0.5,
            "POM_height": 10.0,
            "height": 1.1,
            "radius": -9.497


        },
        {   "type":"XSZJ_POM",
           "base": APoint(0, 0),
           "diameter":10,
           "POM_thickness": 1.5,
           "Cu_thickness": 0.5,
           "POM_height": 10.0,
           "height": 1.3,
           "radius": -9.497
        }
        # {
            # "type":"XJJK",  
            # "base": APoint(-130, 0),
            # "diameter": float(70.17),
            # "POM_thickness": 1.5,
            # "Cu_thickness": 0.5,
            # "POM_height": 10.0
        # },
        # {
            # "type":"XJJK",  
            # "base": APoint(-130, 0),  
            # "diameter": float(72.17),
            # "POM_thickness": 1.5,
            # "Cu_thickness": 0.5,
            # "POM_height": 10.0
        # }
    ]
    
    for index, params in enumerate(params_list, 1):
        print(f"\n正在创建第 {index}/{len(params_list)} 个夹具图形...")
        
        fixture = None
        try:
            fixture = FixtureOperations()
            fixture.main(params, type=params["type"], designer_name=designer_name)
            fixture.save_drawing(params)
            print(f"✓ 第 {index} 个夹具图形创建成功")
        except Exception as error:
            print(f"✗ 夹具图形创建失败，错误: {error}")
            import traceback
            traceback.print_exc()
        finally:
            if fixture is not None:
                print("关闭 AutoCAD 连接...")
                fixture.acad = None
                print("等待 AutoCAD 释放资源...")
                time.sleep(1.5)
   