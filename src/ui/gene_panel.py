"""
Gene Panel - NCBI Gene Explorer
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

from src.api.ncbi_api import NCBIAPI


class GenePanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.ncbi = NCBIAPI()
        self._build()

    def _build(self):
        header = tk.Frame(self.parent, bg=self.t.BG_PANEL, pady=16)
        header.pack(fill="x")
        tk.Label(header,
                 text="🔬  Gene Explorer",
                 font=("Segoe UI", 18, "bold"),
                 fg=self.t.ACCENT_TEAL,
                 bg=self.t.BG_PANEL).pack(side="left", padx=24)
        tk.Label(header,
                 text="Powered by NCBI Entrez",
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="left")

        # Search
        sf = tk.Frame(self.parent, bg=self.t.BG_MAIN, pady=12)
        sf.pack(fill="x", padx=20)

        row = tk.Frame(sf, bg=self.t.BG_MAIN)
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

        self.sp_var = tk.StringVar(value="9606")   # human
        sp_menu = ttk.Combobox(row,
                               textvariable=self.sp_var,
                               values=["9606 (Human)", "10090 (Mouse)",
                                       "10116 (Rat)", "4932 (Yeast)",
                                       "511145 (E. coli K-12)", "7227 (Drosophila)"],
                               width=20, state="readonly",
                               font=("Segoe UI", 10))
        sp_menu.pack(side="left", padx=8, ipady=6)

        tk.Button(row, text=" 🔍 Search ",
                  font=("Segoe UI", 12, "bold"),
                  bg=self.t.ACCENT_TEAL,
                  fg=self.t.BG_MAIN,
                  relief="flat",
                  cursor="hand2",
                  command=self._search).pack(side="left", ipady=6)

        # Results area
        paned = tk.PanedWindow(self.parent, orient="horizontal",
                               bg=self.t.BG_MAIN, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=8)

        # List
        left = tk.Frame(paned, bg=self.t.BG_MAIN)
        paned.add(left, width=360)
        tk.Label(left, text="RESULTS",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(anchor="w", padx=6, pady=(4, 2))

        list_wrap = tk.Frame(left, bg=self.t.BG_MAIN)
        list_wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(list_wrap, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(list_wrap, orient="vertical", command=self.canvas.yview)
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
                 text="Select a gene to see details.",
                 font=("Segoe UI", 12),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(expand=True)

    def _search(self, event=None):
        q = self.q.get().strip()
        if not q:
            return
        sp_raw = self.sp_var.get().split()[0]   # taxon id
        self.set_status(f"Searching NCBI Gene for '{q}'...", self.t.ACCENT_BLUE)
        for w in self.inner.winfo_children():
            w.destroy()
        threading.Thread(target=self._fetch,
                         args=(q, sp_raw), daemon=True).start()

    def _fetch(self, q, taxid):
        try:
            results = self.ncbi.search_gene(q, taxid=taxid, limit=20)
            self.inner.after(0, lambda: self._populate(results))
            self.inner.after(0, lambda: self.set_status(
                f"Found {len(results)} genes."))
        except Exception as ex:
            self.inner.after(0, lambda: self.set_status(
                f"NCBI error: {ex}", self.t.ACCENT_RED))

    def _populate(self, results):
        for w in self.inner.winfo_children():
            w.destroy()
        if not results:
            tk.Label(self.inner, text="No genes found.",
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_MAIN).pack(pady=20)
            return
        for gene in results:
            self._gene_card(gene)

    def _gene_card(self, gene):
        card = tk.Frame(self.inner, bg=self.t.BG_PANEL, padx=10, pady=8, cursor="hand2")
        card.pack(fill="x", pady=3, padx=4)

        hr = tk.Frame(card, bg=self.t.BG_PANEL)
        hr.pack(fill="x")
        tk.Label(hr, text=gene.get("name", "?"),
                 font=("Segoe UI", 12, "bold"),
                 fg=self.t.ACCENT_BLUE,
                 bg=self.t.BG_PANEL).pack(side="left")
        tk.Label(hr, text=f"  ID: {gene.get('uid','')}",
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="right")

        tk.Label(card, text=gene.get("description", "")[:70],
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_PANEL,
                 anchor="w").pack(fill="x")

        card.bind("<Button-1>", lambda e, g=gene: self._show_detail(g))
        for c in card.winfo_children():
            c.bind("<Button-1>", lambda e, g=gene: self._show_detail(g))

    def _show_detail(self, gene):
        for w in self.detail.winfo_children():
            w.destroy()

        uid = gene.get("uid", "")
        name = gene.get("name", "")

        canvas = tk.Canvas(self.detail, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(self.detail, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=self.t.BG_MAIN, padx=16, pady=12)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(inner, text=f"🔬 {name}",
                 font=("Segoe UI", 20, "bold"),
                 fg=self.t.ACCENT_BLUE,
                 bg=self.t.BG_MAIN).pack(anchor="w")
        tk.Label(inner, text=gene.get("description", ""),
                 font=("Segoe UI", 12),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_MAIN,
                 wraplength=500, justify="left").pack(anchor="w", pady=(0, 10))

        for label, val in [
            ("NCBI Gene ID", uid),
            ("Symbol",       name),
            ("Full Name",    gene.get("description", "—")),
            ("Status",       gene.get("status", "—")),
        ]:
            row = tk.Frame(inner, bg=self.t.BG_PANEL, pady=6, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:",
                     font=("Segoe UI", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_PANEL,
                     width=14, anchor="w").pack(side="left")
            tk.Label(row, text=str(val),
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_MAIN,
                     bg=self.t.BG_PANEL,
                     anchor="w").pack(side="left")

        # Links
        bf = tk.Frame(inner, bg=self.t.BG_MAIN, pady=10)
        bf.pack(fill="x")
        for label, url, color in [
            ("🌐 NCBI Gene", f"https://www.ncbi.nlm.nih.gov/gene/{uid}", self.t.ACCENT_BLUE),
            ("🧬 UniProt",  f"https://www.uniprot.org/uniprot/?query=gene:{name}", self.t.ACCENT_TEAL),
            ("🗺️ KEGG",     f"https://www.genome.jp/dbget-bin/www_bget?hsa:{name}", self.t.ACCENT_ORANGE),
        ]:
            tk.Button(bf, text=label,
                      font=("Segoe UI", 10),
                      bg=color, fg=self.t.BG_MAIN,
                      relief="flat", cursor="hand2",
                      command=lambda u=url: webbrowser.open(u)).pack(
                          side="left", padx=4, ipady=4, ipadx=6)
