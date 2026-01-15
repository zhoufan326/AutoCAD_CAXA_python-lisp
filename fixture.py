
import math
import os
import time
from typing import Optional
from pyautocad import APoint, aDouble, Autocad
from utils import set_layer, create_hatch, insert_block, date_name
# from utils import load_linetypes
DEFAULT_TEMPLATE_PATH = r"Z:\AutoCAD_AI\新图样.dwt"
DEFAULT_SAVE_DIR = "D:\\CAD\\test"
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
                for _ in range(3):
                    try:
                        self.acad.app.Documents.Add(template_path)
                        print("模板加载成功，等待文档准备就绪...")
                        time.sleep(1.5)
                        break
                    except Exception as e:
                        if '繁忙' in str(e) or '2147418111' in str(e):
                            time.sleep(1.5)
                            continue
                        else:
                            print(f"模板加载失败: {e}")
                            break
        self.set_layer=set_layer                
    def save_drawing(self, diameter: float, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
        if not self.acad or not self.acad.doc:
            print("错误: AutoCAD 文档未初始化")
            return None
        
        if not self.acad.doc.Name:
            print("错误: AutoCAD 文档未打开")
            return None

        os.makedirs(save_directory, exist_ok=True)
        
        self.filename = f"XSZJ_{diameter:.0f}mm.dwg"
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
                if '-2147418111' in error_str or '拒绝接收' in error_str:
                    print(f"AutoCAD 繁忙，等待重试... (尝试 {attempt + 1}/5)")
                    time.sleep(1)
                    continue
                else:
                    print(f"保存失败: {error}")
                    break
        
        return None
           
    # ==================== 绘制图形 ====================
    def draw(self, parameter):
        """绘制标准夹具
        parameter（夹具参数）"""
        base = parameter["base"]
        diameter = parameter["diameter"]
        POM_thickness = parameter["POM_thickness"]
        
        
        
        A = base + APoint(0, 2.5)
        B = A + APoint(-POM_thickness, 0)
        C = B + APoint(0, 2.5)
        D = C + APoint(2*POM_thickness+diameter, 0)
        E = D + APoint(0, -2.5)
        F = E + APoint(-POM_thickness, 0)
        G = F + APoint(0, -2.5)

        set_layer("轮廓线")
        pnts = [A, B, C, D, E, F, G, base, A]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)
        set_layer("中心线")
        
        self.acad.model.AddLine(APoint(A.x+diameter/2, A.y-5), APoint(A.x+diameter/2, A.y+5))
        set_layer("标注线")
       
        
        
        
        

        dim_list = [None]*6
      
       
        DimLineLocation_C = C + APoint(-4, 0)
        dim_list[2] = self.acad.model.AddDimRotated(C, B, DimLineLocation_C, math.radians(90))
        DimLineLocation_D = D + APoint(0, 25)
        dim_list[3] = self.acad.model.AddDimRotated(D, C, DimLineLocation_D, 0)
        dim_list[3].TextOverride = "Φ<>"
        DimLineLocation_G = G + APoint(0, -6)
        dim_list[4] = self.acad.model.AddDimRotated(base, G, DimLineLocation_G, 0)
        dim_list[4].TextOverride = "Φ<>"
        
        



    
    def draw_port(self, parameter):
        """绘制夹具端口"""
        base = parameter["base"]
        diameter = parameter["diameter"]
        Cu_thickness = parameter["Cu_thickness"]
        base2 = base + APoint(diameter/2-2.5, Cu_thickness)
        A = base2 + APoint(0, 2)
        B = A + APoint(-1.7, 0)
        C = B + APoint(0, 2.5)
        D = C + APoint(8.4, 0)
        E = D + APoint(0, -2.5)
        F = E + APoint(-1.7, 0)
        G = F + APoint(0, -2)
        set_layer("轮廓线")
        pnts = [A, B, C, D, E, F, G, base2, A]
        pnts = [j for i in pnts for j in i]
        pnts = aDouble(pnts)
        self.acad.model.AddPolyLine(pnts)

        set_layer("标注线")
        DimLineLocation_F = F + APoint(0, 9)
        dim_list = [None]*6
        dim_list[0] = self.acad.model.AddDimRotated(A, F, DimLineLocation_F, 0)
        dim_list[0].TextOverride = "Φ<>"
        DimLineLocation_D = D + APoint(0,16)
        dim_list[1] = self.acad.model.AddDimRotated(C, D, DimLineLocation_D, 0)
        dim_list[1].TextOverride = "Φ<>"
        DimLineLocation_D = D + APoint(6,0)+diameter/2
        dim_list[2] = self.acad.model.AddDimRotated(E, D, DimLineLocation_D, math.radians(90))

        DimLineLocation_D = D +diameter/2
        dim_list[3] = self.acad.model.AddDimRotated(G, D, DimLineLocation_D, math.radians(90))
      
    
    def main(self,parameter,designer_name: str):
        """主函数"""
        self.draw(parameter)
        self.draw_port(parameter)
        self.save_drawing(diameter=parameter["diameter"])
        
        self.set_layer("轮廓线")
        date_name( name=f"XSZJ / Φ{parameter['diameter']:.0f}")
        
        base=parameter["base"]
        diameter=parameter["diameter"]
        self.set_layer("剖面线")
        internal_x=base.x+1
        internal_y=base.y+1
        acad = Autocad(create_if_not_exists=True)
        create_hatch(acad,internal_x,internal_y)
        create_hatch(acad,internal_x+diameter-2,internal_y)
        self.set_layer("轮廓线")
        print("插入图块...")
        insertionPnt = APoint(-187, -110)
        insertionPnt2 = APoint(-187, -110)
        
        base_path = r"Z:\AutoCAD_AI\Blocks"
        block_configs = [
        (insertionPnt, f"{base_path}\\A4图框.dwg"),
        (insertionPnt2, f"{base_path}\\XSZJ.dwg"),
        (insertionPnt2, f"{base_path}\\{designer_name}.dwg")
            ]       
        block_results = []
        for i, config in enumerate(block_configs, 1):
                print(f"  插入第 {i}/3 个图块...")
                result = insert_block(*config)
                block_results.append(result)
                time.sleep(0.8)



if __name__ == "__main__":
    designer_name = "周凡"
    
    params_list = [
        {
            "base": APoint(-130, 0),
            "diameter": 88.17,
            "POM_thickness": 1.5,
            "Cu_thickness": 0.5,
            "designer_name": designer_name
        # },
        # {
        #     "base": APoint(-100, 0),
        #     "diameter": 70.17,
        #     "POM_thickness": 1.5,
        #     "Cu_thickness": 0.5,
        #     "designer_name": designer_name
        # },
        # {
        #     "base": APoint(-100, 0),
        #     "diameter": 72.17,
        #     "POM_thickness": 1.5,
        #     "Cu_thickness": 0.5,
        #     "designer_name": designer_name
        }
    ]
    
    for index, params in enumerate(params_list, 1):
        print(f"\n正在创建第 {index}/{len(params_list)} 个夹具图形...")
        
        try:
            fixture = FixtureOperations()
            fixture.main(params, designer_name)
            print(f"✓ 第 {index} 个夹具图形创建成功")
        except Exception as error:
            print(f"✗ 夹具图形创建失败，错误: {error}")
        finally:
            if 'fixture' in locals():
                print("关闭 AutoCAD 连接...")
                fixture.acad = None
                print("等待 AutoCAD 释放资源...")
                time.sleep(1.5)
   