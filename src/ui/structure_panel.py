"""
Structure Panel - RCSB PDB 3D Protein Structure Viewer
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

from src.api.pdb_api import PDBAPI


class StructurePanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.pdb = PDBAPI()
        self._build()

    def _build(self):
        header = tk.Frame(self.parent, bg=self.t.BG_PANEL, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="🔷  3D Protein Structure Explorer",
                 font=("Consolas", 18, "bold"),
                 fg=self.t.ACCENT_GREEN,
                 bg=self.t.BG_PANEL).pack(side="left", padx=24)
        tk.Label(header, text="Powered by RCSB PDB",
                 font=("Consolas", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="left")

        # Search
        sf = tk.Frame(self.parent, bg=self.t.BG_DARK, pady=12)
        sf.pack(fill="x", padx=20)
        row = tk.Frame(sf, bg=self.t.BG_DARK)
        row.pack(fill="x")

        self.q = tk.StringVar()
        e = tk.Entry(row, textvariable=self.q,
                     font=("Consolas", 13),
                     bg=self.t.BG_PANEL,
                     fg=self.t.TEXT_MAIN,
                     insertbackground=self.t.ACCENT_GREEN,
                     relief="flat", width=44)
        e.pack(side="left", ipady=8, ipadx=8)
        e.bind("<Return>", self._search)

        tk.Button(row, text=" 🔍 Search PDB ",
                  font=("Consolas", 12, "bold"),
                  bg=self.t.ACCENT_GREEN, fg=self.t.BG_DARK,
                  relief="flat", cursor="hand2",
                  command=self._search).pack(side="left", ipady=6)

        # Info tip
        tk.Label(sf,
                 text="Search by protein name, PDB ID (e.g. 1HHO), or keyword. "
                      "Click any result to open the 3D viewer in browser.",
                 font=("Consolas", 9),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", pady=(4, 0))

        # Paned
        paned = tk.PanedWindow(self.parent, orient="horizontal",
                               bg=self.t.BG_DARK, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=8)

        # List
        left = tk.Frame(paned, bg=self.t.BG_DARK)
        paned.add(left, width=380)
        tk.Label(left, text="STRUCTURES",
                 font=("Consolas", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", padx=6, pady=(4, 2))

        lw = tk.Frame(left, bg=self.t.BG_DARK)
        lw.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(lw, bg=self.t.BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(lw, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=self.t.BG_DARK)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))

        # Detail
        self.detail = tk.Frame(paned, bg=self.t.BG_DARK)
        paned.add(self.detail)
        self._placeholder()

        # Featured structures
        self._show_featured()

    def _show_featured(self):
        featured = [
            {"id": "1HHO", "title": "Hemoglobin", "resolution": "2.10 Å"},
            {"id": "4HHB", "title": "Hemoglobin (deoxy)", "resolution": "1.74 Å"},
            {"id": "1INS", "title": "Insulin", "resolution": "1.50 Å"},
            {"id": "2GS2", "title": "GTPase HRas", "resolution": "2.20 Å"},
            {"id": "3EAM", "title": "p53 DNA-binding domain", "resolution": "1.70 Å"},
            {"id": "6VXX", "title": "SARS-CoV-2 Spike Protein", "resolution": "2.80 Å"},
        ]
        tk.Label(self.inner, text="Featured Structures:",
                 font=("Consolas", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", padx=6, pady=(6, 4))
        for s in featured:
            self._structure_card(s)

    def _search(self, event=None):
        q = self.q.get().strip()
        if not q:
            return
        self.set_status(f"Searching PDB for '{q}'...", self.t.ACCENT_BLUE)
        for w in self.inner.winfo_children():
            w.destroy()
        threading.Thread(target=self._fetch, args=(q,), daemon=True).start()

    def _fetch(self, q):
        try:
            results = self.pdb.search(q, limit=20)
            self.inner.after(0, lambda: self._populate(results))
            self.inner.after(0, lambda: self.set_status(
                f"Found {len(results)} structures."))
        except Exception as ex:
            self.inner.after(0, lambda: self.set_status(
                f"PDB error: {ex}", self.t.ACCENT_RED))

    def _populate(self, results):
        for w in self.inner.winfo_children():
            w.destroy()
        if not results:
            tk.Label(self.inner, text="No structures found.",
                     font=("Consolas", 10),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_DARK).pack(pady=20)
            return
        for s in results:
            self._structure_card(s)

    def _structure_card(self, s):
        card = tk.Frame(self.inner, bg=self.t.BG_CARD, padx=10, pady=8,
                        cursor="hand2")
        card.pack(fill="x", pady=3, padx=4)

        hr = tk.Frame(card, bg=self.t.BG_CARD)
        hr.pack(fill="x")
        tk.Label(hr, text=s.get("id", "?"),
                 font=("Consolas", 13, "bold"),
                 fg=self.t.ACCENT_PURPLE,
                 bg=self.t.BG_CARD).pack(side="left")
        res = s.get("resolution", "")
        if res:
            tk.Label(hr, text=f"  {res}",
                     font=("Consolas", 9),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_CARD).pack(side="right")

        tk.Label(card, text=s.get("title", "")[:65],
                 font=("Consolas", 9),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_CARD,
                 anchor="w").pack(fill="x")

        if s.get("method"):
            tk.Label(card, text=f"Method: {s.get('method','')}",
                     font=("Consolas", 8),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_CARD,
                     anchor="w").pack(fill="x")

        card.bind("<Button-1>", lambda e, st=s: self._show_detail(st))
        for c in card.winfo_children():
            c.bind("<Button-1>", lambda e, st=s: self._show_detail(st))

    def _show_detail(self, s):
        for w in self.detail.winfo_children():
            w.destroy()

        sid = s.get("id", "")

        canvas = tk.Canvas(self.detail, bg=self.t.BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(self.detail, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=self.t.BG_DARK, padx=16, pady=12)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(inner, text=f"🔷 {sid}",
                 font=("Consolas", 24, "bold"),
                 fg=self.t.ACCENT_PURPLE,
                 bg=self.t.BG_DARK).pack(anchor="w")
        tk.Label(inner, text=s.get("title", ""),
                 font=("Consolas", 12),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_DARK,
                 wraplength=500, justify="left").pack(anchor="w", pady=(0, 10))

        # Buttons
        bf = tk.Frame(inner, bg=self.t.BG_DARK, pady=8)
        bf.pack(fill="x")
        for label, url, color in [
            ("🔷 3D Viewer (RCSB)", f"https://www.rcsb.org/3d-view/{sid}", self.t.ACCENT_PURPLE),
            ("📄 PDB Entry",        f"https://www.rcsb.org/structure/{sid}", self.t.ACCENT_BLUE),
            ("🤖 AlphaFold",        f"https://alphafold.ebi.ac.uk/entry/{sid}", self.t.ACCENT_GREEN),
            ("📥 Download PDB",     f"https://files.rcsb.org/download/{sid}.pdb", self.t.ACCENT_ORANGE),
        ]:
            tk.Button(bf, text=label,
                      font=("Consolas", 10),
                      bg=color, fg=self.t.BG_DARK,
                      relief="flat", cursor="hand2",
                      command=lambda u=url: webbrowser.open(u)).pack(
                          side="left", padx=3, ipady=4, ipadx=5)

        # Info rows
        for label, val in [
            ("PDB ID",      sid),
            ("Resolution",  s.get("resolution", "—")),
            ("Method",      s.get("method", "—")),
            ("Released",    s.get("release_date", "—")),
            ("Authors",     s.get("authors", "—")),
        ]:
            row = tk.Frame(inner, bg=self.t.BG_PANEL, pady=6, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:",
                     font=("Consolas", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_PANEL,
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=str(val)[:120],
                     font=("Consolas", 10),
                     fg=self.t.TEXT_MAIN,
                     bg=self.t.BG_PANEL,
                     anchor="w").pack(side="left")

        # Fetch full details
        threading.Thread(target=self._fetch_full,
                         args=(sid, inner), daemon=True).start()

    def _fetch_full(self, sid, inner):
        try:
            detail = self.pdb.get_entry(sid)
            if detail:
                inner.after(0, lambda: self._append_detail(inner, detail))
        except Exception:
            pass

    def _append_detail(self, inner, detail):
        if detail.get("abstract"):
            tk.Label(inner, text="DESCRIPTION",
                     font=("Consolas", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_DARK).pack(anchor="w", pady=(14, 2))
            tk.Label(inner, text=detail["abstract"],
                     font=("Consolas", 10),
                     fg=self.t.TEXT_MAIN,
                     bg=self.t.BG_DARK,
                     wraplength=520,
                     justify="left").pack(anchor="w")

    def _placeholder(self):
        tk.Label(self.detail,
                 text="Select a structure to view details\nor open the 3D viewer.",
                 font=("Consolas", 12),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK,
                 justify="center").pack(expand=True)
