"""
Pathway Panel - KEGG Biological Pathway Explorer
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

from src.api.kegg_api import KEGGAPI


class PathwayPanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.kegg = KEGGAPI()
        self._build()

    def _build(self):
        header = tk.Frame(self.parent, bg=self.t.BG_PANEL, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="🗺️  Biological Pathway Explorer",
                 font=("Segoe UI", 18, "bold"),
                 fg=self.t.ACCENT_TEAL,
                 bg=self.t.BG_PANEL).pack(side="left", padx=24)
        tk.Label(header, text="Powered by KEGG",
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="left")

        # Controls
        cf = tk.Frame(self.parent, bg=self.t.BG_MAIN, pady=12)
        cf.pack(fill="x", padx=20)
        row = tk.Frame(cf, bg=self.t.BG_MAIN)
        row.pack(fill="x")

        self.q = tk.StringVar()
        e = tk.Entry(row, textvariable=self.q,
                     font=("Segoe UI", 13),
                     bg=self.t.BG_PANEL,
                     fg=self.t.TEXT_MAIN,
                     insertbackground=self.t.ACCENT_TEAL,
                     relief="flat", width=40)
        e.pack(side="left", ipady=8, ipadx=8)
        e.bind("<Return>", self._search)

        self.org_var = tk.StringVar(value="hsa")
        org_menu = ttk.Combobox(row,
                                textvariable=self.org_var,
                                values=["hsa (Human)", "mmu (Mouse)", "eco (E. coli)",
                                        "sce (Yeast)", "dme (Drosophila)"],
                                width=16, state="readonly",
                                font=("Segoe UI", 10))
        org_menu.pack(side="left", padx=8, ipady=6)

        tk.Button(row, text=" 🔍 Search ",
                  font=("Segoe UI", 12, "bold"),
                  bg=self.t.ACCENT_TEAL,
                  fg=self.t.BG_MAIN,
                  relief="flat", cursor="hand2",
                  command=self._search).pack(side="left", ipady=6)

        # Browse categories button
        tk.Button(row, text=" 📋 Browse All ",
                  font=("Segoe UI", 12),
                  bg=self.t.BG_PANEL,
                  fg=self.t.TEXT_MAIN,
                  relief="flat", cursor="hand2",
                  command=self._browse_all).pack(side="left", padx=8, ipady=6)

        # Paned view
        paned = tk.PanedWindow(self.parent, orient="horizontal",
                               bg=self.t.BG_MAIN, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=8)

        # List
        left = tk.Frame(paned, bg=self.t.BG_MAIN)
        paned.add(left, width=360)
        tk.Label(left, text="PATHWAYS",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(anchor="w", padx=6, pady=(4, 2))

        lw = tk.Frame(left, bg=self.t.BG_MAIN)
        lw.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(lw, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(lw, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=self.t.BG_MAIN)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))

        # Detail
        self.detail = tk.Frame(paned, bg=self.t.BG_MAIN)
        paned.add(self.detail)
        tk.Label(self.detail,
                 text="Select a pathway to explore it.",
                 font=("Segoe UI", 12),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(expand=True)

        # Load featured pathways on startup
        threading.Thread(target=self._load_featured, daemon=True).start()

    def _load_featured(self):
        featured = [
            "Glycolysis", "TCA cycle", "MAPK signaling",
            "p53 signaling", "Insulin signaling", "Apoptosis"
        ]
        self.inner.after(0, lambda: self._show_chips(featured))

    def _show_chips(self, items):
        tk.Label(self.inner, text="Featured Pathways:",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(anchor="w", padx=6, pady=6)
        for item in items:
            chip = tk.Label(self.inner,
                            text=f"  ► {item}  ",
                            font=("Segoe UI", 10),
                            fg=self.t.ACCENT_ORANGE,
                            bg=self.t.BG_PANEL,
                            cursor="hand2",
                            pady=6)
            chip.pack(fill="x", padx=4, pady=2)
            chip.bind("<Button-1>",
                      lambda e, q=item: self._set_query_search(q))

    def _set_query_search(self, q):
        self.q.set(q)
        self._search()

    def _search(self, event=None):
        q = self.q.get().strip()
        if not q:
            return
        org = self.org_var.get().split()[0]
        self.set_status(f"Searching KEGG for '{q}'...", self.t.ACCENT_BLUE)
        for w in self.inner.winfo_children():
            w.destroy()
        threading.Thread(target=self._fetch,
                         args=(q, org), daemon=True).start()

    def _fetch(self, q, org):
        try:
            results = self.kegg.search_pathway(q, org=org)
            self.inner.after(0, lambda: self._populate(results))
            self.inner.after(0, lambda: self.set_status(
                f"Found {len(results)} pathways."))
        except Exception as ex:
            self.inner.after(0, lambda: self.set_status(
                f"KEGG error: {ex}", self.t.ACCENT_RED))

    def _browse_all(self):
        self.set_status("Loading KEGG pathway list...", self.t.ACCENT_BLUE)
        threading.Thread(target=self._fetch_all, daemon=True).start()

    def _fetch_all(self):
        try:
            org = self.org_var.get().split()[0]
            results = self.kegg.list_pathways(org=org)
            self.inner.after(0, lambda: self._populate(results[:50]))
            self.inner.after(0, lambda: self.set_status(
                f"Showing 50 of {len(results)} pathways."))
        except Exception as ex:
            self.inner.after(0, lambda: self.set_status(
                f"Error: {ex}", self.t.ACCENT_RED))

    def _populate(self, results):
        for w in self.inner.winfo_children():
            w.destroy()
        if not results:
            tk.Label(self.inner, text="No pathways found.",
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_MAIN).pack(pady=20)
            return
        for pathway in results:
            self._pathway_card(pathway)

    def _pathway_card(self, pathway):
        card = tk.Frame(self.inner, bg=self.t.BG_PANEL, padx=10, pady=8,
                        cursor="hand2")
        card.pack(fill="x", pady=3, padx=4)

        tk.Label(card, text=pathway.get("name", "?"),
                 font=("Segoe UI", 10, "bold"),
                 fg=self.t.ACCENT_ORANGE,
                 bg=self.t.BG_PANEL,
                 anchor="w").pack(fill="x")
        tk.Label(card, text=f"ID: {pathway.get('id','—')}",
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL,
                 anchor="w").pack(fill="x")

        card.bind("<Button-1>", lambda e, p=pathway: self._show_detail(p))
        for c in card.winfo_children():
            c.bind("<Button-1>", lambda e, p=pathway: self._show_detail(p))

    def _show_detail(self, pathway):
        for w in self.detail.winfo_children():
            w.destroy()

        pid = pathway.get("id", "")
        pname = pathway.get("name", "")

        canvas = tk.Canvas(self.detail, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(self.detail, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=self.t.BG_MAIN, padx=16, pady=12)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(inner, text=f"🗺️ {pname}",
                 font=("Segoe UI", 18, "bold"),
                 fg=self.t.ACCENT_ORANGE,
                 bg=self.t.BG_MAIN,
                 wraplength=500).pack(anchor="w")
        tk.Label(inner, text=f"KEGG ID: {pid}",
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(anchor="w", pady=(0, 12))

        bf = tk.Frame(inner, bg=self.t.BG_MAIN, pady=6)
        bf.pack(fill="x")

        kegg_url = f"https://www.kegg.jp/pathway/{pid}"
        wiki_q   = pname.replace(" ", "_") + "_pathway"

        for label, url, color in [
            ("🗺️ KEGG Map",      kegg_url,                          self.t.ACCENT_ORANGE),
            ("🌐 KEGG Entry",    f"https://www.genome.jp/entry/{pid}", self.t.ACCENT_BLUE),
            ("📖 Wikipedia",     f"https://en.wikipedia.org/wiki/{wiki_q}", self.t.ACCENT_PURPLE),
        ]:
            tk.Button(bf, text=label,
                      font=("Segoe UI", 10),
                      bg=color, fg=self.t.BG_MAIN,
                      relief="flat", cursor="hand2",
                      command=lambda u=url: webbrowser.open(u)).pack(
                          side="left", padx=4, ipady=4, ipadx=6)

        # Fetch details in background
        threading.Thread(target=self._fetch_detail,
                         args=(pid, inner), daemon=True).start()

    def _fetch_detail(self, pid, inner):
        try:
            details = self.kegg.get_pathway_info(pid)
            if details:
                inner.after(0, lambda: self._append_info(inner, details))
        except Exception as ex:
            pass

    def _append_info(self, inner, info):
        for label, val in info.items():
            if not val:
                continue
            row = tk.Frame(inner, bg=self.t.BG_PANEL, pady=6, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:",
                     font=("Segoe UI", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_PANEL,
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=str(val)[:200],
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_MAIN,
                     bg=self.t.BG_PANEL,
                     wraplength=420,
                     justify="left",
                     anchor="w").pack(side="left", fill="x")
