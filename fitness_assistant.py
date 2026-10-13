# -*- coding: utf-8 -*-
"""
健身记录助手 —— 一个运行在 Windows 上的本地健身记录软件。
训练记录保存在“训练记录.txt”，体重记录保存在“体重记录.txt”，动作库保存在“动作库.txt”。
"""
import os
import sys
from datetime import datetime, date
from dataclasses import dataclass

import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "健身记录助手"
DATA_FILENAME = "训练记录.txt"
WEIGHT_FILENAME = "体重记录.txt"
ACTION_LIB_FILENAME = "动作库.txt"
SEP = " | "

# —— 淡蓝色主题配色 ——
BG = "#EAF4FB"
BG_PANEL = "#D9EAF7"
CARD = "#FFFFFF"
BORDER = "#D7E7F3"
ACCENT = "#3D9BE9"
ACCENT_DARK = "#2E82C8"
ACCENT_DEEP = "#1F6EB3"
TEXT = "#1F3A4D"
HINT = "#7A96A8"
OK_GREEN = "#2E8B57"
ERR_RED = "#C0392B"
GOLD = "#F0A500"
ROW_A = "#FFFFFF"
ROW_B = "#EAF5FC"

FONT = ("Microsoft YaHei UI", 10)
FONT_SMALL = ("Microsoft YaHei UI", 9)
FONT_BIG = ("Microsoft YaHei UI", 12)
FONT_HEAD = ("Microsoft YaHei UI", 14, "bold")
FONT_CARD_NUM = ("Microsoft YaHei UI", 24, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 22, "bold")

# —— 常用动作预设 ——
DEFAULT_ACTIONS = [
    "卧推", "上斜卧推", "哑铃卧推", "深蹲", "硬拉", "引体向上", "高位下拉",
    "杠铃划船", "坐姿划船", "实力推举", "哑铃侧平举", "二头弯举", "三头下压",
    "腿举", "腿弯举", "箭步蹲", "俯卧撑", "平板支撑", "卷腹", "跑步", "椭圆机",
]

# —— 动作 → 训练部位（用于训练间隔提示）——
MUSCLE_GROUPS = {
    "卧推": ["胸"], "上斜卧推": ["胸"], "哑铃卧推": ["胸"], "俯卧撑": ["胸"], "夹胸": ["胸"],
    "硬拉": ["背", "腿"],
    "引体向上": ["背"], "高位下拉": ["背"], "杠铃划船": ["背"], "坐姿划船": ["背"],
    "深蹲": ["腿"], "腿举": ["腿"], "腿弯举": ["腿"], "箭步蹲": ["腿"],
    "实力推举": ["肩"], "哑铃侧平举": ["肩"],
    "二头弯举": ["臂"], "三头下压": ["臂"],
    "平板支撑": ["核心"], "卷腹": ["核心"],
    "跑步": ["有氧"], "椭圆机": ["有氧"],
}

# —— 推拉腿（Push-Pull-Legs）三分化训练模板 ——
PPL_PLAN = {
    "推日（胸·肩·三头）": [
        ("卧推", "4", "8"),
        ("上斜卧推", "4", "10"),
        ("实力推举", "3", "8"),
        ("哑铃侧平举", "3", "12"),
        ("三头下压", "3", "12"),
    ],
    "拉日（背·二头）": [
        ("硬拉", "3", "5"),
        ("引体向上", "4", "8"),
        ("杠铃划船", "4", "10"),
        ("高位下拉", "3", "10"),
        ("二头弯举", "3", "12"),
    ],
    "腿日（腿·核心）": [
        ("深蹲", "4", "8"),
        ("腿举", "4", "10"),
        ("腿弯举", "3", "12"),
        ("箭步蹲", "3", "10"),
        ("卷腹", "3", "15"),
    ],
}

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


@dataclass
class Record:
    date: str
    action: str
    sets: str
    weight: str
    reps: str
    note: str


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_data_path():
    return os.path.join(get_base_dir(), DATA_FILENAME)


def get_weight_path():
    return os.path.join(get_base_dir(), WEIGHT_FILENAME)


def get_action_lib_path():
    return os.path.join(get_base_dir(), ACTION_LIB_FILENAME)

def load_records(path):
    records = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            parts = line.split("|", 5)
            if len(parts) < 6:
                continue
            date, action, sets, weight, reps, note = [p.strip() for p in parts[:6]]
            if not date or not action:
                continue
            records.append(Record(date, action, sets, weight, reps, note))
    return records


def save_records(path, records):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("# 健身记录助手数据文件（请用本软件修改，不要手动改动格式）\n")
        f.write("# 格式：日期 | 动作 | 组数 | 重量(kg) | 次数 | 备注\n")
        for r in records:
            f.write(f"{r.date}{SEP}{r.action}{SEP}{r.sets}{SEP}{r.weight}{SEP}{r.reps}{SEP}{r.note}\n")


def load_weights(path):
    items = []
    if not os.path.exists(path):
        return items
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue
            d, w = parts[0], parts[1]
            if not is_valid_date(d):
                continue
            try:
                float(w)
            except ValueError:
                continue
            items.append((d, w))
    return items


