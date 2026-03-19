# gui.py

import tkinter as tk
from tkinter import messagebox
import os
from csr_generator import generate_csr
from utils import save_file

BG      = "#F8F8F8"
CARD    = "#FFFFFF"
BORDER  = "#E0E0E0"
ACCENT  = "#2563EB"
TEXT    = "#1A1A1A"
MUTED   = "#6B7280"
DANGER  = "#B91C1C"
SUCCESS = "#15803D"
MONO    = ("Courier New", 9)
SANS    = ("Segoe UI", 10)
SANS_SM = ("Segoe UI", 9)

PLACEHOLDERS = {
    "cn":  "e.g. example.com",
    "org": "e.g. Acme Pvt Ltd",
    "c":   "e.g. IN",
    "st":  "e.g. West Bengal",
    "loc": "e.g. Kolkata",
}


class CSRApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSR Generator")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(560, 400)

        self._private_key = ""
        self._csr         = ""
        self._key_visible = False

        self._build_header()
        self._build_scrollable_body()
        self._build_form()
        self._build_summary()
        self._build_footer()

        self.root.update_idletasks()
        w = min(self.root.winfo_reqwidth(), 680)
        h = min(self.root.winfo_reqheight(), 820)
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── layout shell ───────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=CARD,
                       highlightthickness=1,
                       highlightbackground=BORDER)
        hdr.pack(fill="x", side="top")
        tk.Label(hdr, text="CSR Generator",
                 font=("Segoe UI", 13, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w", padx=20, pady=(14, 2))
        tk.Label(hdr,
                 text="Generate an RSA private key and Certificate Signing Request",
                 font=SANS_SM, bg=CARD, fg=MUTED).pack(
            anchor="w", padx=20, pady=(0, 14))

    def _build_scrollable_body(self):
        wrapper = tk.Frame(self.root, bg=BG)
        wrapper.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical",
                                 command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=BG)
        self._body_window = self.canvas.create_window(
            (0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>", self._on_body_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>",  self._on_mousewheel)
        self.canvas.bind_all("<Button-4>",    self._on_mousewheel)
        self.canvas.bind_all("<Button-5>",    self._on_mousewheel)

    def _on_body_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._body_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_footer(self):
        ft = tk.Frame(self.root, bg=BG)
        ft.pack(fill="x", side="bottom")
        tk.Frame(ft, bg=BORDER, height=1).pack(fill="x")
        tk.Label(ft,
                 text="RSA 2048-bit  ·  SHA-256  ·  Files saved to ~/Downloads",
                 font=SANS_SM, bg=BG, fg=MUTED).pack(pady=(4, 8))

    # ── form ───────────────────────────────────────────────

    def _build_form(self):
        card = tk.LabelFrame(self.body, text=" Certificate Details ",
                             font=SANS_SM, bg=CARD, fg=MUTED,
                             relief="flat",
                             highlightthickness=1,
                             highlightbackground=BORDER,
                             padx=16, pady=8)
        card.pack(fill="x", padx=16, pady=(12, 0))
        card.columnconfigure(0, weight=1)

        self.cn  = self._labeled_entry(card, "Common Name (Domain)",    0, "cn")
        self.org = self._labeled_entry(card, "Organisation",            2, "org")
        self.c   = self._labeled_entry(card, "Country (2-letter code)", 4, "c")
        self.st  = self._labeled_entry(card, "State / Province",        6, "st")
        self.loc = self._labeled_entry(card, "City / Locality",         8, "loc")

        tk.Button(card, text="Generate CSR",
                  command=self._generate,
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="#FFFFFF",
                  activebackground="#1D4ED8",
                  activeforeground="#FFFFFF",
                  relief="flat", cursor="hand2",
                  padx=18, pady=7).grid(
            row=10, column=0, sticky="e", pady=(14, 6))

    def _labeled_entry(self, parent, label, row, key):
        tk.Label(parent, text=label, bg=CARD, fg=MUTED,
                 font=SANS_SM, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(8, 0))

        var = tk.StringVar()
        e = tk.Entry(parent, textvariable=var, font=SANS,
                     bg=BG, fg=MUTED, relief="flat",
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.grid(row=row + 1, column=0, sticky="ew", ipady=5)

        placeholder = PLACEHOLDERS[key]
        e.insert(0, placeholder)

        def on_focus_in(_event, entry=e, var=var, ph=placeholder):
            if entry.get() == ph:
                entry.delete(0, tk.END)
                entry.config(fg=TEXT)

        def on_focus_out(_event, entry=e, var=var, ph=placeholder):
            if entry.get().strip() == "":
                entry.insert(0, ph)
                entry.config(fg=MUTED)

        e.bind("<FocusIn>",  on_focus_in)
        e.bind("<FocusOut>", on_focus_out)

        return var, e

    def _get_field(self, field_tuple):
        var, entry = field_tuple
        val = entry.get().strip()
        key = entry.winfo_name()
        for ph in PLACEHOLDERS.values():
            if val == ph:
                return ""
        return val

    # ── summary ────────────────────────────────────────────

    def _build_summary(self):
        outer = tk.LabelFrame(self.body, text=" Summary ",
                              font=SANS_SM, bg=CARD, fg=MUTED,
                              relief="flat",
                              highlightthickness=1,
                              highlightbackground=BORDER,
                              padx=12, pady=10)
        outer.pack(fill="x", padx=16, pady=(10, 0))

        # ── input details ──
        tk.Label(outer, text="Input Details",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 4))

        details = tk.Frame(outer, bg=CARD)
        details.pack(fill="x", pady=(0, 8))

        field_labels = ["Common Name", "Organisation",
                        "Country", "State", "City"]
        self.detail_vars = []
        for i, lbl in enumerate(field_labels):
            tk.Label(details, text=lbl + ":",
                     font=SANS_SM, bg=CARD, fg=MUTED,
                     anchor="w", width=16).grid(
                row=i, column=0, sticky="w", pady=1)
            var = tk.StringVar(value="—")
            tk.Label(details, textvariable=var,
                     font=SANS_SM, bg=CARD, fg=TEXT,
                     anchor="w").grid(row=i, column=1, sticky="w", pady=1)
            self.detail_vars.append(var)

        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(0, 8))

        # ── CSR block ──
        self._summary_block(
            outer,
            title="Generated CSR",
            warning=None,
            attr_name="sum_csr",
            copy_cmd=lambda: self._copy(self.sum_csr),
            dl_cmd=self._download_csr,
            dl_label="Download .csr",
            dl_bg=ACCENT,
        )

        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(8, 8))

        # ── Key block ──
        self._summary_block(
            outer,
            title="Private Key",
            warning="Keep this key secret. Never share it.",
            attr_name="sum_key",
            copy_cmd=lambda: self._copy(self.sum_key),
            dl_cmd=self._download_key,
            dl_label="Download .key",
            dl_bg="#1F2937",
            has_toggle=True,
        )

    def _summary_block(self, parent, title, warning, attr_name,
                       copy_cmd, dl_cmd, dl_label, dl_bg,
                       has_toggle=False):
        hdr = tk.Frame(parent, bg=CARD)
        hdr.pack(fill="x")

        tk.Label(hdr, text=title,
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(side="left")

        if has_toggle:
            self.eye_btn = tk.Button(hdr, text="Show",
                                     command=self._toggle_key,
                                     font=SANS_SM, bg=CARD, fg=ACCENT,
                                     relief="flat", cursor="hand2",
                                     activeforeground=ACCENT)
            self.eye_btn.pack(side="right")

        if warning:
            tk.Label(parent, text=warning,
                     font=SANS_SM, bg=CARD, fg=DANGER).pack(
                anchor="w", pady=(2, 0))

        box = tk.Text(parent, height=6, font=MONO,
                      bg=BG, fg=TEXT, relief="flat",
                      state="disabled",
                      highlightthickness=1,
                      highlightbackground=BORDER)
        box.pack(fill="x", pady=(4, 0))
        setattr(self, attr_name, box)

        btn_row = tk.Frame(parent, bg=CARD)
        btn_row.pack(fill="x", pady=(6, 0))

        self.dl_status = tk.Label(btn_row, text="",
                                  font=SANS_SM, bg=CARD, fg=SUCCESS)
        self.dl_status.pack(side="right")

        tk.Button(btn_row, text=dl_label,
                  command=dl_cmd,
                  font=("Segoe UI", 9, "bold"),
                  bg=dl_bg, fg="#FFFFFF",
                  activebackground="#1D4ED8",
                  activeforeground="#FFFFFF",
                  relief="flat", cursor="hand2",
                  padx=12, pady=4).pack(side="left", padx=(0, 6))

        tk.Button(btn_row, text="Copy",
                  command=copy_cmd,
                  font=SANS_SM, bg=CARD, fg=ACCENT,
                  relief="flat", cursor="hand2",
                  activeforeground=ACCENT).pack(side="left")

    # ── actions ────────────────────────────────────────────

    def _generate(self):
        data = {
            "CN": self._get_field(self.cn),
            "O":  self._get_field(self.org),
            "C":  self._get_field(self.c),
            "ST": self._get_field(self.st),
            "L":  self._get_field(self.loc),
        }

        if any(v == "" for v in data.values()):
            messagebox.showwarning("Missing fields",
                                   "Please fill in all fields before generating.")
            return

        if len(data["C"]) != 2:
            messagebox.showwarning("Invalid country",
                                   "Country must be exactly 2 letters (e.g. IN, US).")
            return

        try:
            self._private_key, self._csr = generate_csr(data)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        for var, val in zip(self.detail_vars,
                            [data["CN"], data["O"], data["C"],
                             data["ST"], data["L"]]):
            var.set(val)

        self._set_text(self.sum_csr, self._csr)

        self._key_visible = False
        self.eye_btn.config(text="Show")
        self._set_text(self.sum_key, self._masked_key())

        self.dl_status.config(text="")

        # scroll to summary
        self.root.update_idletasks()
        self.canvas.yview_moveto(0.4)

    def _masked_key(self):
        if not self._private_key:
            return ""
        lines = self._private_key.strip().splitlines()
        masked = []
        for line in lines:
            if line.startswith("-----"):
                masked.append(line)
            else:
                masked.append("•" * min(len(line), 64))
        return "\n".join(masked)

    def _toggle_key(self):
        if not self._private_key:
            return
        self._key_visible = not self._key_visible
        if self._key_visible:
            self.eye_btn.config(text="Hide")
            self._set_text(self.sum_key, self._private_key)
        else:
            self.eye_btn.config(text="Show")
            self._set_text(self.sum_key, self._masked_key())

    def _download_csr(self):
      if not self._csr:
          messagebox.showwarning("Nothing to save", "Generate a CSR first.")
          return
      folder = os.path.dirname(os.path.abspath(__file__))
      path = os.path.join(folder, "request.csr")
      save_file(self._csr, path)
      self.dl_status.config(text=f"Saved → {path}")

    def _download_key(self):
      if not self._private_key:
          messagebox.showwarning("Nothing to save", "Generate a CSR first.")
          return
      folder = os.path.dirname(os.path.abspath(__file__))
      path = os.path.join(folder, "private.key")
      save_file(self._private_key, path)
      self.dl_status.config(text=f"Saved → {path}")


    def _set_text(self, widget, content):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.config(state="disabled")

    def _copy(self, widget):
        content = widget.get("1.0", tk.END).strip()
        if not content:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)

    def run(self):
        self.root.mainloop()