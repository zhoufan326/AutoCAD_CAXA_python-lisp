import tkinter as tk
from tkinter import messagebox
import os
import json
import sys
import traceback

# 添加父目录到路径以确保能导入其他模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 图形组配置
GROUPS = [
    ("下摆机抛光基模", "XPMJM", False),
    ("下摆机精磨基模", "XJMJM", False),
    ("基准模压聚氨酯", "JZM", False),
    ("基准模改丸片", "JZM_KC", True),
    ("高速抛光修盘基模", "GPMXJ", False),
    ("高速抛光基模修盘", "GPMJX", False),
    ("精磨丸片", "精磨丸片", False),  # 直接使用中文名称作为drawing_type
    ("修盘丸片", "修盘丸片", False)   # 直接使用中文名称作为drawing_type
]

# 配置文件路径 - 保存在draw文件夹
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
    return {}


def save_config(r_value, d_value, a_value, b_value, c_value, designer_name, selected_groups, draw_bottom):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'r_value': r_value,
                'd_value': d_value,
                'a_value': a_value,
                'b_value': b_value,
                'c_value': c_value,
                'designer_name': designer_name,
                'selected_groups': selected_groups,
                'draw_bottom': draw_bottom
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置失败: {e}")


def start_drawing():
    """开始绘图"""
    r = r_entry.get().strip()
    d = d_entry.get().strip()
    a = a_entry.get().strip() or str(3)  # 默认值为3
    b = b_entry.get().strip() or str(6)  # 默认值为6
    c = c_entry.get().strip() or str(25)  # 默认值为25
    designer_name = designer_entry.get().strip() or "周凡"  # 默认值为"周凡"
    
    if not (r and d):
        messagebox.showwarning("输入错误", "请输入完整的R值和直径！")
        return
    
    try:
        a = float(a)
        b = float(b)
        c = float(c)
    except ValueError:
        messagebox.showwarning("输入错误", "a、b、c参数必须为数字！")
        return
    
    selected = [i for i, var in enumerate(check_vars) if var.get()]
    if not selected:
        messagebox.showwarning("选择错误", "请至少选择一个图形组！")
        return
    
    # 获取"不绘制底座"复选框的值
    draw_bottom = not no_bottom_var.get()
    
    save_config(r, d, a, b, c, designer_name, selected, draw_bottom)
    
    # 将选中的组分为传统图形组和WP图形组
    traditional_groups = [g for g in selected if g < 6]
    wp_groups = [g for g in selected if g >= 6]
    
    total_tasks = 0
    
    # 导入所有需要的模块
    from molds.draw_molds import batch_draw_molds
    from molds.wp import run_wp_from_params
    
    # 处理传统图形组
    if traditional_groups:
        batch_draw_molds(r, d, traditional_groups, draw_bottom=draw_bottom, designer_name=designer_name, a_value=a, b_value=b, c_value=c)
        total_tasks += len(traditional_groups)
    
    # 处理WP图形组
    if wp_groups:
        run_wp_from_params(r, d, [g - 6 for g in wp_groups], designer_name=designer_name)
        total_tasks += len(wp_groups)
    
    if total_tasks == 0:
        messagebox.showwarning("警告", "没有选择任何有效的图形组！")