def save_weights(path, items):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("# 体重记录（日期 | 体重kg）\n")
        for d, w in items:
            f.write("%s | %s\n" % (d, w))


def load_action_lib(path):
    if not os.path.exists(path):
        save_action_lib(path, list(DEFAULT_ACTIONS))
        return list(DEFAULT_ACTIONS)
    items = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\r\n").strip()
            if not line or line.startswith("#"):
                continue
            if line not in items:
                items.append(line)
    for a in DEFAULT_ACTIONS:
        if a not in items:
            items.append(a)
    return items


def save_action_lib(path, items):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write("# 动作库（每行一个动作）\n")
        for a in items:
            f.write(a + "\n")


# —— 校验与统计 ——
def is_valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_positive_int(s):
    s = s.strip()
    if not s.isdigit():
        return None
    v = int(s)
    return v if v > 0 else None


def parse_float(s):
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_weight(s):
    s = s.strip()
    if s == "":
        return "", True
    v = parse_float(s)
    if v is None:
        return None, False
    return s, v > 0


def month_key(datestr):
    return datestr[:7]


def count_workouts_this_month(records, today=None):
    today = today or datetime.now()
    key = "%04d-%02d" % (today.year, today.month)
    return len({r.date for r in records if r.date and month_key(r.date) == key})


def action_names(records):
    return sorted({r.action for r in records if r.action})


def action_pr(records, action):
    weights = []
    for r in records:
        if r.action == action:
            w = parse_float(r.weight)
            if w is not None and w > 0:
                weights.append(w)
    return max(weights) if weights else None


def volume_by_action(records):
    d = {}
    for r in records:
        d.setdefault(r.action, 0.0)
        w = parse_float(r.weight)
        s = parse_positive_int(r.sets)
        n = parse_positive_int(r.reps)
        if w and w > 0 and s and n:
            d[r.action] += w * s * n
    return d


def groups_of(action):
    return MUSCLE_GROUPS.get(action, [])


def last_training_by_group(records, today=None):
    today = today or datetime.now().date()
    group_last = {}
    for r in records:
        try:
            d = datetime.strptime(r.date, "%Y-%m-%d").date()
        except ValueError:
            continue
        for g in groups_of(r.action):
            if g not in group_last or d > group_last[g]:
                group_last[g] = d
    return {g: (today - d).days for g, d in group_last.items()}


def weight_trend(records, action):
    d = {}
    for r in records:
        if r.action != action:
            continue
        w = parse_float(r.weight)
        if w is None or w <= 0:
            continue
        if r.date not in d or w > d[r.date]:
            d[r.date] = w
    return sorted([(k, v) for k, v in d.items()])


def fmt_weight(v):
    if v is None:
        return ""
    if float(v).is_integer():
        return str(int(v))
    return "%.1f" % v

