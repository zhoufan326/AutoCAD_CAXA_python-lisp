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
    ("下摆机抛光基模", "XPMJM", 6, False),
    ("下摆机精磨基模", "XJMJM", 6, False),
    ("基准模压聚氨酯", "JZM", 3, False),
    ("基准模改丸片", "JZM_KC", 3, True),
    ("高速抛光修盘基模", "GPMXJ", 6, False),
    ("高速抛光基模修盘", "GPMJX", 3, False),
    ("精磨丸片", "精磨丸片", 6, False),  # 直接使用中文名称作为drawing_type
    ("修盘丸片", "修盘丸片", 3, False)   # 直接使用中文名称作为drawing_type
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


def save_config(r_value, d_value, selected_groups, draw_bottom):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'r_value': r_value,
                'd_value': d_value,
                'selected_groups': selected_groups,
                'draw_bottom': draw_bottom
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置失败: {e}")


def start_drawing():
    """开始绘图"""
    r = r_entry.get().strip()
    d = d_entry.get().strip()
    
    if not (r and d):
        messagebox.showwarning("输入错误", "请输入完整的参数！")
        return
    
    selected = [i for i, var in enumerate(check_vars) if var.get()]
    if not selected:
        messagebox.showwarning("选择错误", "请至少选择一个图形组！")
        return
    
    # 获取"不绘制底座"复选框的值
    draw_bottom = not no_bottom_var.get()
    
    save_config(r, d, selected, draw_bottom)
    
    # 将选中的组分为传统图形组（索引0-5）和WP图形组（索引6-7）
    traditional_groups = [g for g in selected if g < 6]
    wp_groups = [g for g in selected if g >= 6]
    
    total_tasks = 0
    
    # 处理传统图形组
    if traditional_groups:
        # 直接调用draw_molds模块的功能，避免subprocess开销
        from molds.draw_molds import run_drawing_from_params
        try:
            run_drawing_from_params(r, d, traditional_groups, draw_bottom_part=draw_bottom)
            total_tasks += len(traditional_groups)
        except Exception as e:
            messagebox.showerror("错误", f"传统图形组启动失败：{e}\n{traceback.format_exc()}")
            return
    
    # 处理WP图形组（精磨丸片和修盘丸片）
    if wp_groups:
        # 将索引转换为wp.py中all_params的索引（6→0，7→1）
        wp_params_indices = [g - 6 for g in wp_groups]
        from molds.wp import run_wp_from_params
        try:
            run_wp_from_params(r, d, wp_params_indices)
            total_tasks += len(wp_groups)
        except Exception as e:
            messagebox.showerror("错误", f"WP图形组启动失败：{e}\n{traceback.format_exc()}")
            return
    
    if total_tasks > 0:
        messagebox.showinfo("成功", f"已启动 {total_tasks} 个图形组的绘制任务！")
    else:
        messagebox.showwarning("警告", "没有选择任何有效的图形组！")


def create_gui():
    """创建GUI界面"""
    global r_entry, d_entry, check_vars
    
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
    
    # 选择图形组部分
    tk.Label(root, text="选择图形组:", font=('仿宋', 14, 'bold')).grid(row=2, column=0, columnspan=2, pady=10, sticky="w", padx=30)
    
    checkbox_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN, padx=20, pady=10)
    checkbox_frame.grid(row=3, column=0, columnspan=2, padx=30, pady=7, sticky="nsew")
    
    config = load_config()
    saved_groups = config.get('selected_groups', None)
    check_vars = []
    
    for i, (name, gtype, b, neg) in enumerate(GROUPS):
        var = tk.BooleanVar(value=(i in saved_groups if saved_groups is not None else True))
        check_vars.append(var)
        
        text = f"{name} ({gtype})" + (" [反半径]" if neg else "")
        tk.Checkbutton(checkbox_frame, text=text, variable=var, font=('仿宋', 14, 'bold')).pack(anchor="w", pady=3, padx=15)
    
    # 设置默认值
    if 'r_value' in config:
        r_entry.insert(0, config['r_value'])
    if 'd_value' in config:
        d_entry.insert(0, config['d_value'])
    
    # 添加"不绘制底座"复选框
    global no_bottom_var
    no_bottom_var = tk.BooleanVar(value=(not config.get('draw_bottom', True)))
    tk.Checkbutton(root, text="不绘制底座", variable=no_bottom_var, font=('仿宋', 14, 'bold')).grid(row=4, column=0, columnspan=2, pady=10, padx=30, sticky="w")
    
    # 按钮部分 - 使用黄金分割比设置按钮大小
    button_width = 25
    button_height = 2
    tk.Button(root, text="开始绘图", command=start_drawing, width=button_width, height=button_height, font=('仿宋', 14, 'bold')).grid(row=5, column=0, columnspan=2, pady=17)
    
    # 回车键绑定
    root.bind('<Return>', lambda e: start_drawing())
    
    # 窗口退出时保存配置
    root.protocol("WM_DELETE_WINDOW", lambda: (save_config(
        r_entry.get().strip(), 
        d_entry.get().strip(), 
        [i for i, var in enumerate(check_vars) if var.get()],
        not no_bottom_var.get()
    ), root.destroy()))
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()