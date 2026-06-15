import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# 路径配置 - 必须在导入本地模块之前设置
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.com_interface import APoint

NUM_LENSES = 4

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

LENS4_EXTRA_FIELDS = [
    ("outer_diameter_min", "最小外径 (mm):", ""),
    ("outer_diameter_min_upper_tolerance", "最小外径上偏差 (+mm):", ""),
    ("outer_diameter_min_lower_tolerance", "最小外径下偏差 (-mm):", ""),
    ("Minsagitta1", "最小矢高1 (mm):", ""),
    ("Minsagitta2", "最小矢高2 (mm):", ""),
]

ALL_FIELDS = FIRST_SURFACE_FIELDS + SECOND_SURFACE_FIELDS + THICKNESS_FIELDS + DIAMETER_FIELDS

SYNC_CATEGORIES = [
    ("radius", "半径参数同步", ["radius1", "radius2"], [True, True, True, True]),
    ("center_thickness", "中心厚度同步", ["center_thickness"], [False, True, True, True]),
    ("thickness_tolerance", "厚度公差同步", ["thickness_tolerance"], [True, True, True, True]),
    ("sagitta", "矢高同步", ["sagitta1", "sagitta2"], [False, False, False, False]),
    ("sagitta_tolerance", "矢高公差同步", ["sagitta1_tolerance", "sagitta2_tolerance"], [False, False, False, False]),
]

DATA_FILE = os.path.join(os.path.dirname(__file__), "lens_gui_data.json")


class LensParamsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("镜片参数配置")
        self.root.geometry("880x780")

        self.entries = {}
        self.lens_selection = {i: True for i in range(1, NUM_LENSES + 1)}
        self.lens_check_vars = {}
        self.sync_vars = {}
        self._syncing = False

        self._init_sync_vars()
        self.create_widgets()
        self.load_data()
        self._bind_events()

    def _init_sync_vars(self):
        for cat_id, _, _, defaults in SYNC_CATEGORIES:
            self.sync_vars[cat_id] = {
                i + 1: tk.BooleanVar(value=defaults[i]) for i in range(NUM_LENSES)
            }

    def _field_to_category(self, field):
        for cat_id, _, fields, _ in SYNC_CATEGORIES:
            if field in fields:
                return cat_id
        return None

    def _is_synced(self, cat_id, lens_num):
        return self.sync_vars.get(cat_id, {}).get(lens_num, tk.BooleanVar(value=False)).get()

    def _sync_field(self, cat_id, source_lens, field):
        if self._syncing:
            return
        if not self._is_synced(cat_id, source_lens):
            return
        self._syncing = True
        try:
            value = self.entries[f"lens{source_lens}_{field}"].get()
            for lens in range(1, NUM_LENSES + 1):
                if lens != source_lens and self._is_synced(cat_id, lens):
                    entry = self.entries[f"lens{lens}_{field}"]
                    entry.delete(0, tk.END)
                    entry.insert(0, value)
        finally:
            self._syncing = False

    def _on_field_change(self, source_lens, field):
        cat_id = self._field_to_category(field)
        if cat_id:
            self._sync_field(cat_id, source_lens, field)

    def _make_field_callback(self, lens, field):
        def callback(event):
            self._on_field_change(lens, field)
        return callback

    def _bind_events(self):
        for lens in range(1, NUM_LENSES + 1):
            for cat_id, _, fields, _ in SYNC_CATEGORIES:
                for field in fields:
                    key = f"lens{lens}_{field}"
                    entry = self.entries.get(key)
                    if entry:
                        entry.bind("<KeyRelease>", self._make_field_callback(lens, field))

    # ── UI Creation ──────────────────────────────────────────────

    def create_widgets(self):
        main = ttk.Frame(self.root, padding="12")
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        ttk.Label(main, text="镜片参数配置", font=("Microsoft YaHei UI", 13, "bold")).grid(
            row=0, column=0, pady=(0, 8)
        )

        self._create_notebook(main)
        self._create_draw_section(main)
        self._create_sync_section(main)
        self._create_buttons(main)

    def _create_notebook(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, pady=(0, 8), sticky="nsew")
        parent.rowconfigure(1, weight=1)

        for i in range(1, NUM_LENSES + 1):
            tab = self._create_lens_tab(notebook, i)
            notebook.add(tab, text=f"镜片 {i}")

    def _create_lens_tab(self, parent, lens_num):
        tab = ttk.Frame(parent, padding="8")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        first_frame = ttk.LabelFrame(tab, text="第一面参数", padding="6")
        first_frame.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        first_frame.columnconfigure(1, weight=1)
        for r, (fid, label, default) in enumerate(FIRST_SURFACE_FIELDS):
            ttk.Label(first_frame, text=label, font=("Microsoft YaHei UI", 9)).grid(
                row=r, column=0, sticky="w", padx=(0, 6), pady=3
            )
            entry = ttk.Entry(first_frame, width=14, font=("Consolas", 10))
            entry.insert(0, default)
            entry.grid(row=r, column=1, sticky="ew", pady=3)
            self.entries[f"lens{lens_num}_{fid}"] = entry

        second_frame = ttk.LabelFrame(tab, text="第二面参数", padding="6")
        second_frame.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        second_frame.columnconfigure(1, weight=1)
        for r, (fid, label, default) in enumerate(SECOND_SURFACE_FIELDS):
            ttk.Label(second_frame, text=label, font=("Microsoft YaHei UI", 9)).grid(
                row=r, column=0, sticky="w", padx=(0, 6), pady=3
            )
            entry = ttk.Entry(second_frame, width=14, font=("Consolas", 10))
            entry.insert(0, default)
            entry.grid(row=r, column=1, sticky="ew", pady=3)
            self.entries[f"lens{lens_num}_{fid}"] = entry

        thickness_frame = ttk.LabelFrame(tab, text="厚度参数", padding="6")
        thickness_frame.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        thickness_frame.columnconfigure(1, weight=1)
        for r, (fid, label, default) in enumerate(THICKNESS_FIELDS):
            ttk.Label(thickness_frame, text=label, font=("Microsoft YaHei UI", 9)).grid(
                row=r, column=0, sticky="w", padx=(0, 6), pady=3
            )
            entry = ttk.Entry(thickness_frame, width=14, font=("Consolas", 10))
            entry.insert(0, default)
            entry.grid(row=r, column=1, sticky="ew", pady=3)
            self.entries[f"lens{lens_num}_{fid}"] = entry

        diameter_frame = ttk.LabelFrame(tab, text="外径参数", padding="6")
        diameter_frame.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        diameter_frame.columnconfigure(1, weight=1)
        for r, (fid, label, default) in enumerate(DIAMETER_FIELDS):
            ttk.Label(diameter_frame, text=label, font=("Microsoft YaHei UI", 9)).grid(
                row=r, column=0, sticky="w", padx=(0, 6), pady=3
            )
            entry = ttk.Entry(diameter_frame, width=14, font=("Consolas", 10))
            entry.insert(0, default)
            entry.grid(row=r, column=1, sticky="ew", pady=3)
            self.entries[f"lens{lens_num}_{fid}"] = entry

        if lens_num == 4:
            extra_frame = ttk.LabelFrame(tab, text="最小尺寸参数", padding="6")
            extra_frame.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
            extra_frame.columnconfigure(1, weight=1)
            extra_frame.columnconfigure(3, weight=1)
            extra_frame.columnconfigure(5, weight=1)
            for r, (fid, label, default) in enumerate(LENS4_EXTRA_FIELDS):
                col = r % 3 * 2
                row = r // 3
                ttk.Label(extra_frame, text=label, font=("Microsoft YaHei UI", 9)).grid(
                    row=row, column=col, sticky="w", padx=(0, 6), pady=3
                )
                entry = ttk.Entry(extra_frame, width=12, font=("Consolas", 10))
                entry.insert(0, default)
                entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 20), pady=3)
                self.entries[f"lens{lens_num}_{fid}"] = entry

        return tab

    def _create_draw_section(self, parent):
        frame = ttk.LabelFrame(parent, text="绘图镜片选择", padding="8")
        frame.grid(row=2, column=0, pady=(0, 6), sticky="ew")

        for i in range(1, NUM_LENSES + 1):
            frame.columnconfigure(i - 1, weight=1)
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(frame, text=f"镜片 {i}", variable=var,
                                 command=lambda idx=i: self._on_lens_selection(idx))
            cb.grid(row=0, column=i - 1, padx=8)
            self.lens_check_vars[i] = var

    def _create_sync_section(self, parent):
        frame = ttk.LabelFrame(parent, text="参数同步设置", padding="8")
        frame.grid(row=3, column=0, pady=(0, 6), sticky="ew")

        ttk.Label(frame, text="", width=14).grid(row=0, column=0)
        for i in range(NUM_LENSES):
            ttk.Label(frame, text=f"镜片{i+1}", font=("Microsoft YaHei UI", 9, "bold"),
                      anchor="center", width=7).grid(row=0, column=i + 1)

        for r, (cat_id, label, _, _) in enumerate(SYNC_CATEGORIES):
            ttk.Label(frame, text=label + ":", font=("Microsoft YaHei UI", 9)).grid(
                row=r + 1, column=0, sticky="e", padx=(0, 8), pady=2
            )
            for c in range(NUM_LENSES):
                lens = c + 1
                cb = ttk.Checkbutton(frame, variable=self.sync_vars[cat_id][lens])
                cb.grid(row=r + 1, column=c + 1, pady=2)

    def _create_buttons(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=4, column=0, pady=(6, 0))
        ttk.Button(frame, text="开始绘图", command=self.start, width=14).pack(side=tk.LEFT, padx=8)
        ttk.Button(frame, text="重置", command=self.reset, width=14).pack(side=tk.LEFT, padx=8)

    def _on_lens_selection(self, lens_num):
        self.lens_selection[lens_num] = self.lens_check_vars[lens_num].get()

    # ── Core Logic ───────────────────────────────────────────────

    def get_params(self, lens_num):
        params = {}
        for fid, _, _ in ALL_FIELDS:
            key = f"lens{lens_num}_{fid}"
            value = self.entries[key].get().strip()
            if not value:
                if fid in ("sagitta1", "sagitta2") or fid.endswith("_tolerance"):
                    params[fid] = None
                else:
                    raise ValueError(f"镜片{lens_num}的{fid}参数不能为空")
            else:
                params[fid] = float(value)

        if params.get("sagitta1") is not None:
            if params.get("sagitta1_tolerance") is None:
                params["sagitta1_tolerance"] = 0.02
        if params.get("sagitta2") is not None:
            if params.get("sagitta2_tolerance") is None:
                params["sagitta2_tolerance"] = 0.02

        if params.get("outer_diameter", 0) <= 0:
            return None

        if lens_num == 4:
            for fid, _, _ in LENS4_EXTRA_FIELDS:
                key = f"lens{lens_num}_{fid}"
                value = self.entries[key].get().strip()
                if not value:
                    params[fid] = None
                else:
                    params[fid] = float(value)
            if params.get("outer_diameter_min") is None:
                params["Minsagitta1"] = None
                params["Minsagitta2"] = None

        return params

    def start(self):
        base_x, base_y = 0.0, 0.0
        spacing = 50.0
        self.params_list = []
        current_x = base_x

        for lens_num in range(1, NUM_LENSES + 1):
            if not self.lens_selection.get(lens_num, False):
                continue
            try:
                params = self.get_params(lens_num)
                if params:
                    params["base"] = APoint(current_x, base_y)
                    self.params_list.append(params)
                    current_x += 2 * params["outer_diameter"] + spacing
            except ValueError as e:
                messagebox.showerror("参数错误", str(e))
                continue

        if not self.params_list:
            messagebox.showwarning("警告", "没有有效的镜片参数")
            return

        try:
            from draw_lens import draw_multiple_lenses
            success, warnings = draw_multiple_lenses(self.params_list)
            if success:
                self.save_data()
                for w in warnings:
                    messagebox.showwarning("矢高警告", w)
            else:
                messagebox.showerror("错误", "绘图失败")
        except ImportError:
            messagebox.showerror("导入错误", "无法导入绘图模块")
        except Exception as e:
            messagebox.showerror("错误", f"绘图错误: {str(e)}")

    def reset(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for lens_num in range(1, NUM_LENSES + 1):
            for fid, _, default in ALL_FIELDS:
                key = f"lens{lens_num}_{fid}"
                if key in self.entries and default:
                    self.entries[key].insert(0, default)
            if lens_num == 4:
                for fid, _, default in LENS4_EXTRA_FIELDS:
                    key = f"lens{lens_num}_{fid}"
                    if key in self.entries and default:
                        self.entries[key].insert(0, default)
        for lens_num in range(1, NUM_LENSES + 1):
            self.lens_check_vars[lens_num].set(True)
            self.lens_selection[lens_num] = True

    # ── Persistence ──────────────────────────────────────────────

    def save_data(self):
        try:
            data = {
                "lens_selection": {str(i): self.lens_selection[i] for i in range(1, NUM_LENSES + 1)},
                "sync_config": {
                    cat_id: {str(i): self.sync_vars[cat_id][i].get() for i in range(1, NUM_LENSES + 1)}
                    for cat_id, _, _, _ in SYNC_CATEGORIES
                },
                "lens_data": {
                    f"lens{i}": {
                        fid: self.entries[f"lens{i}_{fid}"].get()
                        for fid, _, _ in (ALL_FIELDS + (LENS4_EXTRA_FIELDS if i == 4 else []))
                        if f"lens{i}_{fid}" in self.entries
                    }
                    for i in range(1, NUM_LENSES + 1)
                },
            }
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def load_data(self):
        try:
            if not os.path.exists(DATA_FILE):
                return
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "lens_selection" in data:
                for k, v in data["lens_selection"].items():
                    n = int(k)
                    if n in self.lens_check_vars:
                        self.lens_check_vars[n].set(v)
                        self.lens_selection[n] = v

            if "lens_data" in data:
                for i in range(1, NUM_LENSES + 1):
                    lens_key = f"lens{i}"
                    if lens_key in data["lens_data"]:
                        for fid, value in data["lens_data"][lens_key].items():
                            entry_key = f"lens{i}_{fid}"
                            if entry_key in self.entries:
                                self.entries[entry_key].delete(0, tk.END)
                                self.entries[entry_key].insert(0, value)

            if "sync_config" in data:
                for cat_id, cfg in data["sync_config"].items():
                    if cat_id in self.sync_vars:
                        for k, v in cfg.items():
                            n = int(k)
                            if n in self.sync_vars[cat_id]:
                                self.sync_vars[cat_id][n].set(v)
        except Exception as e:
            print(f"加载数据失败: {e}")

    def on_closing(self):
        self.save_data()
        self.root.quit()


def main():
    root = tk.Tk()
    app = LensParamsGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