def draw_line_chart(canvas, points):
    c = canvas
    c.delete("all")
    w = c.winfo_width()
    h = c.winfo_height()
    if w < 80 or h < 80:
        w, h = 560, 240
    if not points:
        c.create_text(w / 2, h / 2, text="暂无数据", fill=HINT, font=FONT_BIG)
        return
    pts = []
    for d, v in points:
        try:
            dd = datetime.strptime(d, "%Y-%m-%d")
            fv = float(v)
        except (ValueError, TypeError):
            continue
        pts.append((dd, fv))
    if not pts:
        return
    pts.sort(key=lambda p: p[0])
    vals = [p[1] for p in pts]
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-6:
        lo -= 1
        hi += 1
    pad_l, pad_r, pad_t, pad_b = 48, 18, 18, 34
    n = len(pts)

    def x_of(i):
        return pad_l + (w - pad_l - pad_r) * (i / (n - 1) if n > 1 else 0.5)

    def y_of(v):
        return pad_t + (h - pad_t - pad_b) * (1 - (v - lo) / (hi - lo))

    for k in range(5):
        v = lo + (hi - lo) * k / 4
        y = y_of(v)
        c.create_line(pad_l, y, w - pad_r, y, fill="#EAF0F4")
        c.create_text(pad_l - 8, y, text="%.1f" % v, anchor="e", fill=HINT, font=FONT_SMALL)
    c.create_text(x_of(0), h - pad_b + 16, text=pts[0][0].strftime("%m-%d"), anchor="n", fill=HINT, font=FONT_SMALL)
    if n > 1:
        c.create_text(x_of(n - 1), h - pad_b + 16, text=pts[-1][0].strftime("%m-%d"), anchor="n", fill=HINT, font=FONT_SMALL)
    coords = []
    for i in range(n):
        coords.extend([x_of(i), y_of(vals[i])])
    if n > 1:
        c.create_line(*coords, fill=ACCENT, width=2, smooth=True)
    for i in range(n):
        cx, cy = x_of(i), y_of(vals[i])
        r = 3
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=ACCENT, outline="#FFFFFF")
    imax = vals.index(max(vals))
    imin = vals.index(min(vals))
    c.create_text(x_of(imax), y_of(max(vals)) - 12, text="%.1f" % max(vals), fill=ACCENT_DEEP, font=("Microsoft YaHei UI", 9, "bold"))
    c.create_text(x_of(imin), y_of(min(vals)) + 12, text="%.1f" % min(vals), fill="#8A9AA8", font=("Microsoft YaHei UI", 9, "bold"))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1040x860")
        self.root.minsize(900, 680)
        self.root.configure(bg=BG)
        self.data_path = get_data_path()
        self.weight_path = get_weight_path()
        self.action_lib_path = get_action_lib_path()
        self.records = load_records(self.data_path)
        self.weights = load_weights(self.weight_path)
        self.action_lib = load_action_lib(self.action_lib_path)
        self.item_index = {}
        self._setup_style()
        self._build_header()
        self._build_footer()
        self._build_notebook()
        self.refresh_all()

    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=FONT)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#C9E2F3", foreground=TEXT, font=FONT_BIG, padding=[22, 8])
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", ACCENT_DARK)])
        style.configure("TButton", font=FONT, padding=[10, 5])
        style.configure("Accent.TButton", background=ACCENT, foreground="#FFFFFF", font=FONT_BIG, padding=[16, 7], borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)], foreground=[("active", "#FFFFFF")])
        style.configure("TEntry", font=FONT, padding=4, fieldbackground="#FFFFFF")
        style.configure("TCombobox", font=FONT, padding=4)
        style.configure("Treeview", font=FONT, rowheight=28, fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", font=FONT_BIG, background="#C9E2F3", foreground=TEXT, padding=4)
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#FFFFFF")])

    def _build_header(self):
        header = tk.Frame(self.root, bg=ACCENT, height=96)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=APP_NAME, bg=ACCENT, fg="#FFFFFF", font=FONT_TITLE).place(x=28, y=16)
        tk.Label(header, text="训练 · 体重 · 统计，数据全程本地保存", bg=ACCENT, fg="#D9ECF9", font=FONT_BIG).place(x=30, y=58)
        tk.Label(header, text="FITNESS LOG", bg=ACCENT, fg="#A8D4F2", font=("Segoe UI", 11, "bold")).place(relx=1.0, x=-28, y=38, anchor="e")

    def _build_footer(self):
        foot = tk.Frame(self.root, bg=BG_PANEL, height=30)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)
        tk.Label(foot, text="数据自动保存在程序同目录：训练记录.txt · 体重记录.txt · 动作库.txt", bg=BG_PANEL, fg=HINT, font=FONT_SMALL).pack(side="left", padx=16, pady=6)

    def _build_notebook(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=16, pady=(14, 10))
        self.add_tab = ttk.Frame(self.nb, padding=22)
        self.view_tab = ttk.Frame(self.nb, padding=14)
        self.weight_tab = ttk.Frame(self.nb, padding=16)
        self.plan_tab = ttk.Frame(self.nb, padding=16)
        self.stats_tab = ttk.Frame(self.nb, padding=16)
        self.nb.add(self.add_tab, text="录入记录")
        self.nb.add(self.view_tab, text="查看记录")
        self.nb.add(self.weight_tab, text="体重追踪")
        self.nb.add(self.plan_tab, text="训练计划")
        self.nb.add(self.stats_tab, text="数据统计")
        self._build_add_tab()
        self._build_view_tab()
        self._build_weight_tab()
        self._build_plan_tab()
        self._build_stats_tab()
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _build_add_tab(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.var_date = tk.StringVar(value=today)
        self.var_action = tk.StringVar()
        self.var_sets = tk.StringVar()
        self.var_weight = tk.StringVar()
        self.var_reps = tk.StringVar()
        self.var_note = tk.StringVar()
        self.var_status = tk.StringVar()

        tk.Label(self.add_tab, text="录入一条训练记录", bg=BG, fg=TEXT, font=FONT_HEAD).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        def put_label(row, text):
            tk.Label(self.add_tab, text=text, bg=BG, fg=TEXT, font=FONT).grid(
                row=row, column=0, sticky="e", padx=(0, 12), pady=8)

        def put_entry(row, var, hint=None, button=None):
            e = ttk.Entry(self.add_tab, textvariable=var, width=30)
            e.grid(row=row, column=1, sticky="w", pady=8)
            col = 2
            if button is not None:
                button.grid(row=row, column=col, sticky="w", padx=(10, 0))
                col += 1
            if hint:
                tk.Label(self.add_tab, text=hint, bg=BG, fg=HINT, font=FONT_SMALL).grid(
                    row=row, column=col, sticky="w", padx=(10, 0))

        put_label(1, "训练日期")
        put_entry(1, self.var_date, button=ttk.Button(self.add_tab, text="今天", command=self._set_today))

        put_label(2, "动作名称")
        self.combo_action = ttk.Combobox(self.add_tab, textvariable=self.var_action, values=self.action_lib, width=28)
        self.combo_action.grid(row=2, column=1, sticky="w", pady=8)
        tk.Label(self.add_tab, text="可下拉选择，也可直接输入新动作", bg=BG, fg=HINT, font=FONT_SMALL).grid(
            row=2, column=2, sticky="w", padx=(10, 0))

        put_label(3, "组数")
        put_entry(3, self.var_sets, hint="例如：4")

        put_label(4, "重量 (kg)")
        put_entry(4, self.var_weight, hint="徒手动作可留空")

        put_label(5, "次数")
        put_entry(5, self.var_reps, hint="例如：8")

        put_label(6, "备注")
        put_entry(6, self.var_note, hint="可选")

        ttk.Button(self.add_tab, text="保存记录", style="Accent.TButton", command=self._add_record).grid(
            row=7, column=1, sticky="w", pady=(18, 0))

        self.status_label = tk.Label(self.add_tab, textvariable=self.var_status, bg=BG, fg=OK_GREEN, font=FONT)
        self.status_label.grid(row=8, column=1, sticky="w", pady=(12, 0))

    def _build_view_tab(self):
        top = ttk.Frame(self.view_tab)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="按日期筛选").pack(side="left")
        self.var_filter = tk.StringVar()
        ttk.Entry(top, textvariable=self.var_filter, width=14).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="筛选", command=lambda: self.refresh_view(self.var_filter.get().strip())).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="显示全部", command=lambda: self.refresh_view(None)).pack(side="left", padx=(8, 0))
        self.var_count = tk.StringVar(value="共 0 条记录")
        ttk.Label(top, textvariable=self.var_count).pack(side="right")

        cols = ("date", "action", "sets", "weight", "reps", "note")
        self.tree = ttk.Treeview(self.view_tab, columns=cols, show="headings", height=16)
        col_cfg = {
            "date": ("日期", 110, "center"),
            "action": ("动作", 130, "w"),
            "sets": ("组数", 70, "center"),
            "weight": ("重量(kg)", 90, "center"),
            "reps": ("次数", 70, "center"),
            "note": ("备注", 300, "w"),
        }
        for c, (t, w, a) in col_cfg.items():
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=a)
        self.tree.tag_configure("odd", background=ROW_A)
        self.tree.tag_configure("even", background=ROW_B)

        vsb = ttk.Scrollbar(self.view_tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        bottom = ttk.Frame(self.view_tab)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="修改选中记录", command=self._on_edit).pack(side="left")
        ttk.Button(bottom, text="删除选中记录", command=self._on_delete).pack(side="left", padx=(10, 0))
        tk.Label(bottom, text="提示：先在列表里点选一条记录，再点“修改”或“删除”", bg=BG, fg=HINT, font=FONT_SMALL).pack(side="left", padx=(16, 0))
        ttk.Button(bottom, text="导出 CSV", command=self._export_csv).pack(side="right")

    def _build_plan_tab(self):
        tk.Label(self.plan_tab, text="推拉腿（Push-Pull-Legs）三分化训练模板", bg=BG, fg=TEXT, font=FONT_HEAD).pack(anchor="w", pady=(0, 4))
        tk.Label(self.plan_tab, text="按“推日 → 拉日 → 腿日 → 休息”循环，每周练 3~6 天；点“去录入”可把动作填入录入页", bg=BG, fg=HINT, font=FONT).pack(anchor="w", pady=(0, 10))
        row = tk.Frame(self.plan_tab, bg=BG)
        row.pack(fill="both", expand=True)
        first = True
        for day, exs in PPL_PLAN.items():
            card = tk.Frame(row, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0 if first else 10, 0))
            first = False
            tk.Label(card, text=day, bg=CARD, fg=ACCENT_DEEP, font=("Microsoft YaHei UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 2))
            tk.Label(card, text="动作（建议组数 × 次数）", bg=CARD, fg=HINT, font=FONT_SMALL).pack(anchor="w", padx=16)
            for act, s, r in exs:
                line = tk.Frame(card, bg=CARD)
                line.pack(fill="x", padx=14, pady=5)
                tk.Label(line, text=act, bg=CARD, fg=TEXT, font=FONT_BIG, width=8, anchor="w").pack(side="left")
                tk.Label(line, text="%s × %s" % (s, r), bg=CARD, fg=HINT, font=FONT).pack(side="left", padx=(8, 0))
                ttk.Button(line, text="去录入", command=lambda a=act, ss=s, rr=r: self._plan_to_add(a, ss, rr)).pack(side="right")

    def _plan_to_add(self, action, sets, reps):
        self.var_action.set(action)
        self.var_sets.set(sets)
        self.var_reps.set(reps)
        self.var_weight.set("")
        self.nb.select(self.add_tab)

    def _build_weight_tab(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.var_wdate = tk.StringVar(value=today)
        self.var_wvalue = tk.StringVar()
        self.var_wstatus = tk.StringVar()

        form = ttk.Frame(self.weight_tab)
        form.pack(fill="x", pady=(0, 10))
        ttk.Label(form, text="日期").pack(side="left")
        ttk.Entry(form, textvariable=self.var_wdate, width=12).pack(side="left", padx=(6, 0))
        ttk.Button(form, text="今天", command=self._set_wtoday).pack(side="left", padx=(6, 0))
        ttk.Label(form, text="体重 (kg)").pack(side="left", padx=(18, 0))
        ttk.Entry(form, textvariable=self.var_wvalue, width=8).pack(side="left", padx=(6, 0))
        ttk.Button(form, text="记录体重", style="Accent.TButton", command=self._add_weight).pack(side="left", padx=(12, 0))
        self.weight_status = tk.Label(form, textvariable=self.var_wstatus, bg=BG, fg=OK_GREEN, font=FONT)
        self.weight_status.pack(side="left", padx=(14, 0))

        main = ttk.Frame(self.weight_tab)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=False)
        self.wtree = ttk.Treeview(left, columns=("date", "weight"), show="headings", height=12)
        self.wtree.heading("date", text="日期")
        self.wtree.heading("weight", text="体重(kg)")
        self.wtree.column("date", width=130, anchor="center")
        self.wtree.column("weight", width=100, anchor="center")
        self.wtree.tag_configure("odd", background=ROW_A)
        self.wtree.tag_configure("even", background=ROW_B)
        wsb = ttk.Scrollbar(left, orient="vertical", command=self.wtree.yview)
        self.wtree.configure(yscrollcommand=wsb.set)
        self.wtree.pack(side="left", fill="both", expand=True)
        wsb.pack(side="left", fill="y")

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        tk.Label(right, text="体重变化趋势", bg=BG, fg=TEXT, font=FONT_HEAD).pack(anchor="w", pady=(0, 6))
        self.wchart = tk.Canvas(right, width=560, height=300, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        self.wchart.pack(anchor="w")
        self.wchart.bind("<Configure>", lambda e: self._draw_weight_chart())

    def _build_stats_tab(self):
        cards = tk.Frame(self.stats_tab, bg=BG)
        cards.pack(fill="x")
        self.var_card_month = tk.StringVar(value="0 次")
        self.var_card_total = tk.StringVar(value="0 条")
        self.var_card_actions = tk.StringVar(value="0 种")
        self.var_card_weight = tk.StringVar(value="—")
        self._card(cards, "本月训练次数", self.var_card_month)
        self._card(cards, "累计训练记录", self.var_card_total)
        self._card(cards, "动作种类", self.var_card_actions)
        self._card(cards, "当前体重 (kg)", self.var_card_weight)

        body = tk.Frame(self.stats_tab, bg=BG)
        body.pack(fill="both", expand=True, pady=(14, 0))

        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(14, 0))

        card_l = self._card_container(left)
        tk.Label(card_l, text="动作总训练容量（重量 × 次数 × 组数）", bg=CARD, fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 8))
        vcols = ("action", "vol")
        self.vtree = ttk.Treeview(card_l, columns=vcols, show="headings", height=11)
        self.vtree.heading("action", text="动作")
        self.vtree.heading("vol", text="总容量(kg)")
        self.vtree.column("action", width=190, anchor="w")
        self.vtree.column("vol", width=120, anchor="center")
        self.vtree.tag_configure("odd", background=ROW_A)
        self.vtree.tag_configure("even", background=ROW_B)
        self.vtree.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        card_r = self._card_container(right)
        tk.Label(card_r, text="个人纪录 PR", bg=CARD, fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12, 8))
        prow = tk.Frame(card_r, bg=CARD)
        prow.pack(anchor="w", padx=14)
        self.var_pr_action = tk.StringVar()
        self.combo_pr = ttk.Combobox(prow, textvariable=self.var_pr_action, width=16)
        self.combo_pr.pack(side="left")
        ttk.Button(prow, text="查询", command=self._on_query_pr).pack(side="left", padx=(8, 0))
        self.var_pr_result = tk.StringVar()
        tk.Label(card_r, textvariable=self.var_pr_result, bg=CARD, fg=ACCENT_DEEP, font=FONT_BIG, wraplength=280, justify="left").pack(anchor="w", padx=14, pady=(10, 4))

        tk.Label(card_r, text="训练间隔提示", bg=CARD, fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=14, pady=(14, 8))
        self.interval_frame = tk.Frame(card_r, bg=CARD)
        self.interval_frame.pack(anchor="w", fill="x", padx=14, pady=(0, 8))

        tk.Label(card_r, text="动作重量趋势", bg=CARD, fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=14, pady=(6, 8))
        trow = tk.Frame(card_r, bg=CARD)
        trow.pack(anchor="w", padx=14)
        self.var_trend_action = tk.StringVar()
        self.combo_trend = ttk.Combobox(trow, textvariable=self.var_trend_action, width=16)
        self.combo_trend.pack(side="left")
        ttk.Button(trow, text="刷新", command=self._refresh_trend).pack(side="left", padx=(8, 0))
        self.trend_chart = tk.Canvas(card_r, height=180, bg=CARD, highlightthickness=0)
        self.trend_chart.pack(fill="both", expand=True, padx=10, pady=(8, 12))
        self.trend_chart.bind("<Configure>", lambda e: self._redraw_trend())

    def _card(self, parent, title, var):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1, padx=16, pady=12)
        card.pack(side="left", expand=True, fill="both", padx=(0, 10))
        tk.Label(card, text=title, bg=CARD, fg=HINT, font=FONT).pack(anchor="w")
        tk.Label(card, textvariable=var, bg=CARD, fg=ACCENT, font=FONT_CARD_NUM).pack(anchor="w", pady=(4, 0))

    def _card_container(self, parent):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)
        return card

    # —— 事件处理 ——
    def _set_today(self):
        self.var_date.set(datetime.now().strftime("%Y-%m-%d"))

    def _set_wtoday(self):
        self.var_wdate.set(datetime.now().strftime("%Y-%m-%d"))

    def _save(self):
        save_records(self.data_path, self.records)

    def _on_tab_changed(self, event):
        self.refresh_all()

    def refresh_all(self):
        self.var_filter.set("")
        self.refresh_view(None)
        self.refresh_stats()
        self.refresh_weights()
        self._refresh_action_combos()

    def _refresh_action_combos(self):
        self.combo_action["values"] = self.action_lib
        names = sorted(set(self.action_lib) | set(action_names(self.records)))
        self.combo_pr["values"] = names

    def refresh_view(self, filter_date):
        if filter_date and not is_valid_date(filter_date):
            messagebox.showwarning("提示", "日期格式不对，请输入 年-月-日（例如 2026-10-13）")
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.item_index = {}
        if filter_date:
            pairs = [(r, i) for i, r in enumerate(self.records) if r.date == filter_date]
        else:
            pairs = sorted(((r, i) for i, r in enumerate(self.records)), key=lambda x: x[0].date, reverse=True)
        for row, (r, idx) in enumerate(pairs):
            w = r.weight if r.weight else "—"
            tag = "even" if row % 2 == 0 else "odd"
            item = self.tree.insert("", "end", values=(r.date, r.action, r.sets, w, r.reps, r.note), tags=(tag,))
            self.item_index[item] = idx
        self.var_count.set("共 %d 条记录" % len(pairs))

    def _selected_index(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在列表里点选一条记录")
            return None
        return self.item_index[sel[0]]

    def _add_record(self):
        date = self.var_date.get().strip()
        action = self.var_action.get().strip()
        sets = self.var_sets.get().strip()
        weight = self.var_weight.get().strip()
        reps = self.var_reps.get().strip()
        note = self.var_note.get().strip()

        if not is_valid_date(date):
            self._status("请填写正确的日期，格式：年-月-日（例如 2026-10-13）", True)
            return
        if not action:
            self._status("请填写动作名称", True)
            return
        s = parse_positive_int(sets)
        if s is None:
            self._status("组数要填正整数（例如 4）", True)
            return
        w, ok = parse_weight(weight)
        if not ok:
            self._status("重量要填正数，徒手动作请留空", True)
            return
        r = parse_positive_int(reps)
        if r is None:
            self._status("次数要填正整数（例如 8）", True)
            return

        prev_max = action_pr(self.records, action)
        self.records.append(Record(date, action, str(s), w, str(r), note))
        self._save()

        if action not in self.action_lib:
            self.action_lib.append(action)
            save_action_lib(self.action_lib_path, self.action_lib)

        self.var_action.set("")
        self.var_sets.set("")
        self.var_weight.set("")
        self.var_reps.set("")
        self.var_note.set("")

        if w:
            new_w = float(w)
            if prev_max is not None and new_w > prev_max:
                self._status("已保存：%s %s组 %skg %s次 —— 并刷新了个人纪录！" % (action, s, w, r))
                self.root.after(200, lambda a=action, p=prev_max, n=new_w: messagebox.showinfo(
                    "恭喜！刷新个人纪录", "%s\n%s kg → %s kg" % (a, fmt_weight(p), fmt_weight(n))))
            else:
                self._status("已保存：%s %s组 %skg %s次" % (action, s, w, r))
        else:
            self._status("已保存：%s %s组（徒手） %s次" % (action, s, r))
        self.refresh_all()

    def _status(self, text, error=False):
        self.var_status.set(text)
        self.status_label.configure(fg=ERR_RED if error else OK_GREEN)

    def _on_edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        dlg = EditDialog(self.root, self.records[idx])
        self.root.wait_window(dlg)
        if dlg.result is not None:
            self.records[idx] = dlg.result
            self._save()
            if dlg.result.action not in self.action_lib:
                self.action_lib.append(dlg.result.action)
                save_action_lib(self.action_lib_path, self.action_lib)
            self.refresh_all()

    def _on_delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        r = self.records[idx]
        if r.weight:
            desc = "%s  %s  %s组  %skg  %s次" % (r.date, r.action, r.sets, r.weight, r.reps)
        else:
            desc = "%s  %s  %s组（徒手）  %s次" % (r.date, r.action, r.sets, r.reps)
        if messagebox.askyesno("删除确认", "确定删除这条记录吗？\n\n" + desc):
            del self.records[idx]
            self._save()
            self.refresh_all()

    def _export_csv(self):
        from tkinter import filedialog
        if not self.records:
            messagebox.showinfo("提示", "还没有训练记录，先录入一些再导出吧")
            return
        default = os.path.join(get_base_dir(), "训练记录_%s.csv" % datetime.now().strftime("%Y%m%d"))
        path = filedialog.asksaveasfilename(
            title="导出训练记录为 CSV",
            defaultextension=".csv",
            initialfile=os.path.basename(default),
            initialdir=get_base_dir(),
            filetypes=[("CSV 文件", "*.csv")],
        )
        if not path:
            return
        import csv
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["日期", "动作", "组数", "重量(kg)", "次数", "备注"])
            for r in sorted(self.records, key=lambda x: x.date):
                w.writerow([r.date, r.action, r.sets, r.weight, r.reps, r.note])
        messagebox.showinfo("导出成功", "已导出到：\n" + path)

    def refresh_stats(self):
        today = datetime.now()
        cnt = count_workouts_this_month(self.records, today)
        self.var_card_month.set("%d 次" % cnt)
        self.var_card_total.set("%d 条" % len(self.records))
        self.var_card_actions.set("%d 种" % len(action_names(self.records)))
        self._refresh_volume_table()
        names = sorted(set(self.action_lib) | set(action_names(self.records)))
        self.combo_pr["values"] = names
        if self.var_pr_action.get() not in names and names:
            self.var_pr_action.set(names[0])
        self._refresh_interval(today.date())
        self._refresh_trend()

    def _refresh_volume_table(self):
        for i in self.vtree.get_children():
            self.vtree.delete(i)
        vol = volume_by_action(self.records)
        items = sorted(vol.items(), key=lambda x: -x[1])
        for row, (a, v) in enumerate(items):
            tag = "even" if row % 2 == 0 else "odd"
            self.vtree.insert("", "end", values=(a, fmt_weight(v) if v > 0 else "—"), tags=(tag,))

    def _refresh_interval(self, today):
        for w in self.interval_frame.winfo_children():
            w.destroy()
        gaps = last_training_by_group(self.records, today)
        order = ["胸", "背", "腿", "肩", "臂", "核心", "有氧"]
        found = False
        for g in order:
            if g in gaps:
                days = gaps[g]
                if days <= 0:
                    text = "%s：今天练过 ✓" % g
                else:
                    text = "%s：%d 天前" % (g, days)
                tk.Label(self.interval_frame, text=text, bg=CARD, fg=TEXT, font=FONT_BIG).pack(anchor="w", pady=3)
                found = True
        if not found:
            tk.Label(self.interval_frame, text="暂无训练记录，快去开始第一次训练吧", bg=CARD, fg=HINT, font=FONT).pack(anchor="w", pady=4)

    def _refresh_trend(self):
        names = action_names(self.records)
        self.combo_trend["values"] = names
        if self.var_trend_action.get() not in names:
            self.var_trend_action.set(names[0] if names else "")
        self._redraw_trend()

    def _redraw_trend(self):
        action = self.var_trend_action.get().strip()
        pts = weight_trend(self.records, action) if action else []
        draw_line_chart(self.trend_chart, pts)

    def _on_query_pr(self):
        action = self.var_pr_action.get().strip()
        if not action:
            messagebox.showinfo("提示", "请选择或输入一个动作名称")
            return
        pr = action_pr(self.records, action)
        if pr is None:
            self.var_pr_result.set("「%s」目前还没有重量记录（可能是徒手动作）" % action)
        else:
            self.var_pr_result.set("「%s」历史最大重量：%s kg" % (action, fmt_weight(pr)))

    def _add_weight(self):
        d = self.var_wdate.get().strip()
        w = self.var_wvalue.get().strip()
        if not is_valid_date(d):
            self._wstatus("日期格式：年-月-日（例如 2026-10-13）", True)
            return
        wv = parse_float(w)
        if wv is None or wv <= 0:
            self._wstatus("体重要填正数", True)
            return
        self.weights.append((d, "%.1f" % wv))
        save_weights(self.weight_path, self.weights)
        self.var_wvalue.set("")
        self._wstatus("已记录：%s  %.1f kg" % (d, wv))
        self.refresh_weights()

    def _wstatus(self, text, error=False):
        self.var_wstatus.set(text)
        self.weight_status.configure(fg=ERR_RED if error else OK_GREEN)

    def refresh_weights(self):
        for i in self.wtree.get_children():
            self.wtree.delete(i)
        data = sorted(self.weights, key=lambda x: x[0])
        for row, (d, w) in enumerate(reversed(data)):
            tag = "even" if row % 2 == 0 else "odd"
            self.wtree.insert("", "end", values=(d, w), tags=(tag,))
        if data:
            self.var_card_weight.set(data[-1][1] + " kg")
        else:
            self.var_card_weight.set("—")
        self._draw_weight_chart(data)

    def _draw_weight_chart(self, data=None):
        if data is None:
            data = sorted(self.weights, key=lambda x: x[0])
        pts = [(d, float(x)) for d, x in data]
        draw_line_chart(self.wchart, pts)


