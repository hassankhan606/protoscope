"""
Dashboard Panel - Bright landing screen
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

from src.api.uniprot_api import UniProtAPI
from src.api.ncbi_api import NCBIAPI


class DashboardPanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.uniprot = UniProtAPI()
        self.ncbi = NCBIAPI()
        self._build()

    def _build(self):
        canvas = tk.Canvas(self.parent, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        frame = tk.Frame(canvas, bg=self.t.BG_MAIN)
        cw = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        # Hero
        hero = tk.Frame(frame, bg=self.t.BG_PANEL, pady=36)
        hero.pack(fill="x")
        tk.Frame(hero, bg=self.t.BORDER, height=1).pack(fill="x", side="bottom")

        tk.Label(hero, text="Welcome to BioDiscover",
                 font=("Segoe UI", 26, "bold"),
                 fg=self.t.TEXT_MAIN, bg=self.t.BG_PANEL).pack()
        tk.Label(hero,
                 text="Search proteins · Explore genes · Map pathways · Visualize structures",
                 font=("Segoe UI", 12),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL).pack(pady=6)

        # Search
        sf = tk.Frame(hero, bg=self.t.BG_PANEL)
        sf.pack(pady=16)
        self.q = tk.StringVar()
        e = tk.Entry(sf, textvariable=self.q,
                     font=("Segoe UI", 13),
                     bg=self.t.BG_CARD, fg=self.t.TEXT_MAIN,
                     insertbackground=self.t.ACCENT_TEAL,
                     relief="flat", width=38)
        e.pack(side="left", ipady=10, ipadx=10)
        e.insert(0, "Type a protein, gene or drug name...")
        e.bind("<FocusIn>", lambda ev: e.delete(0,"end") if "Type" in e.get() else None)
        e.bind("<Return>", self._search)
        tk.Button(sf, text=" Search ",
                  font=("Segoe UI", 12, "bold"),
                  bg=self.t.ACCENT_TEAL, fg="#0a1628",
                  relief="flat", cursor="hand2",
                  command=self._search).pack(side="left", ipady=10, ipadx=4)

        chips = tk.Frame(hero, bg=self.t.BG_PANEL)
        chips.pack()
        tk.Label(chips, text="Popular: ",
                 font=("Segoe UI", 9), fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="left")
        for q in ["insulin", "BRCA1", "p53", "hemoglobin", "collagen"]:
            lbl = tk.Label(chips, text=f" {q} ",
                           font=("Segoe UI", 9), fg=self.t.ACCENT_BLUE,
                           bg="#e6f1fb", cursor="hand2", padx=2)
            lbl.pack(side="left", padx=3)
            lbl.bind("<Button-1>", lambda e, v=q: self._fill(v))

        # Stats cards
        stats_f = tk.Frame(frame, bg=self.t.BG_MAIN, padx=24, pady=20)
        stats_f.pack(fill="x")
        tk.Label(stats_f, text="DATABASE STATS",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_MAIN).pack(anchor="w", pady=(0,10))
        row = tk.Frame(stats_f, bg=self.t.BG_MAIN)
        row.pack(fill="x")
        stats = [
            ("250M+",   "Proteins\nUniProt",      self.t.ACCENT_TEAL),
            ("70K+",    "Genes\nNCBI",             self.t.ACCENT_BLUE),
            ("210K+",   "3D Structures\nRCSB PDB", self.t.ACCENT_PURPLE),
            ("500+",    "Pathways\nKEGG",          self.t.ACCENT_AMBER),
            ("200M+",   "AI Models\nAlphaFold",    "#dc2626"),
        ]
        for num, label, color in stats:
            card = tk.Frame(row, bg=self.t.BG_PANEL, padx=16, pady=14, relief="flat")
            card.pack(side="left", expand=True, fill="x", padx=4)
            tk.Frame(card, bg=color, height=3).pack(fill="x")
            tk.Label(card, text=num,
                     font=("Segoe UI", 20, "bold"),
                     fg=color, bg=self.t.BG_PANEL).pack(pady=(8,0))
            tk.Label(card, text=label,
                     font=("Segoe UI", 9),
                     fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL,
                     justify="center").pack()

        # Results
        rf = tk.Frame(frame, bg=self.t.BG_MAIN, padx=24, pady=10)
        rf.pack(fill="x")
        tk.Label(rf, text="QUICK RESULTS",
                 font=("Segoe UI", 9, "bold"),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_MAIN).pack(anchor="w", pady=(0,6))
        self.res_box = tk.Text(rf, height=12,
                               bg=self.t.BG_PANEL, fg=self.t.TEXT_MAIN,
                               font=("Consolas", 10), relief="flat",
                               wrap="word", state="disabled",
                               padx=14, pady=10)
        self.res_box.pack(fill="x")
        self._set_res("Enter a search term above to discover proteins, genes, or pathways.\n\n"
                      "Use the navbar to switch between dedicated modules.\n\n"
                      "Powered by: UniProt · NCBI Entrez · RCSB PDB · KEGG · AlphaFold DB")

    def _fill(self, q):
        self.q.set(q)
        self._search()

    def _search(self, event=None):
        q = self.q.get().strip()
        if not q or "Type" in q:
            return
        self.set_status(f"Searching for '{q}'...", self.t.ACCENT_BLUE)
        self._set_res(f"Searching for: {q} ...\n")
        threading.Thread(target=self._do_search, args=(q,), daemon=True).start()

    def _do_search(self, q):
        lines = []
        try:
            proteins = self.uniprot.search(q, limit=3)
            if proteins:
                lines.append("── PROTEINS (UniProt) ──────────────────────────────\n")
                for p in proteins:
                    lines.append(
                        f"  {p.get('id','?')}  |  {p.get('protein_name','')}\n"
                        f"  Organism: {p.get('organism','')}  |  "
                        f"{p.get('length','')} aa  |  Gene: {p.get('gene_name','')}\n\n")
        except Exception as e:
            lines.append(f"  UniProt error: {e}\n\n")
        try:
            genes = self.ncbi.search_gene(q, limit=3)
            if genes:
                lines.append("── GENES (NCBI) ─────────────────────────────────────\n")
                for g in genes:
                    lines.append(f"  {g.get('name','?')}  |  {g.get('description','')}\n\n")
        except Exception as e:
            lines.append(f"  NCBI error: {e}\n\n")
        text = "".join(lines) if lines else "No results found."
        self.res_box.after(0, lambda: self._set_res(text))
        self.res_box.after(0, lambda: self.set_status(f"Done — '{q}'"))

    def _set_res(self, t):
        self.res_box.configure(state="normal")
        self.res_box.delete("1.0","end")
        self.res_box.insert("end", t)
        self.res_box.configure(state="disabled")
