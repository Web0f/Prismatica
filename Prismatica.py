import math
import re
import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------------
#  ХЕЛПЕРЫ ЦВЕТА
# ------------------------------------------------------------------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(c))) for c in rgb])

def lighten(hex_color, amount=0.25):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex((r + (255 - r) * amount,
                       g + (255 - g) * amount,
                       b + (255 - b) * amount))

def darken(hex_color, amount=0.25):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex((r * (1 - amount), g * (1 - amount), b * (1 - amount)))

def luminance(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255

def contrast_text(bg_hex):
    return "#ffffff" if luminance(bg_hex) < 0.6 else "#1a1a2e"

# ------------------------------------------------------------------
#  ТЕМЫ
# ------------------------------------------------------------------
THEMES = {
    "rainbow": {"bg": "#0e0e24", "panel": "#1b1b3d", "display_bg": "#05050f",
        "display_fg": "#ffffff", "muted": "#8f8fd0", "disabled": "#2a2a45",
        "accent": "#ffd60a", "eq": "#22e06b", "glow": "#7b5cff",
        "colors": ["#ff2d55","#ff7a00","#ffd60a","#22e06b","#00c7be","#0a84ff","#bf5af2"]},
    "neon": {"bg": "#000000", "panel": "#0a0a0a", "display_bg": "#000000",
        "display_fg": "#eaffea", "muted": "#3a7a3a", "disabled": "#141414",
        "accent": "#faff00", "eq": "#39ff14", "glow": "#39ff14",
        "colors": ["#ff073a","#ff6ec7","#faff00","#39ff14","#00f0ff","#4d4dff","#b026ff"]},
    "sunset": {"bg": "#1a0838", "panel": "#2a1055", "display_bg": "#12062a",
        "display_fg": "#fff0d0", "muted": "#b090d0", "disabled": "#3a2a5a",
        "accent": "#ffd93d", "eq": "#ffd93d", "glow": "#ff5f6d",
        "colors": ["#ff5f6d","#ff8c42","#ffc371","#ffd93d","#f9a826","#e056fd","#a044ff"]},
    "ocean": {"bg": "#021820", "panel": "#042c3d", "display_bg": "#001018",
        "display_fg": "#e6fbff", "muted": "#4a8fa3", "disabled": "#0d3a4d",
        "accent": "#00f5d4", "eq": "#00f5d4", "glow": "#00b4d8",
        "colors": ["#00b4d8","#48cae4","#90e0ef","#00f5d4","#0fa3b1","#1e6091","#7bdff2"]},
    "forest": {"bg": "#0a1e14", "panel": "#123322", "display_bg": "#061510",
        "display_fg": "#eaffee", "muted": "#5f9b7a", "disabled": "#1d4230",
        "accent": "#b7e4c7", "eq": "#7bff9b", "glow": "#52b788",
        "colors": ["#2d6a4f","#40916c","#52b788","#74c69d","#95d5b2","#b7e4c7","#7bff9b"]},
    "space": {"bg": "#08081a", "panel": "#14142e", "display_bg": "#03030d",
        "display_fg": "#f5ebff", "muted": "#8a7fb0", "disabled": "#20203a",
        "accent": "#ffbe0b", "eq": "#ffbe0b", "glow": "#8338ec",
        "colors": ["#ff006e","#fb5607","#ffbe0b","#8338ec","#3a86ff","#06d6a0","#ef476f"]},
    "pastel": {"bg": "#fef6ff", "panel": "#ffffff", "display_bg": "#f4f0ff",
        "display_fg": "#4a3f5a", "muted": "#b0a0c0", "disabled": "#ece4ee",
        "accent": "#ffd6a5", "eq": "#b8f5c8", "glow": "#c8b6ff",
        "colors": ["#ffadad","#ffd6a5","#fdffb6","#caffbf","#9bf6ff","#a0c4ff","#bdb2ff"]},
}

THEME_ORDER = ["rainbow", "neon", "sunset", "ocean", "forest", "space", "pastel"]
MODE_ORDER = ["basic", "sci", "prog"]

LAYOUTS = {
    "basic": [
        [("C","clear"),("⌫","back"),("%","percent"),("÷","ins:÷")],
        [("7","ins:7"),("8","ins:8"),("9","ins:9"),("×","ins:×")],
        [("4","ins:4"),("5","ins:5"),("6","ins:6"),("−","ins:-")],
        [("1","ins:1"),("2","ins:2"),("3","ins:3"),("+","ins:+")],
        [("±","neg"),("0","ins:0"),(".","ins:."),("=","equals")],
    ],
    "sci": [
        [("sin","sin"),("cos","cos"),("tan","tan"),("π","pi"),("e","e"),("C","clear")],
        [("ln","ln"),("log","log"),("√","sqrt"),("x²","sq"),("xʸ","pow"),("⌫","back")],
        [("(","paren_open"),(")","paren_close"),("n!","fact"),("%","percent"),("±","neg"),("1/x","inv")],
        [("7","ins:7"),("8","ins:8"),("9","ins:9"),("÷","ins:÷"),("×","ins:×"),("=","equals",{"rs":3})],
        [("4","ins:4"),("5","ins:5"),("6","ins:6"),("−","ins:-"),("+","ins:+")],
        [("1","ins:1"),("2","ins:2"),("3","ins:3"),("0","ins:0"),(".","ins:.")],
    ],
    "prog": [
        [("HEX","base:16"),("DEC","base:10"),("OCT","base:8"),("BIN","base:2"),("AC","clear"),("⌫","back")],
        [("A","ins:A"),("B","ins:B"),("C","ins:C"),("D","ins:D"),("E","ins:E"),("F","ins:F")],
        [("AND","ins:&"),("OR","ins:|"),("XOR","ins:^"),("NOT","not_op"),("<<","ins:<<"),(">>","ins:>>")],
        [("7","ins:7"),("8","ins:8"),("9","ins:9"),("÷","ins:/"),("×","ins:*"),("=","equals",{"rs":3})],
        [("4","ins:4"),("5","ins:5"),("6","ins:6"),("−","ins:-"),("+","ins:+")],
        [("1","ins:1"),("2","ins:2"),("3","ins:3"),("0","ins:0"),("(","paren_open")],
    ],
}

L = {
    "ru": {
        "title": "🌈 Радужный калькулятор",
        "lang": "Язык", "mode": "Режим", "theme": "Тема",
        "error": "Ошибка", "div_zero": "Деление на ноль",
        "modes": {"basic": "Обычный", "sci": "Научный", "prog": "Программист"},
        "themes": {"rainbow": "Радуга", "neon": "Неон", "sunset": "Закат",
                   "ocean": "Океан", "forest": "Лес", "space": "Космос", "pastel": "Пастель"},
        "langs": {"ru": "Русский", "en": "English"},
    },
    "en": {
        "title": "🌈 Rainbow Calculator",
        "lang": "Language", "mode": "Mode", "theme": "Theme",
        "error": "Error", "div_zero": "Division by zero",
        "modes": {"basic": "Basic", "sci": "Scientific", "prog": "Programmer"},
        "themes": {"rainbow": "Rainbow", "neon": "Neon", "sunset": "Sunset",
                   "ocean": "Ocean", "forest": "Forest", "space": "Space", "pastel": "Pastel"},
        "langs": {"ru": "Русский", "en": "English"},
    },
}

SAFE_FUNCS = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "sqrt": math.sqrt, "ln": math.log, "log": math.log10,
    "fact": lambda n: math.factorial(int(n)),
    "pi": math.pi, "e": math.e, "abs": abs,
}


class RainbowCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("780x1000")
        self.minsize(620, 820)

        self.lang = tk.StringVar(value="ru")
        self.mode_key = "basic"
        self.theme_key = "rainbow"
        self.base = 10
        self.fullscreen = False

        self.expr = tk.StringVar()
        self.history = tk.StringVar()
        self.mode_display = tk.StringVar()
        self.theme_display = tk.StringVar()
        self.lang_display = tk.StringVar()

        self.funcs = {
            "clear": self.clear_all, "back": self.backspace,
            "equals": self.do_equals, "neg": self.toggle_sign,
            "percent": lambda: self.insert("%"),
            "pi": lambda: self.insert("π"),
            "e": lambda: self.insert("e"),
            "sqrt": lambda: self.insert("√("),
            "sq": lambda: self.insert("**2"),
            "pow": lambda: self.insert("**"),
            "sin": lambda: self.insert("sin("),
            "cos": lambda: self.insert("cos("),
            "tan": lambda: self.insert("tan("),
            "ln": lambda: self.insert("ln("),
            "log": lambda: self.insert("log("),
            "fact": lambda: self.insert("!"),
            "inv": lambda: self.insert("1/("),
            "paren_open": lambda: self.insert("("),
            "paren_close": lambda: self.insert(")"),
            "not_op": lambda: self.insert("~"),
        }

        self._build_widgets()
        self._retranslate()
        self.apply_theme()
        self._bind_keys()

    # ---------------------------------------------------------------
    def _t(self, key):
        return L[self.lang.get()][key]

    def _build_widgets(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.top = tk.Frame(self)
        self.top.pack(fill="x", padx=14, pady=(14, 8))

        self.lbl_lang = tk.Label(self.top, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_lang.pack(side="left")
        self.lang_cb = ttk.Combobox(self.top, textvariable=self.lang_display,
                                    state="readonly", width=10,
                                    font=("Segoe UI", 11, "bold"))
        self.lang_cb.pack(side="left", padx=(6, 14))
        self.lang_cb.bind("<<ComboboxSelected>>", self.on_lang_change)

        self.lbl_mode = tk.Label(self.top, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_mode.pack(side="left")
        self.mode_cb = ttk.Combobox(self.top, textvariable=self.mode_display,
                                    state="readonly", width=13,
                                    font=("Segoe UI", 11, "bold"))
        self.mode_cb.pack(side="left", padx=(6, 14))
        self.mode_cb.bind("<<ComboboxSelected>>", self.on_mode_change)

        self.lbl_theme = tk.Label(self.top, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_theme.pack(side="left")
        self.theme_cb = ttk.Combobox(self.top, textvariable=self.theme_display,
                                     state="readonly", width=13,
                                     font=("Segoe UI", 11, "bold"))
        self.theme_cb.pack(side="left", padx=6)
        self.theme_cb.bind("<<ComboboxSelected>>", self.on_theme_change)

        self.fs_btn = tk.Button(self.top, text="⛶  F11",
                                command=self.toggle_fullscreen,
                                bd=0, padx=12, pady=6, cursor="hand2",
                                font=("Segoe UI", 11, "bold"))
        self.fs_btn.pack(side="right")

        self.glow_frame = tk.Frame(self, bd=0)
        self.glow_frame.pack(fill="x", padx=14, pady=8)
        self.disp = tk.Frame(self.glow_frame, bd=0)
        self.disp.pack(fill="x", padx=3, pady=3)

        self.hist_lbl = tk.Label(self.disp, textvariable=self.history,
                                 anchor="e", font=("Consolas", 14))
        self.hist_lbl.pack(fill="x", padx=16, pady=(12, 0))

        self.entry = tk.Entry(self.disp, textvariable=self.expr,
                              state="readonly", justify="right",
                              font=("Consolas", 34, "bold"),
                              bd=0, relief="flat")
        self.entry.pack(fill="x", padx=16, pady=(4, 0), ipady=12)

        self.info_lbl = tk.Label(self.disp, text="", anchor="e",
                                 font=("Consolas", 12, "bold"))
        self.info_lbl.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    # ---------------------------------------------------------------
    def _retranslate(self):
        self.title(self._t("title"))
        self.lbl_lang.configure(text=self._t("lang"))
        self.lbl_mode.configure(text=self._t("mode"))
        self.lbl_theme.configure(text=self._t("theme"))

        self.lang_cb["values"] = list(self._t("langs").values())
        self.lang_display.set(self._t("langs")[self.lang.get()])

        self.mode_cb["values"] = [self._t("modes")[k] for k in MODE_ORDER]
        self.mode_display.set(self._t("modes")[self.mode_key])

        self.theme_cb["values"] = [self._t("themes")[k] for k in THEME_ORDER]
        self.theme_display.set(self._t("themes")[self.theme_key])

    def on_lang_change(self, *_):
        for key, name in self._t("langs").items():
            if name == self.lang_display.get():
                self.lang.set(key)
                break
        self._retranslate()
        cur = self.expr.get()
        if cur == L["ru"]["error"] or cur == L["en"]["error"]:
            self.expr.set(self._t("error"))
        elif cur == L["ru"]["div_zero"] or cur == L["en"]["div_zero"]:
            self.expr.set(self._t("div_zero"))

    def on_mode_change(self, *_):
        for key in MODE_ORDER:
            if self._t("modes")[key] == self.mode_display.get():
                self.mode_key = key
                break
        if self.mode_key != "prog":
            self.base = 10
        self.expr.set("")
        self.history.set("")
        self.info_lbl.configure(text="")
        self.rebuild_buttons()

    def on_theme_change(self, *_):
        for key in THEME_ORDER:
            if self._t("themes")[key] == self.theme_display.get():
                self.theme_key = key
                break
        self.apply_theme()

    # ---------------------------------------------------------------
    def apply_theme(self, *_):
        t = THEMES[self.theme_key]

        self.style.configure("TCombobox",
                             fieldbackground=t["panel"],
                             background=t["panel"],
                             foreground=t["display_fg"],
                             arrowcolor=t["accent"],
                             borderwidth=0, relief="flat",
                             padding=4)
        self.style.map("TCombobox",
                       fieldbackground=[("readonly", t["panel"])],
                       foreground=[("readonly", t["display_fg"])])

        self.configure(bg=t["bg"])
        for w in (self.top, self.btn_frame):
            w.configure(bg=t["bg"])
        self.glow_frame.configure(bg=t["glow"])
        self.disp.configure(bg=t["display_bg"])

        self.lbl_lang.configure(bg=t["bg"], fg=t["display_fg"])
        self.lbl_mode.configure(bg=t["bg"], fg=t["display_fg"])
        self.lbl_theme.configure(bg=t["bg"], fg=t["display_fg"])

        self.fs_btn.configure(bg=t["accent"], fg=contrast_text(t["accent"]),
                              activebackground=lighten(t["accent"], 0.25),
                              activeforeground=contrast_text(t["accent"]))

        self.hist_lbl.configure(bg=t["display_bg"], fg=t["muted"])
        self.entry.configure(readonlybackground=t["display_bg"],
                             fg=t["display_fg"],
                             insertbackground=t["display_fg"])
        self.info_lbl.configure(bg=t["display_bg"], fg=t["accent"])

        self.rebuild_buttons()

    def rebuild_buttons(self):
        t = THEMES[self.theme_key]
        for w in self.btn_frame.winfo_children():
            w.destroy()

        rows = LAYOUTS[self.mode_key]
        ncols = 6
        for c in range(ncols):
            self.btn_frame.columnconfigure(c, weight=1, uniform="col")
        for r in range(len(rows)):
            self.btn_frame.rowconfigure(r, weight=1, uniform="row")

        colors = t["colors"]
        for r, row in enumerate(rows):
            for c, item in enumerate(row):
                text, action = item[0], item[1]
                opts = item[2] if len(item) > 2 else {}

                if action == "equals":
                    bg = t["eq"]
                elif action.startswith("base:"):
                    active = int(action.split(":")[1]) == self.base
                    bg = t["accent"] if active else colors[(r + c) % len(colors)]
                else:
                    bg = colors[(r + c) % len(colors)]

                enabled = self._is_enabled(action)
                fg = contrast_text(bg)
                hover = lighten(bg, 0.28)
                pressed = darken(bg, 0.22)

                # крупный шрифт: одиночные символы больше
                size = 30 if len(text) == 1 else 22

                btn = tk.Button(
                    self.btn_frame, text=text,
                    command=lambda a=action: self.on_press(a),
                    bg=bg, fg=fg,
                    activebackground=pressed, activeforeground=fg,
                    bd=0, relief="flat", cursor="hand2",
                    font=("Segoe UI", size, "bold"),
                    highlightthickness=0)

                if not enabled:
                    btn.configure(state="disabled",
                                  bg=t["disabled"],
                                  disabledforeground=t["muted"])
                else:
                    btn.bind("<Enter>", lambda e, b=btn, h=hover: b.configure(bg=h))
                    btn.bind("<Leave>", lambda e, b=btn, c=bg: b.configure(bg=c))
                    btn.bind("<ButtonPress-1>",
                             lambda e, b=btn, p=pressed: b.configure(bg=p))
                    btn.bind("<ButtonRelease-1>",
                             lambda e, b=btn, h=hover: b.configure(bg=h))

                btn.grid(row=r, column=c,
                         rowspan=opts.get("rs", 1),
                         columnspan=opts.get("cs", 1),
                         sticky="nsew", padx=3, pady=3)

    # ---------------------------------------------------------------
    def on_press(self, action):
        if action.startswith("ins:"):
            self.insert(action[4:])
        elif action.startswith("base:"):
            self.base = int(action.split(":")[1])
            self.expr.set("")
            self.history.set("")
            self.info_lbl.configure(text="")
            self.rebuild_buttons()
        else:
            fn = self.funcs.get(action)
            if fn:
                fn()

    def insert(self, text):
        cur = self.expr.get()
        if cur in (L["ru"]["error"], L["en"]["error"],
                   L["ru"]["div_zero"], L["en"]["div_zero"]):
            cur = ""
        self.expr.set(cur + text)

    def clear_all(self):
        self.expr.set("")
        self.history.set("")
        self.info_lbl.configure(text="")

    def backspace(self):
        self.expr.set(self.expr.get()[:-1])

    def toggle_sign(self):
        s = self.expr.get()
        self.expr.set(s[1:] if s.startswith("-") else "-" + s)

    def _is_enabled(self, action):
        if self.mode_key != "prog" or not action.startswith("ins:"):
            return True
        ch = action[4:]
        if len(ch) != 1 or ch not in "0123456789ABCDEF":
            return True
        if ch in "01":
            return True
        if ch in "234567":
            return self.base >= 8
        if ch in "89":
            return self.base >= 10
        return self.base == 16

    def do_equals(self):
        raw = self.expr.get().strip()
        if not raw:
            return
        self.history.set(raw + " =")
        try:
            if self.mode_key == "prog":
                value = self.eval_programmer(raw)
                self.expr.set(self.to_base(value, self.base))
                self.show_bases(value)
            else:
                value = self.eval_math(raw)
                self.expr.set(self.format_number(value))
                self.info_lbl.configure(text="")
        except ZeroDivisionError:
            self.expr.set(self._t("div_zero"))
        except Exception:
            self.expr.set(self._t("error"))

    def eval_math(self, s):
        s = s.replace("×", "*").replace("÷", "/").replace("−", "-")
        s = s.replace("^", "**").replace("√", "sqrt").replace("π", "pi")
        s = s.replace("%", "/100")
        s = re.sub(r"(?<=[0-9)])(?=(?:sin|cos|tan|sqrt|log|ln|fact|pi|e)\b)", "*", s)
        s = re.sub(r"(\d+(?:\.\d+)?)!", r"fact(\1)", s)
        opens = s.count("(") - s.count(")")
        if opens > 0:
            s += ")" * opens
        return eval(s, {"__builtins__": {}}, SAFE_FUNCS)

    def eval_programmer(self, s):
        base = self.base
        def conv(m):
            try:
                return str(int(m.group(0), base))
            except ValueError:
                return m.group(0)
        s = s.replace("×", "*").replace("÷", "/").replace("−", "-")
        s = re.sub(r"[0-9A-Fa-f]+", conv, s)
        s = re.sub(r"(?<!/)/(?!/)", "//", s)
        opens = s.count("(") - s.count(")")
        if opens > 0:
            s += ")" * opens
        return int(eval(s, {"__builtins__": {}}, {}))

    @staticmethod
    def format_number(v):
        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                return "Error"
            if abs(v - round(v)) < 1e-12 and abs(v) < 1e15:
                return str(int(round(v)))
            return f"{v:.10g}"
        return str(v)

    @staticmethod
    def to_base(n, base):
        if n == 0:
            return "0"
        digits = "0123456789ABCDEF"
        neg = n < 0
        n = abs(n)
        out = ""
        while n:
            out = digits[n % base] + out
            n //= base
        return ("-" if neg else "") + out

    def show_bases(self, n):
        self.info_lbl.configure(
            text="HEX {}   DEC {}   OCT {}   BIN {}".format(
                self.to_base(n, 16), n,
                self.to_base(n, 8), self.to_base(n, 2)))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def set_fullscreen(self, value):
        self.fullscreen = value
        self.attributes("-fullscreen", value)

    def _bind_keys(self):
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda e: self.set_fullscreen(False))
        self.bind("<Return>", lambda e: self.do_equals())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Delete>", lambda e: self.clear_all())
        self.bind_all("<Key>", self._on_key)

    def _on_key(self, event):
        ch = event.char
        if not ch:
            return
        mapping = {"*": "×", "/": "÷", "^": "**"}
        if ch in "0123456789.+-()%":
            self.insert(ch)
        elif ch in mapping:
            self.insert(mapping[ch])


if __name__ == "__main__":
    app = RainbowCalculator()
    app.mainloop()