class EditDialog(tk.Toplevel):
    def __init__(self, parent, record):
        super().__init__(parent)
        self.result = None
        self.title("修改记录")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 140, parent.winfo_rooty() + 110))

        self.var_date = tk.StringVar(value=record.date)
        self.var_action = tk.StringVar(value=record.action)
        self.var_sets = tk.StringVar(value=record.sets)
        self.var_weight = tk.StringVar(value=record.weight)
        self.var_reps = tk.StringVar(value=record.reps)
        self.var_note = tk.StringVar(value=record.note)

        body = ttk.Frame(self, padding=22)
        body.pack(fill="both", expand=True)

        fields = [
            ("训练日期", self.var_date),
            ("动作名称", self.var_action),
            ("组数", self.var_sets),
            ("重量 (kg)", self.var_weight),
            ("次数", self.var_reps),
            ("备注", self.var_note),
        ]
        for row, (lab, var) in enumerate(fields):
            ttk.Label(body, text=lab).grid(row=row, column=0, sticky="e", padx=(0, 10), pady=6)
            ttk.Entry(body, textvariable=var, width=28).grid(row=row, column=1, pady=6)

        btns = ttk.Frame(body)
        btns.grid(row=len(fields), column=0, columnspan=2, pady=(16, 0))
        ttk.Button(btns, text="保存", style="Accent.TButton", command=self._ok).pack(side="left", padx=(0, 12))
        ttk.Button(btns, text="取消", command=self.destroy).pack(side="left")

    def _ok(self):
        date = self.var_date.get().strip()
        action = self.var_action.get().strip()
        sets = self.var_sets.get().strip()
        weight = self.var_weight.get().strip()
        reps = self.var_reps.get().strip()
        note = self.var_note.get().strip()

        if not is_valid_date(date):
            messagebox.showwarning("提示", "日期格式应为 年-月-日（例如 2026-10-13）")
            return
        if not action:
            messagebox.showwarning("提示", "动作名称不能为空")
            return
        s = parse_positive_int(sets)
        if s is None:
            messagebox.showwarning("提示", "组数要填正整数")
            return
        w, ok = parse_weight(weight)
        if not ok:
            messagebox.showwarning("提示", "重量要填正数，徒手动作请留空")
            return
        r = parse_positive_int(reps)
        if r is None:
            messagebox.showwarning("提示", "次数要填正整数")
            return
        self.result = Record(date, action, str(s), w, str(r), note)
        self.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


