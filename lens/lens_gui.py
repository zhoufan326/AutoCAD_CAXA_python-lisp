import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pyautocad import APoint


class LensParamsGUI:
    """简化的镜片参数输入GUI"""
    
    # 按功能分组的参数字段定义
    FIRST_SURFACE_FIELDS = [
        ("radius1", "第一面半径 R1 (mm):", "-28.11"),
        ("radius1_tolerance", "第一面半径公差 (±mm):", ""),
        ("sagitta1", "第一面矢高 S1 (mm):", "-0.316"),
        ("sagitta1_tolerance", "第一面矢高公差 (±mm):", ""),
    ]
    
    SECOND_SURFACE_FIELDS = [
        ("radius2", "第二面半径 R2 (mm):", "28"),
        ("radius2_tolerance", "第二面半径公差 (±mm):", ""),
        ("sagitta2", "第二面矢高 S2 (mm):", ""),
        ("sagitta2_tolerance", "第二面矢高公差 (±mm):", ""),
    ]
    
    THICKNESS_FIELDS = [
        ("center_thickness", "中心厚度 Tc (mm):", "5"),
        ("thickness_tolerance", "厚度公差 (±mm):", ""),
    ]
    
    DIAMETER_FIELDS = [
        ("outer_diameter", "外径 D (mm):", "11.5"),
        ("upper_tolerance", "外径上偏差 (+mm):", ""),
        ("lower_tolerance", "外径下偏差 (-mm):", ""),
    ]
    
    # 标注设置字段
    DIMENSION_FIELDS = [
        ("text_height", "标注文字高度 (mm):", "2.5"),
    ]
    
    # 合并所有参数字段定义
    ALL_FIELDS = FIRST_SURFACE_FIELDS + SECOND_SURFACE_FIELDS + THICKNESS_FIELDS + DIAMETER_FIELDS
    
    # 数据存储文件路径
    DATA_FILE = os.path.join(os.path.dirname(__file__), "lens_gui_data.json")
    
    def __init__(self, root):
        self.root = root
        self.root.title("镜片参数配置 - 符号正负同Zemax")
        self.root.geometry("750x650")
        
        # 存储所有输入框
        self.entries = {}
        self.params_list = []
        
        # 存储镜片选择状态
        self.lens_selection = {1: True, 2: True, 3: True}  # 默认全部选中
        
        # 参数同步控制
        self.sync_radius_params = True  # 默认启用半径参数同步（镜片2、3与镜片1同步）
        self.sync_thickness_tolerance_params = True  # 默认启用厚度公差同步（所有镜片同步）
        self.sync_center_thickness_params = True  # 默认启用中心厚度同步（仅镜片2与3同步）
        
        self.create_widgets()
        
        # 加载之前保存的数据
        self.load_data()
        
        # 绑定参数变化事件
        self.root.after(100, self._bind_all_events)
        
    def create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        ttk.Label(main, text="镜片参数配置 - 符号正负同Zemax", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=5
        )
        
        # 标签页
        notebook = ttk.Notebook(main)
        notebook.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 创建三个相同的标签页
        for i in range(1, 4):
            tab = self.create_lens_tab(notebook, i)
            notebook.add(tab, text=f"镜片{i}")
        
        # 基准点设置
        base_frame = ttk.LabelFrame(main, text="布局设置", padding="10")
        base_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        base_frame.columnconfigure(0, weight=1)
        base_frame.columnconfigure(1, weight=1)
        
        # 镜片选择
        selection_frame = ttk.Frame(base_frame)
        selection_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(selection_frame, text="选择要绘制的镜片:").grid(row=0, column=0, sticky="w", padx=5)
        
        # 创建三个镜片选择复选框
        self.lens_checkboxes = {}
        for i in range(1, 4):
            var = tk.BooleanVar(value=True)
            checkbox = ttk.Checkbutton(selection_frame, text=f"镜片{i}", variable=var,
                                      command=lambda idx=i: self._on_lens_selection_change(idx))
            checkbox.grid(row=0, column=i, padx=10)
            self.lens_checkboxes[i] = var
        
        # 参数同步控制
        sync_frame = ttk.Frame(base_frame)
        sync_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # 半径参数同步
        self.sync_var = tk.BooleanVar(value=True)
        sync_checkbox = ttk.Checkbutton(sync_frame, text="半径参数同步", variable=self.sync_var,
                                       command=self._on_sync_change)
        sync_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Label(sync_frame, text="(镜片2和镜片3的R1、R2参数与镜片1保持同步)", font=("", 8)).grid(
            row=0, column=1, sticky="w", padx=5
        )
        
        # 厚度公差同步
        sync_thickness_tolerance_frame = ttk.Frame(base_frame)
        sync_thickness_tolerance_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.sync_thickness_tolerance_var = tk.BooleanVar(value=True)
        sync_thickness_tolerance_checkbox = ttk.Checkbutton(sync_thickness_tolerance_frame, 
                                                           text="厚度公差同步", 
                                                           variable=self.sync_thickness_tolerance_var,
                                                           command=self._on_thickness_tolerance_sync_change)
        sync_thickness_tolerance_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Label(sync_thickness_tolerance_frame, 
                 text="(镜片1、2、3的厚度公差参数保持同步)", 
                 font=("", 8)).grid(row=0, column=1, sticky="w", padx=5)
        
        # 中心厚度同步
        sync_center_thickness_frame = ttk.Frame(base_frame)
        sync_center_thickness_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.sync_center_thickness_var = tk.BooleanVar(value=True)
        sync_center_thickness_checkbox = ttk.Checkbutton(sync_center_thickness_frame, 
                                                       text="中心厚度同步", 
                                                       variable=self.sync_center_thickness_var,
                                                       command=self._on_center_thickness_sync_change)
        sync_center_thickness_checkbox.grid(row=0, column=0, sticky="w", padx=5)
        
        ttk.Label(sync_center_thickness_frame, 
                 text="(镜片2与3的中心厚度保持同步)", 
                 font=("", 8)).grid(row=0, column=1, sticky="w", padx=5)
        
        # 标注文字高度
        ttk.Label(base_frame, text="标注文字高度 (mm):").grid(row=4, column=0, sticky="e", padx=5)
        self.text_height = ttk.Entry(base_frame, width=15)
        self.text_height.insert(0, "2.5")
        self.text_height.grid(row=4, column=1, sticky="e", padx=5)
        
        # 按钮
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="开始绘图", command=self.start).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        
        
    def create_lens_tab(self, parent, lens_num):
        """创建镜片参数标签页"""
        tab = ttk.Frame(parent)
        
        # 第一面参数区域
        first_frame = ttk.LabelFrame(tab, text="第一面参数", padding="5")
        first_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        row = 0
        for field_id, label, default in self.FIRST_SURFACE_FIELDS:
            ttk.Label(first_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(first_frame, width=12)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            self.entries[f"lens{lens_num}_{field_id}"] = entry
            row += 1
        
        # 第二面参数区域
        second_frame = ttk.LabelFrame(tab, text="第二面参数", padding="5")
        second_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        row = 0
        for field_id, label, default in self.SECOND_SURFACE_FIELDS:
            ttk.Label(second_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(second_frame, width=12)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            self.entries[f"lens{lens_num}_{field_id}"] = entry
            row += 1
        
        # 厚度参数区域
        thickness_frame = ttk.LabelFrame(tab, text="厚度参数", padding="5")
        thickness_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        row = 0
        for field_id, label, default in self.THICKNESS_FIELDS:
            ttk.Label(thickness_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(thickness_frame, width=12)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            self.entries[f"lens{lens_num}_{field_id}"] = entry
            row += 1
        
        # 外径参数区域
        diameter_frame = ttk.LabelFrame(tab, text="外径参数", padding="5")
        diameter_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        row = 0
        for field_id, label, default in self.DIAMETER_FIELDS:
            ttk.Label(diameter_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(diameter_frame, width=12)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            self.entries[f"lens{lens_num}_{field_id}"] = entry
            row += 1
        
        # 设置列权重，使布局更美观
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        
        return tab
    
    def get_params(self, lens_num):
        """获取指定镜片的参数"""
        params = {}
        
        # 获取所有参数
        for field_id, _, _ in self.ALL_FIELDS:
            key = f"lens{lens_num}_{field_id}"
            value = self.entries[key].get().strip()
            
            try:
                # 处理可选字段
                if not value:
                    if field_id in ["sagitta1", "sagitta2"] or field_id.endswith("_tolerance"):
                        params[field_id] = None
                    else:
                        raise ValueError(f"镜片{lens_num}的{field_id}参数不能为空")
                else:
                    params[field_id] = float(value)
            except ValueError:
                raise ValueError(f"镜片{lens_num}的{field_id}参数无效: {value}")
        
        # 智能处理矢高公差
        self._smart_handle_sagitta_tolerances(params)
        
        # 检查外径是否有效
        if params.get("outer_diameter", 0) <= 0:
            return None
        
        # 添加全局参数
        try:
            text_height_value = self.text_height.get().strip()
            params["text_height"] = float(text_height_value) if text_height_value else 2.5
        except ValueError:
            params["text_height"] = 2.5  # 使用默认值
        
        return params
    
    def _on_lens_selection_change(self, lens_num):
        """镜片选择状态变化处理"""
        selected = self.lens_checkboxes[lens_num].get()
        self.lens_selection[lens_num] = selected
    
    def _on_sync_change(self):
        """半径参数同步状态变化处理"""
        self.sync_radius_params = self.sync_var.get()
        
        if self.sync_radius_params:
            # 如果启用同步，立即同步一次参数
            self._sync_radius_params()
    
    def _on_thickness_tolerance_sync_change(self):
        """厚度公差同步状态变化处理"""
        self.sync_thickness_tolerance_params = self.sync_thickness_tolerance_var.get()
        
        if self.sync_thickness_tolerance_params:
            # 如果启用同步，立即同步一次参数
            self._sync_thickness_tolerance_params()
    
    def _on_center_thickness_sync_change(self):
        """中心厚度同步状态变化处理"""
        self.sync_center_thickness_params = self.sync_center_thickness_var.get()
        
        if self.sync_center_thickness_params:
            # 如果启用同步，立即同步一次参数（默认以镜片2为基准）
            self._sync_center_thickness_params(2)

    
    def _sync_radius_params(self):
        """同步镜片1的R1、R2参数到镜片2和镜片3"""
        if not self.sync_radius_params:
            return
            
        try:
            # 获取镜片1的R1和R2参数值
            r1_value = self.entries["lens1_radius1"].get().strip()
            r2_value = self.entries["lens1_radius2"].get().strip()
            
            # 同步到镜片2和镜片3
            for lens_num in [2, 3]:
                if r1_value:
                    self.entries[f"lens{lens_num}_radius1"].delete(0, tk.END)
                    self.entries[f"lens{lens_num}_radius1"].insert(0, r1_value)
                
                if r2_value:
                    self.entries[f"lens{lens_num}_radius2"].delete(0, tk.END)
                    self.entries[f"lens{lens_num}_radius2"].insert(0, r2_value)
                    
        except (KeyError, tk.TclError):
            # 如果输入框尚未创建，忽略错误
            pass
    
    def _sync_thickness_tolerance_params(self):
        """同步所有镜片的厚度公差参数"""
        if not self.sync_thickness_tolerance_params:
            return
            
        try:
            # 获取镜片1的厚度公差参数值
            thickness_tolerance_value = self.entries["lens1_thickness_tolerance"].get().strip()
            
            # 同步到所有镜片（包括镜片1）
            for lens_num in [1, 2, 3]:
                if thickness_tolerance_value:
                    self.entries[f"lens{lens_num}_thickness_tolerance"].delete(0, tk.END)
                    self.entries[f"lens{lens_num}_thickness_tolerance"].insert(0, thickness_tolerance_value)
                    
        except (KeyError, tk.TclError):
            # 如果输入框尚未创建，忽略错误
            pass
    
    def _sync_center_thickness_params(self, source_lens_num):
        """同步镜片2和3的中心厚度参数，镜片1不同步"""
        if not self.sync_center_thickness_params:
            return
            
        try:
            # 获取源镜片的中心厚度参数值
            center_thickness_value = self.entries[f"lens{source_lens_num}_center_thickness"].get().strip()
            
            # 同步到目标镜片
            target_lens_num = 3 if source_lens_num == 2 else 2
            if center_thickness_value:
                self.entries[f"lens{target_lens_num}_center_thickness"].delete(0, tk.END)
                self.entries[f"lens{target_lens_num}_center_thickness"].insert(0, center_thickness_value)
                    
        except (KeyError, tk.TclError):
            # 如果输入框尚未创建，忽略错误
            pass
    
    def _bind_radius_events(self):
        """绑定R1、R2参数变化事件"""
        # 为镜片1的R1和R2输入框绑定变化事件
        for field_id in ["radius1", "radius2"]:
            entry_key = f"lens1_{field_id}"
            entry = self.entries.get(entry_key)
            if entry:
                entry.bind("<KeyRelease>", lambda e, field=field_id: self._on_radius_change(field))
    
    def _on_radius_change(self, field_id):
        """镜片1的R1或R2参数变化处理"""
        if self.sync_radius_params:
            self._sync_radius_params()
    
    def _on_thickness_tolerance_change(self):
        """厚度公差参数变化处理"""
        if self.sync_thickness_tolerance_params:
            self._sync_thickness_tolerance_params()
    
    def _on_center_thickness_change(self, source_lens_num):
        """中心厚度参数变化处理"""
        if self.sync_center_thickness_params:
            self._sync_center_thickness_params(source_lens_num)
    
    def _bind_all_events(self):
        """绑定所有参数变化事件"""
        # 绑定半径参数事件
        self._bind_radius_events()
        
        # 绑定厚度公差参数事件
        for lens_num in [1, 2, 3]:
            entry_key = f"lens{lens_num}_thickness_tolerance"
            entry = self.entries.get(entry_key)
            if entry:
                entry.bind("<KeyRelease>", lambda e: self._on_thickness_tolerance_change())
        
        # 绑定中心厚度参数事件（只绑定镜片2和3）
        for lens_num in [2, 3]:
            entry_key = f"lens{lens_num}_center_thickness"
            entry = self.entries.get(entry_key)
            if entry:
                entry.bind("<KeyRelease>", lambda e, num=lens_num: self._on_center_thickness_change(num))
    
    def _smart_handle_sagitta_tolerances(self, params):
        """智能处理矢高公差逻辑"""
        sagitta1_exists = params.get("sagitta1") is not None
        sagitta2_exists = params.get("sagitta2") is not None
        sagitta1_tol = params.get("sagitta1_tolerance")
        sagitta2_tol = params.get("sagitta2_tolerance")
        
        # 移除无效的公差参数（矢高不存在但设置了公差）
        for exists, tol, tol_key in [
            (sagitta1_exists, sagitta1_tol, "sagitta1_tolerance"),
            (sagitta2_exists, sagitta2_tol, "sagitta2_tolerance")
        ]:
            if not exists and tol is not None:
                params.pop(tol_key, None)
        
        # 智能设置公差（两个矢高都存在时）
        if sagitta1_exists and sagitta2_exists:
            if sagitta1_tol is not None and sagitta2_tol is None:
                params["sagitta2_tolerance"] = sagitta1_tol
            elif sagitta2_tol is not None and sagitta1_tol is None:
                params["sagitta1_tolerance"] = sagitta2_tol
            elif sagitta1_tol is None and sagitta2_tol is None:
                default_tol = 0.02
                params["sagitta1_tolerance"] = default_tol
                params["sagitta2_tolerance"] = default_tol
    
    def start(self):
        """开始绘图"""

        
        # 使用默认起始点坐标(0,0)
        base_x = 0.0
        base_y = 0.0
        # 固定间距为30mm
        spacing = 30.0
        
        # 收集被选中的镜片参数
        self.params_list = []
        current_x = base_x
        
        for lens_num in range(1, 4):
            # 只处理被选中的镜片
            if not self.lens_selection.get(lens_num, False):
                print(f"跳过未选中的镜片 {lens_num}")
                continue
                
            try:
                params = self.get_params(lens_num)
                if params:  # 只添加有效的镜片
                    params["base"] = APoint(current_x, base_y)
                    self.params_list.append(params)
                    current_x += params["outer_diameter"] + spacing
            except ValueError as e:
                messagebox.showerror("参数错误", str(e))

                return
        
        if not self.params_list:
            messagebox.showwarning("警告", "没有有效的镜片参数")

            return
        
        # 调用绘图函数
        try:
            from draw_lens import draw_multiple_lenses
            
            if draw_multiple_lenses(self.params_list):

                # 绘图完成后保存数据
                self.save_data()
            else:

                messagebox.showerror("错误", "绘图失败")
                
        except ImportError:
            messagebox.showerror("导入错误", "无法导入绘图模块")

        except Exception as e:
            messagebox.showerror("错误", f"绘图错误: {str(e)}")

    
    def reset(self):
        """重置所有参数"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # 设置默认值
        for lens_num in range(1, 4):
            for field_id, _, default in self.ALL_FIELDS:
                key = f"lens{lens_num}_{field_id}"
                if key in self.entries and default:
                    self.entries[key].insert(0, default)
        
        # 重置镜片选择状态
        for lens_num in range(1, 4):
            self.lens_checkboxes[lens_num].set(True)
            self.lens_selection[lens_num] = True
        

    
    def save_data(self):
        """保存当前数据到文件"""
        try:
            data = {
                "lens_selection": self.lens_selection,
                "lens_data": {},
                "text_height": self.text_height.get(),
                "sync_params": self.sync_var.get(),
                "sync_thickness_tolerance_params": self.sync_thickness_tolerance_var.get(),
                "sync_center_thickness_params": self.sync_center_thickness_var.get()
            }
            
            # 收集所有镜片数据
            for lens_num in range(1, 4):
                lens_data = {
                    field_id: self.entries[f"lens{lens_num}_{field_id}"].get()
                    for field_id, _, _ in self.ALL_FIELDS
                    if f"lens{lens_num}_{field_id}" in self.entries
                }
                data["lens_data"][f"lens{lens_num}"] = lens_data
            
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def load_data(self):
        """从文件加载数据"""
        try:
            if not os.path.exists(self.DATA_FILE):
                print("未找到数据文件，使用默认值")
                return
                
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载基本设置
            for widget_attr, data_key in [(self.text_height, "text_height")]:
                if data_key in data:
                    widget_attr.delete(0, tk.END)
                    widget_attr.insert(0, data[data_key])
            
            # 加载镜片选择状态
            if "lens_selection" in data:
                for lens_num_str, selected in data["lens_selection"].items():
                    lens_num = int(lens_num_str)
                    if lens_num in self.lens_checkboxes:
                        self.lens_checkboxes[lens_num].set(selected)
                        self.lens_selection[lens_num] = selected
            
            # 加载镜片数据
            if "lens_data" in data:
                for lens_num in range(1, 4):
                    lens_key = f"lens{lens_num}"
                    if lens_key in data["lens_data"]:
                        for field_id, value in data["lens_data"][lens_key].items():
                            entry_key = f"lens{lens_num}_{field_id}"
                            if entry_key in self.entries:
                                self.entries[entry_key].delete(0, tk.END)
                                self.entries[entry_key].insert(0, value)
            
            # 加载参数同步状态
            if "sync_params" in data:
                self.sync_var.set(data["sync_params"])
                self.sync_radius_params = data["sync_params"]
            
            # 加载厚度公差同步状态
            if "sync_thickness_tolerance_params" in data:
                self.sync_thickness_tolerance_var.set(data["sync_thickness_tolerance_params"])
                self.sync_thickness_tolerance_params = data["sync_thickness_tolerance_params"]
            
            # 加载中心厚度同步状态
            if "sync_center_thickness_params" in data:
                self.sync_center_thickness_var.set(data["sync_center_thickness_params"])
                self.sync_center_thickness_params = data["sync_center_thickness_params"]
            
            # 更新同步参数
            if self.sync_radius_params:
                self._sync_radius_params()
            
            if self.sync_thickness_tolerance_params:
                self._sync_thickness_tolerance_params()
            
            if self.sync_center_thickness_params:
                self._sync_center_thickness_params(2)
        except Exception as e:
            print(f"加载数据失败: {e}")
    
    def on_closing(self):
        """窗口关闭时的处理"""
        self.save_data()
        self.root.quit()


def main():
    """启动GUI"""
    root = tk.Tk()
    app = LensParamsGUI(root)
    
    # 设置窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()