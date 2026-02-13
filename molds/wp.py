
import math
import os
import time
from typing import Optional
# 使用绝对导入替代相对导入
from molds.Tool_calculation import SwingMachineToolingCalculator
from pyautocad import APoint, aDouble, Autocad
from utils import set_layer, create_hatch, insert_block, date_name,safe_acad_operation,initial_connection
# 常量定义
# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 根目录是当前目录的父目录（因为molds与utils平级）
BASE_DIR = os.path.dirname(CURRENT_DIR)
DEFAULT_TEMPLATE_PATH = os.path.join(BASE_DIR, "新图样.dwt")
DEFAULT_SAVE_DIR = os.path.join(BASE_DIR, "output")
EXCEL_PATH = os.path.join(CURRENT_DIR, "口径常数.xlsx")

# drawing_type常量定义（使用中文名称）
DRAWING_TYPE_JINGMO = "精磨丸片"
DRAWING_TYPE_XIUPAN = "修盘丸片"

class WP:
      # ==================== 创建 AutoCAD 连接 ====================
    
    def __init__(self, acad=None, template_path=DEFAULT_TEMPLATE_PATH):
        self.acad = None
        self.filename = None
        initial_connection(self, acad, template_path)

    def save_drawing(self, parameter, save_directory: str = DEFAULT_SAVE_DIR) -> Optional[str]:
        if not self.acad or not self.acad.doc:
            print("错误: AutoCAD 连接未初始化")
            return None
        
        if not self.acad.doc:
            print("错误: AutoCAD 文档未初始化")
            return None
        
        if not self.acad.doc.Name:
            print("错误: AutoCAD 文档未打开")
            return None
        
        diameter=parameter["diameter"]
        radius=parameter["radius"]
        # 获取radius的符号
        radius_sign = "+" if radius >= 0 else "-"
        os.makedirs(save_directory, exist_ok=True)   
        self.filename = f" WP_{radius_sign}R{abs(radius):.3f}-Φ{diameter:.2f}.dwg"
        filepath = os.path.join(save_directory, self.filename)
        parent_dir = os.path.dirname(filepath) or save_directory
        os.makedirs(parent_dir, exist_ok=True)
        
        try:
            self.acad.doc.SaveAs(filepath)
            print(f"✓ 图形已保存: {filepath}")
            return filepath
        except Exception as e:
            print(f"✗ 保存失败: {e}")
            import traceback
            traceback.print_exc()
            return None
           
    def main(self, parameter):
        """主函数"""
        set_layer("轮廓线")
        diameter = parameter["diameter"]
        radius = parameter["radius"]
        base = parameter["base"]
        designer_name = parameter.get("designer_name", "默认设计师")
        drawing_type = parameter.get("drawing_type", DRAWING_TYPE_JINGMO)
        radius_sign = "+" if radius >= 0 else "-"
        #计算矢高
        chord = diameter
        r = abs(radius)
        # 矢高 h = r - sqrt(r^2 - (chord/2)^2)
        sagitta = r - math.sqrt(r**2 - (chord / 2)**2)
        sagitta2 = r - math.sqrt(r**2 - 0.5**2)
        # 计算圆心角的一半（弧度）
        half_angle = math.asin((chord / 2) / r)
        # 创建两个数组up和down，各7个元素
        up = [0] * 7
        down = [0] * 7
        #计算圆心位置，起始角度
        if radius>=0:
            center=base+APoint(-radius+3+sagitta,0)
            start_angle=-half_angle
            end_angle=+half_angle
            up[1]=base+APoint(3, chord / 2)
            down[1]=base+APoint(3, -chord / 2)
            up[5]=base+APoint(3+sagitta-sagitta2,0.5)
            down[5]=base+APoint(3+sagitta-sagitta2,-0.5)

        else:
            center=base+APoint(abs(radius)+3,0)
            start_angle=math.pi-half_angle
            end_angle=math.pi+half_angle

            chord=chord+1 if chord <10 else chord+2
            up[1]=base+APoint(3+sagitta,chord / 2)
            down[1]=base+APoint(3+sagitta,-chord / 2)
            up[5]=base+APoint(3+sagitta,0.5)
            down[5]=base+APoint(3+sagitta,-0.5)
        
        
        
        up[0]=base+APoint(0,chord / 2)
        down[0]=base+APoint(0,-chord / 2)
        
        up[2]=base+APoint(0,0.75)
        down[2]=base+APoint(0,-0.75)
        up[3]=base+APoint(1,0.75)
        down[3]=base+APoint(1,-0.75)
        up[4]=base+APoint(3,0.5)
        down[4]=base+APoint(3,-0.5)
        up[6]=center+APoint(radius*math.cos(half_angle),abs(radius)*math.sin(half_angle))
        down[6]=center+APoint(radius*math.cos(half_angle),-abs(radius)*math.sin(half_angle))
    
        # 绘制圆弧
        arc = self.acad.model.AddArc(
            center,
            abs(radius),
            start_angle,
            end_angle
        )
        # 绘制第一段多段线：up1 -> up0 -> down0 -> down1
        pnts1 = [
            up[6],
            up[1],
            up[0],
            down[0],
            down[1],
            down[6],
            up[6],
        ]
        pnts1 = [j for i in pnts1 for j in i]
        pline1 = self.acad.model.AddPolyline(aDouble(pnts1))

        # 绘制第二段多段线：up2 -> up3 -> down3 -> down2
        pnts2 = [
            up[2],
            up[3],
            down[3],
            down[2],
        ]
        pnts2 = [j for i in pnts2 for j in i]
        pline2 = self.acad.model.AddPolyline(aDouble(pnts2))

        # 绘制第三段多段线：up5 -> up4 -> down4 -> down5
        pnts3 = [
            up[5],
            up[4],
            down[4],
            down[5],
        ]
        pnts3 = [j for i in pnts3 for j in i]
        pline3 = self.acad.model.AddPolyline(aDouble(pnts3))

        

        
        date_name( name=f" WP/{radius_sign}R{radius:.3f}-Φ{diameter:.2f}")
        
   
        print("缩放到范围...")
        safe_acad_operation(
        lambda: self.acad.doc.SendCommand("_.zoom _e "),
        "缩放到范围",
        max_retries=3,
        retry_delay=0.8
        )
        time.sleep(1.0)  # 增加等待时间

        set_layer("剖面线")
        
        base=parameter["base"]   
        diameter=parameter["diameter"]
        if type=="XSZJ":
            internal_x=base.x+2
            internal_y=base.y+2
        # 使用 safe_acad_operation 为 create_hatch 添加重试机制，避免 AutoCAD 繁忙导致的失败
            time.sleep(0.5)
            safe_acad_operation(lambda: create_hatch(self.acad, internal_x, internal_y),
                    operation_name="创建填充1", max_retries=3, retry_delay=1.0)

     
        set_layer("轮廓线")

        print("插入图块...")
        insertionPnt = APoint(-187, -110)
        insertionPnt2 = APoint(-187, -110)
        
        base_path = os.path.join(BASE_DIR, "blocks")
        
        # 直接使用drawing_type作为图块名称（因为drawing_type现在是中文名称："精磨丸片"或"修盘丸片"）
        wp_block_name = f"{drawing_type}.dwg"
            
        block_configs = [
        (insertionPnt, os.path.join(base_path, "A4图框.dwg")),
        (insertionPnt2, os.path.join(base_path, wp_block_name)),
        (insertionPnt2, os.path.join(base_path, f"{designer_name}.dwg"))
            ]       
        for i, config in enumerate(block_configs, 1):
                print(f"  插入第 {i}/{len(block_configs)} 个图块...")
                insert_block(self.acad, *config)
                time.sleep(1.5)
        return arc, pline1, pline2, pline3

