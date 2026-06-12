"""
Main Window - BioDiscover UI
Beautiful dark biotech-themed interface using CustomTkinter
"""

import tkinter as tk
from tkinter import ttk, font
import threading
import webbrowser
from datetime import datetime

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

from src.ui.theme import BioTheme
from src.ui.protein_panel import ProteinPanel
from src.ui.gene_panel import GenePanel
from src.ui.pathway_panel import PathwayPanel
from src.ui.structure_panel import StructurePanel
from src.ui.dashboard_panel import DashboardPanel


class BioDiscoverApp:
    def __init__(self, root):
        self.root = root
        self.theme = BioTheme()
        self._setup_root()
        self._build_layout()
        self._show_dashboard()

    def _setup_root(self):
        self.root.configure(bg=self.theme.BG_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Custom styles for ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.theme.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.theme.BG_MID,
                        foreground=self.theme.TEXT_DIM,
                        padding=[16, 8],
                        font=("Consolas", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", self.theme.BG_PANEL)],
                  foreground=[("selected", self.theme.ACCENT_GREEN)])
        style.configure("Vertical.TScrollbar",
                        background=self.theme.BG_MID,
                        troughcolor=self.theme.BG_DARK,
                        arrowcolor=self.theme.ACCENT_GREEN)

    def _build_layout(self):
        # ── Top Header ──────────────────────────────────────────────
        self.header = tk.Frame(self.root, bg=self.theme.BG_PANEL,
                               height=64, pady=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        # Logo + title
        logo_frame = tk.Frame(self.header, bg=self.theme.BG_PANEL)
        logo_frame.pack(side="left", padx=20, pady=10)

        tk.Label(logo_frame,
                 text="⬡ BioDiscover",
                 font=("Consolas", 22, "bold"),
                 fg=self.theme.ACCENT_GREEN,
                 bg=self.theme.BG_PANEL).pack(side="left")

        tk.Label(logo_frame,
                 text="  Biotech Discovery Platform",
                 font=("Consolas", 11),
                 fg=self.theme.TEXT_DIM,
                 bg=self.theme.BG_PANEL).pack(side="left", pady=6)

        # Clock / version
        self.clock_label = tk.Label(self.header,
                                    text="",
                                    font=("Consolas", 10),
                                    fg=self.theme.TEXT_DIM,
                                    bg=self.theme.BG_PANEL)
        self.clock_label.pack(side="right", padx=20)
        self._update_clock()

        tk.Label(self.header,
                 text="v1.0 | PhD Edition",
                 font=("Consolas", 9),
                 fg=self.theme.ACCENT_BLUE,
                 bg=self.theme.BG_PANEL).pack(side="right", padx=4)

        # Separator line
        sep = tk.Frame(self.root, bg=self.theme.ACCENT_GREEN, height=2)
        sep.pack(fill="x")

        # ── Body ────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=self.theme.BG_DARK)
        body.pack(fill="both", expand=True)

        # Left sidebar
        self.sidebar = tk.Frame(body, bg=self.theme.BG_PANEL,
                                width=200, pady=10)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content area
        self.content = tk.Frame(body, bg=self.theme.BG_DARK)
        self.content.pack(fill="both", expand=True, side="left")

        # Status bar
        self.status_bar = tk.Frame(self.root, bg=self.theme.BG_PANEL, height=28)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(self.status_bar,
                                     text="● Ready  |  APIs: UniProt · NCBI · PDB · KEGG · Open Food Facts",
                                     font=("Consolas", 9),
                                     fg=self.theme.ACCENT_GREEN,
                                     bg=self.theme.BG_PANEL,
                                     anchor="w")
        self.status_label.pack(side="left", padx=12, pady=4)

    def _build_sidebar(self):
        tk.Label(self.sidebar,
                 text="MODULES",
                 font=("Consolas", 9, "bold"),
                 fg=self.theme.TEXT_DIM,
                 bg=self.theme.BG_PANEL).pack(pady=(16, 4), padx=12, anchor="w")

        modules = [
            ("🏠  Dashboard",    self._show_dashboard),
            ("🧬  Protein Search", self._show_proteins),
            ("🔬  Gene Explorer", self._show_genes),
            ("🗺️  Pathways",     self._show_pathways),
            ("🔷  3D Structures", self._show_structures),
        ]

        self.nav_buttons = []
        for label, command in modules:
            btn = tk.Button(self.sidebar,
                            text=label,
                            font=("Consolas", 10),
                            fg=self.theme.TEXT_MAIN,
                            bg=self.theme.BG_PANEL,
                            activeforeground=self.theme.ACCENT_GREEN,
                            activebackground=self.theme.BG_MID,
                            relief="flat",
                            anchor="w",
                            padx=16,
                            cursor="hand2",
                            command=command)
            btn.pack(fill="x", pady=2)
            self.nav_buttons.append(btn)

        # Separator
        tk.Frame(self.sidebar, bg=self.theme.BG_MID, height=1).pack(
            fill="x", padx=12, pady=16)

        tk.Label(self.sidebar,
                 text="QUICK LINKS",
                 font=("Consolas", 9, "bold"),
                 fg=self.theme.TEXT_DIM,
                 bg=self.theme.BG_PANEL).pack(pady=(0, 4), padx=12, anchor="w")

        links = [
            ("UniProt DB", "https://www.uniprot.org"),
            ("NCBI Gene DB", "https://www.ncbi.nlm.nih.gov/gene"),
            ("RCSB PDB", "https://www.rcsb.org"),
            ("KEGG Pathways", "https://www.kegg.jp"),
            ("AlphaFold DB", "https://alphafold.ebi.ac.uk"),
        ]
        for txt, url in links:
            lbl = tk.Label(self.sidebar,
                           text=f"  ↗ {txt}",
                           font=("Consolas", 9),
                           fg=self.theme.ACCENT_BLUE,
                           bg=self.theme.BG_PANEL,
                           cursor="hand2",
                           anchor="w")
            lbl.pack(fill="x", padx=8, pady=1)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _highlight_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg=self.theme.ACCENT_GREEN, bg=self.theme.BG_MID)
            else:
                btn.configure(fg=self.theme.TEXT_MAIN, bg=self.theme.BG_PANEL)

    def _show_dashboard(self):
        self._clear_content()
        self._highlight_nav(0)
        DashboardPanel(self.content, self.theme, self.set_status)

    def _show_proteins(self):
        self._clear_content()
        self._highlight_nav(1)
        ProteinPanel(self.content, self.theme, self.set_status)

    def _show_genes(self):
        self._clear_content()
        self._highlight_nav(2)
        GenePanel(self.content, self.theme, self.set_status)

    def _show_pathways(self):
        self._clear_content()
        self._highlight_nav(3)
        PathwayPanel(self.content, self.theme, self.set_status)

    def _show_structures(self):
        self._clear_content()
        self._highlight_nav(4)
        StructurePanel(self.content, self.theme, self.set_status)

    def set_status(self, msg, color=None):
        color = color or self.theme.ACCENT_GREEN
        self.status_label.configure(text=f"● {msg}", fg=color)

    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_label.configure(text=now)
        self.root.after(1000, self._update_clock)

    def _on_close(self):
        self.root.destroy()
