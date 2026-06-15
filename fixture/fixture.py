import math
import os
import sys
import time

# 路径配置 - 必须在导入本地模块之前设置
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from utils.com_interface import APoint
from utils import set_layer, create_hatch, insert_block, date_name, save_drawing, _initialize_acad
from fixture_pom import draw_pom
from pom import pom_main
from fixture_cu import draw_cu, draw_port
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "新图样.dwt")
BLOCKS_PATH = os.path.join(PROJECT_ROOT, "blocks")

def retry_operation(operation, operation_name="操作", max_retries=3, initial_delay=1.0):
    """带重试机制的操作执行"""
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as e:
            if attempt < max_retries and ("-2147418111" in str(e) or "拒绝接收" in str(e)):
                print(f"  {operation_name} 繁忙，{attempt}/{max_retries} 次重试...")
                time.sleep(initial_delay)
                continue
            raise

def print_to_pdf(acad, filename, save_dir):
    """将图纸打印为PDF文件"""
    if not acad.doc:
        print("错误: 未找到 AutoCAD 文档")
        return False

    pdf_path = os.path.join(save_dir, f"{filename}.pdf")
        
    try:
        plot_config = acad.doc.PlotConfigurations.Add(f"PDF_Plot_{filename}", "Model")
        
        plot_config.ConfigName = "DWG to PDF.pc3"
        plot_config.PaperSize = "A4"
        plot_config.UseStandardScale = True
        plot_config.StandardScale = 1
        plot_config.PlotType = 3
        plot_config.PlotToFile = True
        plot_config.PlotFile = pdf_path
        plot_config.CenterPlot = True
        plot_config.PlotRotation = 0
        
        retry_operation(
            lambda: acad.doc.Plot.PlotToDevice(plot_config.ConfigName, plot_config.Name),
            "执行打印"
        )
        
        retry_operation(
            lambda: plot_config.Delete(),
            "删除临时打印配置"
        )
        
        print(f"✓ PDF 文件已创建: {pdf_path}")
        return True
    except Exception as e:
        print(f"错误: 打印为PDF失败 - {e}")
        return False

def create_drawing(acad, params, designer_name="周凡"):
    """创建图纸主函数"""
    type_ = params["type"]
    base = params["base"]
    diameter = params["diameter"]
    radius = params.get("radius")
    height = params.get("height", 0)
    
    if type_ == "XSZJ" or type_ == "XSZJ_POM" or type_ == "POM":
        filename = f"XSZJ／R{radius:.3f}-Φ{diameter:.2f}" if radius else f"XSZJ／Φ{diameter:.2f}"
    elif type_ == "XJJK":
        filename = f"XJJK／Φ{diameter:.2f}-H{height:.2f}"
    else:
        filename = f"{type_}／Φ{diameter:.2f}"
    
    if type_ == "POM":
        pom_main(acad, params)
    elif type_ == "XSZJ" or type_ == "XSZJ_POM":
        draw_cu(params)
        draw_port(params)
    elif type_ == "XJJK":
        draw_pom(params)
    
    set_layer("轮廓线")
    date_name(acad, name=filename)
    
    retry_operation(
        lambda: acad.doc.SendCommand("_.zoom _e "),
        "缩放到范围"
    )
    time.sleep(0.5)
    
    set_layer("剖面线")
    if type_ == "XSZJ":
        x, y = base.x + 1, base.y + 1
        retry_operation(lambda: create_hatch(acad, x, y), "创建填充1")
        retry_operation(lambda: create_hatch(acad, x + diameter - 2, y), "创建填充2")
    else:
        x, y = base.x - 1, base.y + 1
        retry_operation(lambda: create_hatch(acad, x, y), "创建填充1")
        retry_operation(lambda: create_hatch(acad, x + diameter + 2, y), "创建填充2")
    
    set_layer("轮廓线")
    
    insertion_point = APoint(-187, -110)
    blocks = [
        (insertion_point, os.path.join(BLOCKS_PATH, "A4图框.dwg")),
        (insertion_point, os.path.join(BLOCKS_PATH, f"{type_}.dwg")),
        (insertion_point, os.path.join(BLOCKS_PATH, f"{designer_name}.dwg"))
    ]
    
    for block_point, block_path in blocks:
        retry_operation(
            lambda: insert_block(acad, block_point, block_path),
            f"插入图块 {os.path.basename(block_path)}"
        )
        time.sleep(0.5)

    return filename

def parse_parameters(param_str):
    """解析参数字符串"""
    import ast
    params = ast.literal_eval(param_str)
    
    # 转换base为APoint对象
    if isinstance(params.get("base"), str):
        x, y = map(float, params["base"].split(","))
        params["base"] = APoint(x, y)
    
    # 转换数值类型
    number_keys = ["diameter", "radius", "radius2", "height", 
                   "POM_thickness", "Cu_thickness", "POM_height"]
    for key in number_keys:
        if key in params and isinstance(params[key], str):
            params[key] = float(params[key])
    
    return params

if __name__ == "__main__":
    # 默认参数
    default_params = [
        {
            "type": "POM",
            "base": APoint(0, 0),
            "diameter": 12.7,
            "height": 4,
            "radius": -143.85,
            "radius2": 143.85
        },
        {
            "type": "XJJK",
            "base": APoint(-130, 0),
            "diameter": 70.17,
            "POM_thickness": 1.5,
            "POM_height": 10.0
        }
    ]
    
    # 命令行参数处理
    if len(sys.argv) > 2 and sys.argv[1] == "--params":
        params_list = [parse_parameters(sys.argv[2])]
    else:
        params_list = default_params
    
    # 创建图纸
    SAVE_DIR = os.path.join(PROJECT_ROOT, "output")
    
    for i, params in enumerate(params_list, 1):
        print(f"\n创建第 {i}/{len(params_list)} 个夹具图形...")
        
        acad = _initialize_acad()
        if os.path.exists(TEMPLATE_PATH):
            retry_operation(
                lambda: acad.app.Documents.Add(TEMPLATE_PATH),
                "加载模板"
            )
            time.sleep(0.5)
            acad.doc = acad.app.ActiveDocument
            acad.model = acad.doc.ModelSpace
        filename = create_drawing(acad, params, designer_name=params.get("designer_name", "周凡"))
        save_drawing(acad, filename, SAVE_DIR)
        print_to_pdf(acad, filename, SAVE_DIR)
        
        print(f"✓ 第 {i} 个夹具图形创建成功")