def create_gui():
    """创建GUI界面"""
    global r_entry, d_entry, a_entry, b_entry, c_entry, designer_entry, check_vars
    
    root = tk.Tk()
    root.title("AutoCAD绘图")
    # 使用黄金分割比设置窗口大小 (约1:1.618)，增加分辨率提高清晰度
    width = 525
    height = int(width * 1.618)
    root.geometry(f"{width}x{height}")
    
    # 输入框部分 - 使用黄金分割比例调整间距
    tk.Label(root, text="镜片R值:", font=('仿宋', 14, 'bold')).grid(row=0, column=0, padx=30, pady=10, sticky="e")
    r_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    r_entry.grid(row=0, column=1, padx=30, pady=10, sticky="ew")
    r_entry.focus()
    
    tk.Label(root, text="毛坯直径:", font=('仿宋', 14, 'bold')).grid(row=1, column=0, padx=30, pady=5, sticky="e")
    d_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    d_entry.grid(row=1, column=1, padx=30, pady=5, sticky="ew")
    
    tk.Label(root, text="设计师名称:", font=('仿宋', 14, 'bold')).grid(row=2, column=0, padx=30, pady=5, sticky="e")
    designer_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    designer_entry.grid(row=2, column=1, padx=30, pady=5, sticky="ew")
    
    # 添加a、b、c参数输入框
    tk.Label(root, text="模子厚度:", font=('仿宋', 14, 'bold')).grid(row=3, column=0, padx=30, pady=3, sticky="e")
    a_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    a_entry.grid(row=3, column=1, padx=30, pady=3, sticky="ew")
    
    tk.Label(root, text="连接轴厚度:", font=('仿宋', 14, 'bold')).grid(row=4, column=0, padx=30, pady=3, sticky="e")
    b_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    b_entry.grid(row=4, column=1, padx=30, pady=3, sticky="ew")
    
    tk.Label(root, text="底座高度:", font=('仿宋', 14, 'bold')).grid(row=5, column=0, padx=30, pady=3, sticky="e")
    c_entry = tk.Entry(root, font=('仿宋', 14, 'bold'), width=25)
    c_entry.grid(row=5, column=1, padx=30, pady=3, sticky="ew")
    
    # 选择图形组部分
    tk.Label(root, text="选择图形组:", font=('仿宋', 14, 'bold')).grid(row=6, column=0, columnspan=2, pady=8, sticky="w", padx=30)
    
    checkbox_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN, padx=20, pady=8)
    checkbox_frame.grid(row=7, column=0, columnspan=2, padx=30, pady=5, sticky="nsew")
    
    config = load_config()
    saved_groups = config.get('selected_groups', None)
    check_vars = []
    
    for i, (name, gtype, neg) in enumerate(GROUPS):
        var = tk.BooleanVar(value=(i in saved_groups if saved_groups is not None else True))
        check_vars.append(var)
        
        text = f"{name} ({gtype})" + (" [反半径]" if neg else "")
        tk.Checkbutton(checkbox_frame, text=text, variable=var, font=('仿宋', 14, 'bold')).pack(anchor="w", pady=2, padx=15)
    
    # 设置默认值
    if 'r_value' in config:
        r_entry.insert(0, config['r_value'])
    if 'd_value' in config:
        d_entry.insert(0, config['d_value'])
    if 'a_value' in config:
        a_entry.insert(0, config['a_value'])
    else:
        a_entry.insert(0, "3")  # 默认值为3
    if 'b_value' in config:
        b_entry.insert(0, config['b_value'])
    else:
        b_entry.insert(0, "6")  # 默认值为6
    if 'c_value' in config:
        c_entry.insert(0, config['c_value'])
    else:
        c_entry.insert(0, "25")  # 默认值为25
    if 'designer_name' in config:
        designer_entry.insert(0, config['designer_name'])
    else:
        designer_entry.insert(0, "周凡")  # 设置默认值为"周凡"
    
    # 添加"不绘制底座"复选框
    global no_bottom_var
    no_bottom_var = tk.BooleanVar(value=(not config.get('draw_bottom', True)))
    tk.Checkbutton(root, text="不绘制底座", variable=no_bottom_var, font=('仿宋', 14, 'bold')).grid(row=8, column=0, columnspan=2, pady=10, padx=30, sticky="w")
    
    # 按钮部分 - 使用黄金分割比设置按钮大小
    button_width = 25
    button_height = 2
    tk.Button(root, text="开始绘图", command=start_drawing, width=button_width, height=button_height, font=('仿宋', 14, 'bold')).grid(row=9, column=0, columnspan=2, pady=12)
    
    # 回车键绑定
    root.bind('<Return>', lambda e: start_drawing())
    
    # 窗口退出时保存配置
    root.protocol("WM_DELETE_WINDOW", lambda: (save_config(
        r_entry.get().strip(), 
        d_entry.get().strip(),
        a_entry.get().strip() or "3",
        b_entry.get().strip() or "6",
        c_entry.get().strip() or "25",
        designer_entry.get().strip() or "周凡",
        [i for i, var in enumerate(check_vars) if var.get()],
        not no_bottom_var.get()
    ), root.destroy()))
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()