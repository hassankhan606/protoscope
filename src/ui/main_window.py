"""
Main Window - BioDiscover UI
Bright modern biotech interface with dark navy navbar.
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
from datetime import datetime

from src.ui.theme import BioTheme
from src.ui.protein_panel import ProteinPanel
from src.ui.gene_panel import GenePanel
from src.ui.pathway_panel import PathwayPanel
from src.ui.structure_panel import StructurePanel
from src.ui.dashboard_panel import DashboardPanel


class BioDiscoverApp:
    def __init__(self, root):
        self.root = root
        self.t = BioTheme()
        self._setup_styles()
        self._build()
        self._show_dashboard()

    def _setup_styles(self):
        self.root.configure(bg=self.t.BG_MAIN)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                        background=self.t.BG_CARD,
                        troughcolor=self.t.BG_MAIN,
                        arrowcolor=self.t.TEXT_DIM,
                        relief="flat", borderwidth=0)
        style.configure("TCombobox",
                        fieldbackground=self.t.BG_PANEL,
                        background=self.t.BG_PANEL,
                        foreground=self.t.TEXT_MAIN,
                        selectbackground=self.t.ACCENT_TEAL)

    def _build(self):
        # ── Navbar ─────────────────────────────────────────────────
        nav = tk.Frame(self.root, bg=self.t.NAV_BG, height=56)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        # Logo
        logo_f = tk.Frame(nav, bg=self.t.NAV_BG)
        logo_f.pack(side="left", padx=20, pady=10)

        hex_canvas = tk.Canvas(logo_f, width=26, height=26,
                               bg=self.t.NAV_BG, highlightthickness=0)
        hex_canvas.pack(side="left")
        # Draw hexagon
        pts = []
        import math
        cx, cy, r = 13, 13, 11
        for i in range(6):
            angle = math.radians(60*i - 30)
            pts += [cx + r*math.cos(angle), cy + r*math.sin(angle)]
        hex_canvas.create_polygon(pts, fill=self.t.ACCENT_TEAL, outline="")

        tk.Label(logo_f, text="  BioDiscover",
                 font=("Segoe UI", 15, "bold"),
                 fg="#ffffff", bg=self.t.NAV_BG).pack(side="left")

        # Accent line under logo
        tk.Frame(nav, bg=self.t.ACCENT_TEAL,
                 width=2, height=32).pack(side="left", padx=16, pady=12)

        # Nav links
        self.nav_buttons = []
        nav_items = [
            ("Dashboard",   self._show_dashboard),
            ("Proteins",    self._show_proteins),
            ("Genes",       self._show_genes),
            ("Pathways",    self._show_pathways),
            ("Structures",  self._show_structures),
        ]
        for label, cmd in nav_items:
            btn = tk.Button(nav, text=label,
                            font=("Segoe UI", 10),
                            fg=self.t.NAV_TEXT,
                            bg=self.t.NAV_BG,
                            activeforeground=self.t.ACCENT_TEAL,
                            activebackground=self.t.NAV_BG,
                            relief="flat",
                            padx=14, pady=0,
                            cursor="hand2",
                            command=cmd)
            btn.pack(side="left", fill="y")
            self.nav_buttons.append(btn)

        # Clock on right
        self.clock = tk.Label(nav, text="",
                              font=("Segoe UI", 9),
                              fg=self.t.NAV_TEXT, bg=self.t.NAV_BG)
        self.clock.pack(side="right", padx=20)
        self._tick()

        # PhD badge
        badge = tk.Label(nav, text=" PhD Edition ",
                         font=("Segoe UI", 9, "bold"),
                         fg=self.t.NAV_BG,
                         bg=self.t.ACCENT_TEAL,
                         padx=4, pady=2)
        badge.pack(side="right", padx=8, pady=14)

        # ── Teal accent line under navbar ──────────────────────────
        tk.Frame(self.root, bg=self.t.ACCENT_TEAL, height=2).pack(fill="x")

        # ── Content area ───────────────────────────────────────────
        self.content = tk.Frame(self.root, bg=self.t.BG_MAIN)
        self.content.pack(fill="both", expand=True)

        # ── Status bar ─────────────────────────────────────────────
        sb = tk.Frame(self.root, bg=self.t.BG_PANEL,
                      height=26, relief="flat")
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=self.t.BORDER, height=1).pack(fill="x", side="top")
        self.status_lbl = tk.Label(sb,
                                   text="● Ready  |  UniProt · NCBI · PDB · KEGG · AlphaFold",
                                   font=("Segoe UI", 9),
                                   fg=self.t.ACCENT_TEAL,
                                   bg=self.t.BG_PANEL, anchor="w")
        self.status_lbl.pack(side="left", padx=14, pady=4)

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _highlight(self, idx):
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.configure(fg=self.t.ACCENT_TEAL,
                              bg=self.t.NAV_ACTIVE_BG)
            else:
                btn.configure(fg=self.t.NAV_TEXT, bg=self.t.NAV_BG)

    def _show_dashboard(self):
        self._clear(); self._highlight(0)
        DashboardPanel(self.content, self.t, self.set_status)

    def _show_proteins(self):
        self._clear(); self._highlight(1)
        ProteinPanel(self.content, self.t, self.set_status)

    def _show_genes(self):
        self._clear(); self._highlight(2)
        GenePanel(self.content, self.t, self.set_status)

    def _show_pathways(self):
        self._clear(); self._highlight(3)
        PathwayPanel(self.content, self.t, self.set_status)

    def _show_structures(self):
        self._clear(); self._highlight(4)
        StructurePanel(self.content, self.t, self.set_status)

    def set_status(self, msg, color=None):
        self.status_lbl.configure(
            text=f"● {msg}", fg=color or self.t.ACCENT_TEAL)

    def _tick(self):
        self.clock.configure(
            text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick)