def run_selftest():
    import tempfile
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "训练记录.txt")
    recs = [
        Record("2026-10-01", "深蹲", "3", "100", "5", ""),
        Record("2026-10-13", "卧推", "4", "60", "8", "状态不错"),
        Record("2026-10-13", "俯卧撑", "3", "", "20", ""),
    ]
    save_records(p, recs)
    loaded = load_records(p)
    assert len(loaded) == 3, "load count"
    assert loaded[1].note == "状态不错", "note"
    assert count_workouts_this_month(loaded, datetime(2026, 10, 13)) == 2, "month count"
    assert action_pr(loaded, "深蹲") == 100.0, "pr"
    assert action_pr(loaded, "俯卧撑") is None, "pr bodyweight"
    assert set(action_names(loaded)) == {"俯卧撑", "深蹲", "卧推"}, "names"
    assert fmt_weight(100.0) == "100", "fmt int"
    assert fmt_weight(60.5) == "60.5", "fmt dec"

    vol = volume_by_action(loaded)
    assert abs(vol["深蹲"] - 1500.0) < 1e-6, "vol squat"
    assert abs(vol["卧推"] - 1920.0) < 1e-6, "vol bench"
    assert vol.get("俯卧撑", 0.0) == 0.0, "vol bodyweight"

    assert groups_of("卧推") == ["胸"], "group bench"
    assert groups_of("硬拉") == ["背", "腿"], "group deadlift"
    assert groups_of("神秘动作") == [], "group unknown"

    gaps = last_training_by_group(loaded, date(2026, 10, 13))
    assert gaps["胸"] == 0, "chest today"
    assert gaps["腿"] == 12, "legs gap"

    tr = weight_trend(loaded, "卧推")
    assert tr == [("2026-10-13", 60.0)], "trend bench"
    assert weight_trend(loaded, "俯卧撑") == [], "trend bodyweight"

    wp = os.path.join(tmp, "体重记录.txt")
    save_weights(wp, [("2026-10-01", "70.5"), ("2026-10-13", "70.0")])
    wl = load_weights(wp)
    assert len(wl) == 2, "weight count"

    ap = os.path.join(tmp, "动作库.txt")
    lib = load_action_lib(ap)
    assert "卧推" in lib and "硬拉" in lib, "lib defaults"

    print("SELFTEST PASS")


def run_guitest():
    root = tk.Tk()
    App(root)
    root.after(700, root.destroy)
    root.mainloop()
    print("GUI OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        run_selftest()
    elif "--guitest" in sys.argv:
        run_guitest()
    else:
        main()
