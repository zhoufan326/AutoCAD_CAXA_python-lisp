import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# 图形组配置
GROUPS = [
    ("下摆机抛光基模", "XPMJM", 6, False),
    ("下摆机精磨基模", "XJMJM", 6, False),
    ("基准模压聚氨酯", "JZM", 3, False),
    ("基准模改丸片", "JZM_KC", 3, True),
    ("高速抛光修盘基模", "GPMXJ", 6, False),
    ("高速抛光基模修盘", "GPMJX", 3, False)
]

def start_drawing():
    # 获取输入值
    r = r_entry.get().strip()
    d = d_entry.get().strip()
    
    # 验证输入
    if not (r and d):
        messagebox.showwarning("输入错误", "请输入完整的参数！")
        return
    
    
    # 获取选中的图形组
    selected = [i for i, var in enumerate(vars) if var.get()]
    if not selected:
        messagebox.showwarning("选择错误", "请至少选择一个图形组！")
        return
    
    # 构建命令
    cmd = ["python", "main.py", r, d]
    if selected != list(range(len(GROUPS))):
        cmd.extend(["--groups", ",".join(map(str, selected))])
    
    # 启动绘图任务
    try:
        subprocess.Popen(cmd, shell=True)
        messagebox.showinfo("成功", f"已启动 {len(selected)} 个图形组的绘制任务！")
    except Exception as e:
        messagebox.showerror("错误", f"启动失败：{e}")

# 创建主窗口
root = tk.Tk()
root.title("AutoCAD绘图")
root.geometry("450x350")

# 输入框部分
tk.Label(root, text="镜片R值:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
r_entry = tk.Entry(root)
r_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="毛坯直径:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
d_entry = tk.Entry(root)
d_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

# 选择图形组部分
tk.Label(root, text="选择图形组:").grid(row=2, column=0, columnspan=2, pady=10)

# 使用Frame包装复选框
checkbox_frame = tk.Frame(root)
checkbox_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

vars = []
for i, (name, gtype, b, neg) in enumerate(GROUPS):
    var = tk.BooleanVar(value=True)
    vars.append(var)
    
    text = f"{name} ({gtype})" + (" [反半径]" if neg else "")
    tk.Checkbutton(checkbox_frame, text=text, variable=var).pack(anchor="w", pady=2)

# 按钮部分
tk.Button(root, text="开始绘图", command=start_drawing, width=15).grid(
    row=4, column=0, columnspan=2, pady=20)

# 回车键绑定
root.bind('<Return>', lambda e: start_drawing())

root.mainloop()