import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

class FixtureGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("夹具 AutoCAD 绘图工具")
        self.root.geometry("400x400")
        
        # 类型定义
        self.types = ["POM", "XSZJ", "XJJK"]
        
        # 创建界面
        self.create_widgets()
        
        # 初始化字段显示
        self.update_input_fields()
    
    def create_widgets(self):
        """创建界面控件"""
        # 类型选择
        tk.Label(self.root, text="类型:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.type_combo = ttk.Combobox(self.root, values=self.types, state="readonly")
        self.type_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_input_fields())
        
        # 直径输入（所有类型都需要）
        tk.Label(self.root, text="直径:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.diameter_entry = tk.Entry(self.root)
        self.diameter_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # 其他可选参数（初始隐藏）
        self.param_widgets = {}
        param_configs = [
            ("radius", "半径:"),
            ("radius2", "半径2:"),
            ("height", "高度:"),
            ("POM_thickness", "POM厚度:"),
            ("Cu_thickness", "铜厚度:"),
            ("POM_height", "POM高度:")
        ]
        
        for i, (key, label) in enumerate(param_configs, start=2):
            tk.Label(self.root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self.root)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.param_widgets[key] = entry
        
        # 启动按钮
        tk.Button(self.root, text="开始绘图", command=self.start_drawing, 
                 width=15, bg="lightblue").grid(row=len(param_configs)+2, column=0, 
                                               columnspan=2, pady=20)
        
        # 回车键绑定
        self.root.bind('<Return>', lambda e: self.start_drawing())
    
    def update_input_fields(self):
        """根据类型更新显示的输入字段"""
        type_ = self.type_combo.get()
        
        # 隐藏所有可选参数
        for widget in self.param_widgets.values():
            widget.grid_remove()
        
        # 根据类型显示相应参数
        if type_ == "POM":
            for key in ["radius", "radius2", "height", "POM_thickness"]:
                self.param_widgets[key].grid()
        
        elif type_ == "XSZJ":
            self.param_widgets["radius"].grid()
        
        elif type_ == "XJJK":
            for key in ["height", "POM_thickness", "Cu_thickness", "POM_height"]:
                self.param_widgets[key].grid()
    
    def validate_input(self, value, name):
        """验证输入是否为有效数字"""
        if not value:
            return True  # 可选参数可以为空
        try:
            float(value)
            return True
        except ValueError:
            messagebox.showerror("输入错误", f"{name}请输入有效的数值！")
            return False
    
    def start_drawing(self):
        """启动绘图过程"""
        # 获取类型
        type_ = self.type_combo.get()
        if not type_:
            messagebox.showwarning("选择错误", "请选择夹具类型！")
            return
        
        # 验证直径（必需）
        diameter = self.diameter_entry.get().strip()
        if not diameter or not self.validate_input(diameter, "直径"):
            return
        
        # 构建参数字典
        params = {
            "type": type_,
            "base": "-130,0" if type_ == "XJJK" else "0,0",
            "diameter": diameter
        }
        
        # 添加可选参数
        optional_params = ["radius", "radius2", "height", 
                          "POM_thickness", "Cu_thickness", "POM_height"]
        
        for param in optional_params:
            value = self.param_widgets[param].get().strip()
            if value:
                if not self.validate_input(value, param):
                    return
                params[param] = value
        
        # 构建并执行命令
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cmd = ["python", os.path.join(script_dir, "fixture.py"), 
               "--params", str(params)]
        
        try:
            subprocess.Popen(cmd, shell=True, cwd=script_dir)
            messagebox.showinfo("成功", f"已启动 {type_} 类型夹具的绘制任务！")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败：{e}")

def main():
    root = tk.Tk()
    app = FixtureGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()