"""
Dashboard Panel - Landing screen with stats and quick search
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
        # Scrollable canvas
        canvas = tk.Canvas(self.parent, bg=self.t.BG_DARK,
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas, bg=self.t.BG_DARK)
        canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def _on_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_resize)
        frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Hero section
        hero = tk.Frame(frame, bg=self.t.BG_PANEL, pady=40)
        hero.pack(fill="x", padx=0)

        tk.Label(hero,
                 text="⬡  Welcome to BioDiscover",
                 font=("Consolas", 28, "bold"),
                 fg=self.t.ACCENT_GREEN,
                 bg=self.t.BG_PANEL).pack()

        tk.Label(hero,
                 text="Your AI-powered biotech research companion · Proteins · Genes · Pathways · Structures",
                 font=("Consolas", 12),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(pady=8)

        # Quick search bar
        search_frame = tk.Frame(hero, bg=self.t.BG_PANEL)
        search_frame.pack(pady=20)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                font=("Consolas", 14),
                                bg=self.t.BG_MID,
                                fg=self.t.TEXT_MAIN,
                                insertbackground=self.t.ACCENT_GREEN,
                                relief="flat",
                                width=40,
                                bd=0)
        search_entry.pack(side="left", ipady=10, ipadx=12)
        search_entry.insert(0, "Search proteins, genes, pathways...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end")
                          if search_entry.get().startswith("Search") else None)
        search_entry.bind("<Return>", self._quick_search)

        search_btn = tk.Button(search_frame,
                               text="  🔍 Search  ",
                               font=("Consolas", 13, "bold"),
                               bg=self.t.ACCENT_GREEN,
                               fg=self.t.BG_DARK,
                               relief="flat",
                               cursor="hand2",
                               command=self._quick_search)
        search_btn.pack(side="left", ipady=10, ipadx=4)

        # Molecule examples as chips
        chips_frame = tk.Frame(hero, bg=self.t.BG_PANEL)
        chips_frame.pack()
        tk.Label(chips_frame, text="Try: ",
                 font=("Consolas", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL).pack(side="left")
        for example in ["insulin", "BRCA1", "p53", "hemoglobin", "ATP synthase"]:
            chip = tk.Label(chips_frame,
                            text=f" {example} ",
                            font=("Consolas", 10),
                            fg=self.t.ACCENT_BLUE,
                            bg=self.t.BG_MID,
                            cursor="hand2",
                            padx=4, pady=2)
            chip.pack(side="left", padx=3)
            chip.bind("<Button-1>", lambda e, q=example: self._fill_search(q))

        # Stats row
        stats_frame = tk.Frame(frame, bg=self.t.BG_DARK, pady=16)
        stats_frame.pack(fill="x", padx=30)
        tk.Label(stats_frame,
                 text="DATABASE STATS",
                 font=("Consolas", 10, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", pady=(0, 10))

        cards_row = tk.Frame(stats_frame, bg=self.t.BG_DARK)
        cards_row.pack(fill="x")
        stats = [
            ("🧬", "250M+",   "Protein Sequences\n(UniProt)"),
            ("🔬", "70,000+", "Gene Records\n(NCBI)"),
            ("🔷", "210,000+","3D Structures\n(PDB)"),
            ("🗺️", "500+",    "KEGG Pathways"),
            ("🤖", "200M+",   "AlphaFold Models"),
        ]
        for icon, number, label in stats:
            card = tk.Frame(cards_row,
                            bg=self.t.BG_CARD,
                            padx=20, pady=16,
                            relief="flat")
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, text=icon,
                     font=("Consolas", 22),
                     bg=self.t.BG_CARD,
                     fg=self.t.ACCENT_GREEN).pack()
            tk.Label(card, text=number,
                     font=("Consolas", 18, "bold"),
                     bg=self.t.BG_CARD,
                     fg=self.t.TEXT_MAIN).pack()
            tk.Label(card, text=label,
                     font=("Consolas", 9),
                     bg=self.t.BG_CARD,
                     fg=self.t.TEXT_DIM,
                     justify="center").pack()

        # Quick results area
        results_frame = tk.Frame(frame, bg=self.t.BG_DARK, pady=10)
        results_frame.pack(fill="x", padx=30)
        tk.Label(results_frame,
                 text="QUICK RESULTS",
                 font=("Consolas", 10, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", pady=(0, 6))

        self.results_box = tk.Text(results_frame,
                                   height=14,
                                   bg=self.t.BG_PANEL,
                                   fg=self.t.TEXT_MAIN,
                                   font=("Consolas", 10),
                                   relief="flat",
                                   wrap="word",
                                   state="disabled",
                                   padx=14, pady=12)
        self.results_box.pack(fill="x")
        self._set_result("Enter a search term above to discover proteins, genes, or pathways.\n\n"
                         "Use the sidebar to access specialized modules with detailed analysis.\n\n"
                         "Powered by: UniProt API · NCBI Entrez · RCSB PDB · KEGG · AlphaFold DB")

    def _fill_search(self, text):
        self.search_var.set(text)
        self._quick_search()

    def _quick_search(self, event=None):
        query = self.search_var.get().strip()
        if not query or query.startswith("Search"):
            return
        self.set_status(f"Searching for '{query}'...", self.t.ACCENT_BLUE)
        self._set_result(f"Searching for: {query} ...\n")
        threading.Thread(target=self._do_search, args=(query,), daemon=True).start()

    def _do_search(self, query):
        results = []

        # UniProt search
        try:
            proteins = self.uniprot.search(query, limit=3)
            if proteins:
                results.append("═══ PROTEINS (UniProt) ════════════════════════\n")
                for p in proteins:
                    results.append(
                        f"  ▶ {p.get('id','N/A')} | {p.get('protein_name','')}\n"
                        f"    Organism: {p.get('organism','')}\n"
                        f"    Length: {p.get('length','')} aa  |  "
                        f"Gene: {p.get('gene_name','')}\n\n"
                    )
        except Exception as e:
            results.append(f"  UniProt error: {e}\n\n")

        # NCBI Gene search
        try:
            genes = self.ncbi.search_gene(query, limit=3)
            if genes:
                results.append("═══ GENES (NCBI) ══════════════════════════════\n")
                for g in genes:
                    results.append(
                        f"  ▶ {g.get('name','N/A')} (ID: {g.get('uid','')})\n"
                        f"    {g.get('description','')}\n\n"
                    )
        except Exception as e:
            results.append(f"  NCBI error: {e}\n\n")

        text = "".join(results) if results else "No results found."
        self.results_box.after(0, lambda: self._set_result(text))
        self.results_box.after(0, lambda: self.set_status(
            f"Search complete for '{query}'"))

    def _set_result(self, text):
        self.results_box.configure(state="normal")
        self.results_box.delete("1.0", "end")
        self.results_box.insert("end", text)
        self.results_box.configure(state="disabled")