def run_wp_from_params(r_value, d_value, selected_groups=None):
    """从参数运行WP绘图任务
    
    Args:
        r_value: 镜片R值
        d_value: 毛坯直径
        selected_groups: 选中的图形组索引列表（可选）
    """
    R = float(r_value)
    D = float(d_value)
    
    # 计算参数
    calculator = SwingMachineToolingCalculator(
        R=R, blank_D=D, polyurethane_thickness=0.3,
        diamond_pellet_thickness=3, delta_arc=2
    )
    results = calculator.calculate_all(EXCEL_PATH)
    
    # 定义所有WP绘图参数
    all_params = [
        {
          "radius": results["下摆机精磨基模R值"],
          "diameter": results["下摆机精磨基模口径"],
          "drawing_type": DRAWING_TYPE_JINGMO, "designer_name": "周凡"
        },
        {
          "radius": results["镜片R值"],
          "diameter": results["基准模口径"],
          "drawing_type": DRAWING_TYPE_XIUPAN, "designer_name": "周凡"
        }
    ]
    
    # 过滤选中的图形组
    params_list = all_params if not selected_groups else [all_params[i] for i in selected_groups]
    
    # 批量绘图
    for i, params in enumerate(params_list, 1):
        print(f"\n第{i}/{len(params_list)}: {params['drawing_type']}")
        
        wp = None
        try:
                wp = WP()
                params["base"] = APoint(0, 0)
                wp.main(params)
                wp.save_drawing(params)
        except Exception as e:
            print(f"失败: {e}")
        finally:
            if wp:
                wp.acad = None
            if i < len(params_list):
                time.sleep(2.0)

if __name__ == "__main__":
    designer_name = "周凡"
                # 创建计算器实例
    calculator = SwingMachineToolingCalculator(
            R=float(input("请输入镜片半径R：")),
            blank_D=float(input("请输入镜片口径D：")),
            polyurethane_thickness=0.3,
            diamond_pellet_thickness=3,
            delta_arc=2
        )
        
        # 执行计算
    results = calculator.calculate_all(EXCEL_PATH)
    
    params_list = [
        {  # 下摆机精磨丸片
            "base": APoint(0, 0),
            "diameter":results["下摆机精磨基模口径"],
            
            "radius": results["下摆机精磨基模R值"]
        },
        {  # 高速抛光修盘丸片
           "base": APoint(0, 0),
           "diameter":results["基准模口径"],
           
           "radius": results["镜片R值"]
        }
    ]

    try:
        # 为params_list添加drawing_type参数
        for index, params in enumerate(params_list, 1):
            try:
                # 根据索引设置drawing_type
                if index == 1:
                    params["drawing_type"] = DRAWING_TYPE_JINGMO
                else:
                    params["drawing_type"] = DRAWING_TYPE_XIUPAN
                    
                wp = WP()
                params["designer_name"] = designer_name
                wp.main(params)
                wp.save_drawing(params)
                print(f"✓ 第 {index} 个WP图形创建成功")
                wp.acad = None
            except Exception as error:
                print(f"✗ 第 {index} 个WP图形创建失败，错误: {error}")
                import traceback
                traceback.print_exc()
    finally:
        print("所有图形处理完成")
   