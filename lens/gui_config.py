import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass
from pyautocad import APoint
import json
import os

# ====================== 参数存储功能 ======================

# 存储文件路径
PARAMS_STORAGE_FILE = os.path.join(os.path.dirname(__file__), "params_storage.json")


def save_params_to_storage(params_list: List[Dict[str, Any]]) -> bool:
    """
    保存参数到本地存储
    
    参数:
        params_list: 参数列表
    
    返回:
        bool: 是否保存成功
    """
    try:
        # 转换APoint对象为可序列化格式
        serializable_params = []
        for params in params_list:
            serializable = {}
            for key, value in params.items():
                if isinstance(value, APoint):
                    serializable[key] = {"type": "APoint", "x": value.x, "y": value.y}
                else:
                    serializable[key] = value
            serializable_params.append(serializable)
        
        # 写入JSON文件
        with open(PARAMS_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_params, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存参数失败: {str(e)}")
        return False


def load_params_from_storage() -> Optional[List[Dict[str, Any]]]:
    """
    从本地存储加载参数
    
    返回:
        Optional[List[Dict[str, Any]]]: 参数列表或None
    """
    try:
        if not os.path.exists(PARAMS_STORAGE_FILE):
            return None
        
        # 读取JSON文件
        with open(PARAMS_STORAGE_FILE, 'r', encoding='utf-8') as f:
            serializable_params = json.load(f)
        
        # 转换回原始格式
        params_list = []
        for params in serializable_params:
            restored = {}
            for key, value in params.items():
                if isinstance(value, dict) and value.get("type") == "APoint":
                    restored[key] = APoint(value["x"], value["y"])
                else:
                    restored[key] = value
            params_list.append(restored)
        
        return params_list
    except Exception as e:
        print(f"加载参数失败: {str(e)}")
        return None


# ====================== 工厂模式核心组件 ======================

@dataclass
class WidgetConfig:
    """部件配置类"""
    name: str
    display_name: str
    data_type: str  # "float", "int", "point", "string", "bool"
    default_value: Any = None
    required: bool = False
    unit: str = ""
    width: int = 15
    readonly: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class BaseWidget:
    """基础部件抽象类"""
    
    def __init__(self, parent, config: WidgetConfig, value=None, 
                 on_change: Optional[Callable] = None):
        self.parent = parent
        self.config = config
        self.value = value
        self.on_change = on_change
        self.frame = None
        self.widget = None
        self.var = None
        
    def create(self) -> tk.Widget:
        """创建部件，返回最外层容器"""
        raise NotImplementedError
    
    def get_value(self) -> Any:
        """获取值"""
        raise NotImplementedError
    
    def set_value(self, value: Any) -> None:
        """设置值"""
        raise NotImplementedError
    
    def is_valid(self) -> bool:
        """验证值是否有效"""
        return True
    
    def enable(self, enabled: bool = True) -> None:
        """启用/禁用部件"""
        if self.widget:
            state = "normal" if enabled else "disabled"
            try:
                self.widget.configure(state=state)
            except:
                # 某些部件可能不支持state参数
                pass


class FloatWidget(BaseWidget):
    """浮点数输入部件"""
    
    def create(self) -> tk.Widget:
        self.frame = ttk.Frame(self.parent)
        
        # 标签
        label = ttk.Label(
            self.frame, 
            text=self.config.display_name, 
            width=20, 
            anchor="e"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 输入框
        self.var = tk.StringVar(value=str(self.value) if self.value is not None else "")
        self.widget = ttk.Entry(
            self.frame, 
            width=self.config.width, 
            textvariable=self.var,
            state="readonly" if self.config.readonly else "normal"
        )
        self.widget.pack(side=tk.LEFT)
        
        # 单位标签
        if self.config.unit:
            ttk.Label(self.frame, text=self.config.unit).pack(side=tk.LEFT, padx=5)
        
        # 验证提示标签（初始隐藏）
        self.error_label = ttk.Label(
            self.frame, 
            text="", 
            foreground="red",
            font=("Arial", 9)
        )
        self.error_label.pack(side=tk.LEFT, padx=5)
        
        # 绑定变化事件
        if self.on_change and not self.config.readonly:
            self.var.trace_add("write", lambda *args: self._on_change())
        
        return self.frame
    
    def get_value(self) -> Optional[float]:
        try:
            text = self.var.get().strip()
            if not text:
                return None
            value = float(text)
            # 根据参数名称设置精度
            if self.config.name == "radius_tolerance":
                # 半径偏差精度设置为0.001
                return round(value, 4)  # 输入精度0.0001
            else:
                # 其他偏差精度设置为0.01
                return round(value, 3)  # 输入精度0.001
        except (ValueError, AttributeError):
            return None
    
    def set_value(self, value: Any) -> None:
        if value is None:
            self.var.set("")
        else:
            self.var.set(str(value))
    
    def is_valid(self) -> bool:
        value = self.get_value()
        
        if self.config.required and value is None:
            self.error_label.config(text="必填")
            return False
        
        if value is not None:
            if self.config.min_value is not None and value < self.config.min_value:
                self.error_label.config(text=f"不能小于{self.config.min_value}")
                return False
            if self.config.max_value is not None and value > self.config.max_value:
                self.error_label.config(text=f"不能大于{self.config.max_value}")
                return False
        
        self.error_label.config(text="")
        return True
    
    def _on_change(self):
        """内部变化处理"""
        self.is_valid()  # 验证输入
        if self.on_change:
            self.on_change(self.config.name, self.get_value())


class PointWidget(BaseWidget):
    """坐标点输入部件"""
    
    def create(self) -> tk.Widget:
        self.frame = ttk.Frame(self.parent)
        
        # 标签
        label = ttk.Label(
            self.frame, 
            text=self.config.display_name, 
            width=20, 
            anchor="e"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 坐标输入子框架
        subframe = ttk.Frame(self.frame)
        subframe.pack(side=tk.LEFT)
        
        # X坐标
        ttk.Label(subframe, text="X:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        x_entry = ttk.Entry(
            subframe, 
            width=8, 
            textvariable=self.x_var,
            state="readonly" if self.config.readonly else "normal"
        )
        x_entry.pack(side=tk.LEFT, padx=(2, 5))
        
        # Y坐标
        ttk.Label(subframe, text="Y:").pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        y_entry = ttk.Entry(
            subframe, 
            width=8, 
            textvariable=self.y_var,
            state="readonly" if self.config.readonly else "normal"
        )
        y_entry.pack(side=tk.LEFT, padx=(2, 0))
        
        # 设置初始值
        if isinstance(self.value, APoint):
            self.x_var.set(str(self.value.x))
            self.y_var.set(str(self.value.y))
        
        # 验证提示标签
        self.error_label = ttk.Label(
            self.frame, 
            text="", 
            foreground="red",
            font=("Arial", 9)
        )
        self.error_label.pack(side=tk.LEFT, padx=5)
        
        # 绑定变化事件
        if self.on_change and not self.config.readonly:
            self.x_var.trace_add("write", lambda *args: self._on_change())
            self.y_var.trace_add("write", lambda *args: self._on_change())
        
        return self.frame
    
    def get_value(self) -> Optional[APoint]:
        try:
            x_str = self.x_var.get().strip()
            y_str = self.y_var.get().strip()
            
            if not x_str or not y_str:
                return None
            
            return APoint(float(x_str), float(y_str))
        except (ValueError, AttributeError):
            return None
    
    def set_value(self, value: Any) -> None:
        if isinstance(value, APoint):
            self.x_var.set(str(value.x))
            self.y_var.set(str(value.y))
        else:
            self.x_var.set("")
            self.y_var.set("")
    
    def is_valid(self) -> bool:
        if self.config.required:
            try:
                x = float(self.x_var.get().strip())
                y = float(self.y_var.get().strip())
                self.error_label.config(text="")
                return True
            except ValueError:
                self.error_label.config(text="请输入有效坐标")
                return False
        return True
    
    def _on_change(self):
        """内部变化处理"""
        self.is_valid()  # 验证输入
        if self.on_change:
            self.on_change(self.config.name, self.get_value())


class WidgetFactory:
    """部件工厂类"""
    
    # 注册表：数据类型 -> 部件类
    _registry = {
        "float": FloatWidget,
        "int": FloatWidget,  # 暂时使用FloatWidget，可以专门实现IntWidget
        "point": PointWidget,
        "string": FloatWidget,  # 暂时使用FloatWidget
    }
    
    @classmethod
    def register(cls, data_type: str, widget_class):
        """注册新的部件类型"""
        cls._registry[data_type] = widget_class
    
    @classmethod
    def create(cls, parent, config: WidgetConfig, value=None, 
               on_change: Optional[Callable] = None) -> BaseWidget:
        """创建部件实例"""
        widget_class = cls._registry.get(config.data_type)
        if not widget_class:
            raise ValueError(f"未注册的数据类型: {config.data_type}")
        
        widget = widget_class(parent, config, value, on_change)
        widget.create()
        return widget
    
    @classmethod
    def create_multiple(cls, parent, configs: List[WidgetConfig], 
                        values: Dict[str, Any] = None,
                        on_change: Optional[Callable] = None) -> Dict[str, BaseWidget]:
        """批量创建部件"""
        widgets = {}
        for config in configs:
            value = values.get(config.name) if values else None
            widget = cls.create(parent, config, value, on_change)
            widgets[config.name] = widget
        return widgets


# ====================== 镜片参数配置 ======================

class LensParamConfigs:
    """镜片参数配置定义"""
    
    # 几何参数配置
    GEOMETRY_CONFIGS = [
        WidgetConfig(
            name="base",
            display_name="基准点",
            data_type="point",
            required=True
        ),
        WidgetConfig(
            name="outer_diameter",
            display_name="外径 (D)",
            data_type="float",
            unit="mm",
            required=True,
            min_value=0.1
        ),
        WidgetConfig(
            name="center_thickness",
            display_name="中心厚度",
            data_type="float",
            unit="mm",
            required=True,
            min_value=0.1
        ),
        WidgetConfig(
            name="edge_thickness",
            display_name="边缘厚度",
            data_type="float",
            unit="mm",
            min_value=0.1
        ),
    ]
    
    # 镜面1参数配置
    SURFACE1_CONFIGS = [
        WidgetConfig(
            name="radius1",
            display_name="镜面1半径 (R1)",
            data_type="float",
            unit="mm",
            required=True
        ),
        WidgetConfig(
            name="sagitta1",
            display_name="镜面1矢高",
            data_type="float",
            unit="mm"
        ),
        WidgetConfig(
            name="inner_diameter_S1",
            display_name="镜面1内径",
            data_type="float",
            unit="mm",
            min_value=0.1
        ),
    ]
    
    # 镜面2参数配置
    SURFACE2_CONFIGS = [
        WidgetConfig(
            name="radius2",
            display_name="镜面2半径 (R2)",
            data_type="float",
            unit="mm",
            required=True
        ),
        WidgetConfig(
            name="sagitta2",
            display_name="镜面2矢高",
            data_type="float",
            unit="mm"
        ),
        WidgetConfig(
            name="inner_diameter_S2",
            display_name="镜面2内径",
            data_type="float",
            unit="mm",
            min_value=0.1
        ),
    ]
    
    @classmethod
    def get_all_configs(cls) -> List[WidgetConfig]:
        """获取所有参数配置"""
        return (cls.GEOMETRY_CONFIGS + 
                cls.SURFACE1_CONFIGS + 
                cls.SURFACE2_CONFIGS +
                cls.TOLERANCE_CONFIGS)
    
    # 偏差参数配置
    TOLERANCE_CONFIGS = [
        # 极限偏差
        WidgetConfig(
            name="upper_tolerance",
            display_name="外径上偏差",
            data_type="float",
            unit="mm",
            default_value=0.0,
            min_value=-1.0,
            max_value=1.0
        ),
        WidgetConfig(
            name="lower_tolerance",
            display_name="外径下偏差",
            data_type="float",
            unit="mm",
            default_value=0.0,
            min_value=-1.0,
            max_value=1.0
        ),
        # 对称偏差
        WidgetConfig(
            name="thickness_tolerance",
            display_name="中心厚度偏差",
            data_type="float",
            unit="mm",
            default_value=0.02,
            min_value=0.0,
            max_value=1.0
        ),
        WidgetConfig(
            name="radius_tolerance",
            display_name="半径偏差",
            data_type="float",
            unit="mm",
            default_value=0.0,
            min_value=0.0,
            max_value=1.0
        ),
    ]
    
    @classmethod
    def get_all_configs(cls) -> List[WidgetConfig]:
        """获取所有参数配置"""
        return (cls.GEOMETRY_CONFIGS + 
                cls.SURFACE1_CONFIGS + 
                cls.SURFACE2_CONFIGS +
                cls.TOLERANCE_CONFIGS)
    
    @classmethod
    def get_config_groups(cls) -> Dict[str, List[WidgetConfig]]:
        """获取分组配置"""
        return {
            "几何参数": cls.GEOMETRY_CONFIGS,
            "镜面1参数": cls.SURFACE1_CONFIGS,
            "镜面2参数": cls.SURFACE2_CONFIGS,
            "偏差参数": cls.TOLERANCE_CONFIGS,
        }


# ====================== GUI主类（使用工厂模式重构） ======================

class LensParamsGUI:
    """使用工厂模式重构的镜片参数配置GUI"""
    
    def __init__(self, root: Optional[tk.Tk] = None, 
                 params_list: Optional[List[Dict[str, Any]]] = None):
        # 如果没有提供root，创建新的tk.Tk()实例
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.root.title("镜片参数配置工具（工厂模式版）")
        self.root.geometry("900x650")
        
        # 初始化参数
        if params_list is not None:
            self.params_list = params_list
            self.loaded_from_storage = False
        else:
            # 尝试从存储加载参数
            stored_params = load_params_from_storage()
            if stored_params:
                self.params_list = stored_params
                self.loaded_from_storage = True
                # 延迟显示提示，确保GUI已完全初始化
                self.root.after(100, lambda: messagebox.showinfo("参数加载", "已加载上次保存的参数配置"))
            else:
                self.params_list = []
                self.loaded_from_storage = False
        
        self.selected_indices = []
        self.result_params = []
        self.confirmed = False
        
        # 部件存储：param_index -> {param_name -> widget}
        self.param_widgets = {}
        
        # 创建主界面
        self._setup_styles()
        self._create_main_ui()
        
    def _setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="blue", font=("Arial", 10, "bold"))
        style.configure("Group.TLabelframe", padding=10)
        style.configure("Group.TLabelframe.Label", font=("Arial", 10, "bold"))
    
    def _create_main_ui(self):
        """创建主界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个部分
        self._create_selection_section(main_frame)
        self._create_editor_section(main_frame)
        self._create_button_section(main_frame)
        self._create_status_bar(main_frame)
        
        # 初始状态
        self._update_status()
    
    def _create_selection_section(self, parent):
        """创建参数组选择区域"""
        frame = ttk.LabelFrame(parent, text="选择参数组 (最多3个)", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择区域容器
        self.selection_frame = ttk.Frame(frame)
        self.selection_frame.pack(fill=tk.X)
        
        # 存储复选框变量
        self.check_vars = []
        
        # 初始化选择显示
        self._update_selection_display()
    
    def _update_selection_display(self):
        """更新选择区域显示"""
        # 清空现有内容
        for widget in self.selection_frame.winfo_children():
            widget.destroy()
        
        self.check_vars.clear()
        
        if not self.params_list:
            # 显示空状态
            label = ttk.Label(
                self.selection_frame, 
                text="暂无参数组，请添加参数", 
                font=("Arial", 10, "italic"),
                foreground="gray"
            )
            label.pack(pady=5)
            return
        
        # 创建复选框
        for i, params in enumerate(self.params_list):
            var = tk.BooleanVar(value=i in self.selected_indices)
            self.check_vars.append(var)
            
            # 创建复选框
            chk = ttk.Checkbutton(
                self.selection_frame,
                text=self._format_param_summary(i, params),
                variable=var,
                command=lambda idx=i: self._on_selection_change(idx)
            )
            chk.pack(side=tk.LEFT, padx=10, anchor=tk.W)
    
    def _format_param_summary(self, index: int, params: Dict[str, Any]) -> str:
        """格式化参数组摘要"""
        r1 = params.get('radius1', 'N/A')
        r2 = params.get('radius2', 'N/A')
        d = params.get('outer_diameter', 'N/A')
        tc = params.get('center_thickness', 'N/A')
        return f"参数组 {index+1}: R1={r1}, R2={r2}, D={d}, Tc={tc}"
    
    def _create_editor_section(self, parent):
        """创建编辑器区域"""
        frame = ttk.LabelFrame(parent, text="编辑参数", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Notebook
        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建初始提示页
        self._create_prompt_page()
    
    def _create_prompt_page(self):
        """创建提示页"""
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="提示")
        
        label = ttk.Label(
            page, 
            text="请在上方选择要编辑的参数组", 
            font=("Arial", 12),
            foreground="gray"
        )
        label.pack(expand=True)
    
    def _create_button_section(self, parent):
        """创建按钮区域"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用工厂方法创建按钮
        buttons = [
            ("添加参数组", self._on_add_group, "left", ""),
            ("重置选择", self._on_reset, "left", ""),
            ("开始绘制", self._on_confirm, "right", "Accent.TButton"),
        ]
        
        for text, command, side, style in buttons:
            self._create_button(frame, text, command, style).pack(side=side, padx=5)
    
    def _create_button(self, parent, text: str, command: Callable, 
                       style: str = "") -> ttk.Button:
        """创建按钮的工厂方法"""
        return ttk.Button(
            parent,
            text=text,
            width=15,
            command=command,
            style=style if style else None
        )
    
    def _create_status_bar(self, parent):
        """创建状态栏"""
        self.status_var = tk.StringVar(value="就绪 - 请选择1-3个参数组")
        status_bar = ttk.Label(
            parent, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def _on_selection_change(self, index: int):
        """处理选择变化"""
        var = self.check_vars[index]
        
        if var.get():
            # 尝试添加到选中列表
            if len(self.selected_indices) >= 3:
                var.set(False)
                messagebox.showwarning("提示", "最多只能选择3个参数组")
                return
            if index not in self.selected_indices:
                self.selected_indices.append(index)
        else:
            # 从选中列表中移除
            if index in self.selected_indices:
                self.selected_indices.remove(index)
        
        # 更新UI
        self._update_selection_display()
        self._update_editor_tabs()
        self._update_status()
    
    def _update_editor_tabs(self):
        """更新编辑器标签页"""
        # 清除非提示页
        for tab_id in self.notebook.tabs():
            if tab_id != str(self.notebook.children["!frame"]):
                self.notebook.forget(tab_id)
        
        # 清空部件存储
        self.param_widgets.clear()
        
        # 为每个选中的参数组创建标签页
        for idx in self.selected_indices:
            self._create_param_tab(idx)
    
    def _create_param_tab(self, param_index: int):
        """创建参数标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"参数组 {param_index+1}")
        
        # 创建滚动区域
        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        content_frame = ttk.Frame(canvas)
        
        # 配置滚动
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 获取当前参数值
        current_params = self.params_list[param_index]
        
        # 初始化当前组的部件存储
        self.param_widgets[param_index] = {}
        
        # 使用工厂创建参数部件
        row = 0
        config_groups = LensParamConfigs.get_config_groups()
        
        for group_name, configs in config_groups.items():
            # 创建分组框架
            group_frame = ttk.LabelFrame(
                content_frame, 
                text=group_name,
                padding="10"
            )
            group_frame.grid(
                row=row, 
                column=0, 
                columnspan=2, 
                sticky="ew", 
                padx=5, 
                pady=5
            )
            
            # 为组内的每个参数创建部件
            for config in configs:
                # 获取当前值
                value = current_params.get(config.name)
                
                # 使用工厂创建部件
                widget = WidgetFactory.create(
                    parent=group_frame,
                    config=config,
                    value=value,
                    on_change=lambda name=config.name, val=value: 
                        self._on_param_change(param_index, name, val)
                )
                
                # 布局部件
                widget.frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
                group_frame.grid_columnconfigure(0, weight=1)
                
                # 存储部件引用
                self.param_widgets[param_index][config.name] = widget
                row += 1
            
            row += 1
        
        # 布局canvas和滚动条
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
    
    def _on_param_change(self, param_index: int, param_name: str, value: Any):
        """参数变化回调"""
        # 获取部件
        widget = self.param_widgets[param_index].get(param_name)
        if not widget:
            return
        
        # 验证值
        if not widget.is_valid():
            return
        
        # 更新参数值
        new_value = widget.get_value()
        self.params_list[param_index][param_name] = new_value
        
        # R1和R2参数同步功能
        if param_name in ["radius1", "radius2"]:
            self._sync_radius_values(param_name, new_value, param_index)
        
        # 更新选择区域显示
        self._update_selection_display()
        
        # 可以在这里添加图形重绘逻辑
        # self._redraw_graphics(param_index)
    
    def _sync_radius_values(self, param_name: str, new_value: Any, source_index: int):
        """同步R1和R2参数到所有参数组
        
        参数:
            param_name: 参数名称（"radius1" 或 "radius2"）
            new_value: 新的参数值
            source_index: 源参数组索引
        """
        # 边界条件处理：空值或非法值不进行同步
        if new_value is None or not isinstance(new_value, (int, float)):
            return
        
        # 遍历所有参数组，同步参数值
        for idx in range(len(self.params_list)):
            # 跳过源参数组，避免重复更新
            if idx == source_index:
                continue
            
            # 获取目标参数组的部件
            target_widget = self.param_widgets.get(idx, {}).get(param_name)
            
            # 如果目标部件存在且不是只读状态，则更新值
            if target_widget and not target_widget.config.readonly:
                try:
                    # 更新参数值
                    self.params_list[idx][param_name] = new_value
                    
                    # 更新部件显示
                    target_widget.set_value(new_value)
                    
                    # 验证更新后的值
                    target_widget.is_valid()
                    
                except Exception as e:
                    # 捕获同步过程中的异常，避免影响其他参数组
                    print(f"同步参数 {param_name} 到参数组 {idx+1} 失败: {str(e)}")
    
    def _update_status(self):
        """更新状态栏"""
        if not self.params_list:
            self.status_var.set("就绪 - 请添加参数组")
        elif not self.selected_indices:
            self.status_var.set("就绪 - 请选择1-3个参数组")
        else:
            count = len(self.selected_indices)
            self.status_var.set(f"已选择 {count} 个参数组，可在下方编辑参数")
    
    def _on_add_group(self):
        """添加新的参数组"""
        # 创建默认参数组
        default_params = {
            "base": APoint(0, 0),
            "radius1": 50.0,
            "radius2": -50.0,
            "outer_diameter": 60.0,
            "center_thickness": 5.0,
            "edge_thickness": None,
            "sagitta1": None,
            "sagitta2": None,
            "inner_diameter_S1": None,
            "inner_diameter_S2": None,
        }
        
        self.params_list.append(default_params)
        self._update_selection_display()
        self._update_status()
        
        messagebox.showinfo("提示", f"已添加参数组 {len(self.params_list)}")
    
    def _on_reset(self):
        """重置选择"""
        # 重置选择状态
        self.selected_indices.clear()
        
        # 重置复选框
        for var in self.check_vars:
            var.set(False)
        
        # 重置部件存储
        self.param_widgets.clear()
        
        # 更新UI
        self._update_selection_display()
        self._update_editor_tabs()
        self._update_status()
        
        # 重置结果
        self.result_params.clear()
        self.confirmed = False
    
    def _validate_all(self) -> bool:
        """验证所有输入"""
        for param_index in self.selected_indices:
            widgets = self.param_widgets.get(param_index, {})
            for param_name, widget in widgets.items():
                if not widget.is_valid():
                    messagebox.showerror(
                        "输入错误",
                        f"参数组 {param_index+1} 的 {widget.config.display_name} 输入无效"
                    )
                    return False
        return True
    
    def _on_confirm(self):
        """确认按钮点击事件"""
        if not self.params_list:
            messagebox.showwarning("提示", "请先添加参数组")
            return
        
        if not self.selected_indices:
            messagebox.showwarning("提示", "请至少选择一个参数组")
            return
        
        # 验证所有输入
        if not self._validate_all():
            return
        
        # 收集结果
        self.result_params.clear()
        for idx in self.selected_indices:
            params = {}
            widgets = self.param_widgets.get(idx, {})
            
            for param_name, widget in widgets.items():
                params[param_name] = widget.get_value()
            
            self.result_params.append(params)
        
        # 标记为已确认
        self.confirmed = True
        messagebox.showinfo("成功", f"已确认 {len(self.result_params)} 个参数组")
        
        # 自动保存参数到存储
        if save_params_to_storage(self.params_list):
            print("参数已自动保存到本地存储")
        
        # 关闭窗口，继续执行绘图程序
        self.root.destroy()
    
    def run(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """运行GUI"""
        self.root.mainloop()
        return self.confirmed, self.result_params


# ====================== 使用示例 ======================

def main():
    """主函数"""
    # 示例参数列表
    example_params = [
        {
            "base": APoint(0, 0),
            "radius1": 50.0,
            "radius2": -50.0,
            "outer_diameter": 60.0,
            "center_thickness": 5.0,
        },
        {
            "base": APoint(100, 0),
            "radius1": 30.0,
            "radius2": -40.0,
            "outer_diameter": 50.0,
            "center_thickness": 4.0,
            "edge_thickness": 3.0,
        },
    ]
    
    # 创建并运行GUI
    root = tk.Tk()
    app = LensParamsGUI(root, example_params)
    confirmed, results = app.run()
    
    # 输出结果
    if confirmed:
        print("配置成功，获取的参数:")
        for i, params in enumerate(results):
            print(f"\n参数组 {i+1}:")
            for key, value in params.items():
                if isinstance(value, APoint):
                    print(f"  {key}: ({value.x}, {value.y})")
                else:
                    print(f"  {key}: {value}")
    else:
        print("配置已取消")

def configure_params_gui(params_list=None):
    """
    运行参数配置GUI
    
    参数:
        params_list: 可选的参数列表
    
    返回:
        tuple: (是否确认, 配置的参数列表)
    """
    try:
        # 创建主窗口
        root = tk.Tk()
        # 创建应用实例
        app = LensParamsGUI(root, params_list)
        # 运行GUI
        return app.run()
    except Exception as e:
        # 错误处理
        print(f"GUI初始化失败: {str(e)}")
        return False, []


if __name__ == "__main__":
    main()