"""
Protein Panel - Full UniProt protein search and detail viewer
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser

from src.api.uniprot_api import UniProtAPI
from src.api.alphafold_api import AlphaFoldAPI
from src.ui.components import SearchBar, ResultCard, InfoBlock


class ProteinPanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.uniprot = UniProtAPI()
        self.alphafold = AlphaFoldAPI()
        self.current_results = []
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self.parent, bg=self.t.BG_PANEL, pady=16)
        header.pack(fill="x")
        tk.Label(header,
                 text="🧬  Protein Search & Explorer",
                 font=("Consolas", 18, "bold"),
                 fg=self.t.ACCENT_GREEN,
                 bg=self.t.BG_PANEL).pack(side="left", padx=24)

        # Search bar
        search_frame = tk.Frame(self.parent, bg=self.t.BG_DARK, pady=12)
        search_frame.pack(fill="x", padx=20)

        tk.Label(search_frame, text="Protein Name / UniProt ID / Gene:",
                 font=("Consolas", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w")

        input_row = tk.Frame(search_frame, bg=self.t.BG_DARK)
        input_row.pack(fill="x", pady=4)

        self.query_var = tk.StringVar()
        entry = tk.Entry(input_row,
                         textvariable=self.query_var,
                         font=("Consolas", 13),
                         bg=self.t.BG_PANEL,
                         fg=self.t.TEXT_MAIN,
                         insertbackground=self.t.ACCENT_GREEN,
                         relief="flat",
                         width=45)
        entry.pack(side="left", ipady=8, ipadx=8)
        entry.bind("<Return>", self._search)

        # Organism filter
        self.organism_var = tk.StringVar(value="All organisms")
        org_menu = ttk.Combobox(input_row,
                                textvariable=self.organism_var,
                                values=["All organisms", "Human (Homo sapiens)",
                                        "Mouse (Mus musculus)",
                                        "E. coli (Escherichia coli)",
                                        "Yeast (Saccharomyces cerevisiae)",
                                        "Rat (Rattus norvegicus)"],
                                font=("Consolas", 10),
                                width=22, state="readonly")
        org_menu.pack(side="left", padx=8, ipady=6)

        tk.Button(input_row,
                  text=" 🔍 Search ",
                  font=("Consolas", 12, "bold"),
                  bg=self.t.ACCENT_GREEN,
                  fg=self.t.BG_DARK,
                  relief="flat",
                  cursor="hand2",
                  command=self._search).pack(side="left", ipady=6)

        # Main split layout
        paned = tk.PanedWindow(self.parent,
                               orient="horizontal",
                               bg=self.t.BG_DARK,
                               sashwidth=4,
                               sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=10, pady=8)

        # ── Left: results list ──────────────────────────────────────
        left = tk.Frame(paned, bg=self.t.BG_DARK)
        paned.add(left, width=380)

        tk.Label(left,
                 text="RESULTS",
                 font=("Consolas", 9, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(anchor="w", padx=6, pady=(4, 2))

        list_frame = tk.Frame(left, bg=self.t.BG_DARK)
        list_frame.pack(fill="both", expand=True)

        self.results_canvas = tk.Canvas(list_frame,
                                        bg=self.t.BG_DARK,
                                        highlightthickness=0)
        results_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                       command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=results_scroll.set)
        results_scroll.pack(side="right", fill="y")
        self.results_canvas.pack(side="left", fill="both", expand=True)

        self.results_inner = tk.Frame(self.results_canvas, bg=self.t.BG_DARK)
        self.results_canvas.create_window((0, 0), window=self.results_inner,
                                          anchor="nw")
        self.results_inner.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")))

        # ── Right: detail view ──────────────────────────────────────
        self.detail_frame = tk.Frame(paned, bg=self.t.BG_DARK)
        paned.add(self.detail_frame)
        self._show_placeholder()

    def _search(self, event=None):
        query = self.query_var.get().strip()
        if not query:
            return
        organism = self.organism_var.get()
        self.set_status(f"Searching UniProt for '{query}'...", self.t.ACCENT_BLUE)
        for w in self.results_inner.winfo_children():
            w.destroy()
        tk.Label(self.results_inner,
                 text="Fetching data...",
                 font=("Consolas", 10),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK).pack(pady=20)
        threading.Thread(target=self._fetch_proteins,
                         args=(query, organism), daemon=True).start()

    def _fetch_proteins(self, query, organism):
        try:
            results = self.uniprot.search(query, organism=organism, limit=20)
            self.current_results = results
            self.results_inner.after(0, self._populate_results)
        except Exception as e:
            self.results_inner.after(
                0, lambda: self.set_status(f"Error: {e}", self.t.ACCENT_RED))

    def _populate_results(self):
        for w in self.results_inner.winfo_children():
            w.destroy()

        if not self.current_results:
            tk.Label(self.results_inner,
                     text="No results found.",
                     font=("Consolas", 10),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_DARK).pack(pady=20)
            self.set_status("No proteins found.")
            return

        self.set_status(f"Found {len(self.current_results)} proteins.")
        for protein in self.current_results:
            self._make_result_card(protein)

    def _make_result_card(self, protein):
        card = tk.Frame(self.results_inner,
                        bg=self.t.BG_CARD,
                        padx=10, pady=8,
                        cursor="hand2")
        card.pack(fill="x", pady=3, padx=4)

        # Header row
        hrow = tk.Frame(card, bg=self.t.BG_CARD)
        hrow.pack(fill="x")
        tk.Label(hrow,
                 text=protein.get("id", "???"),
                 font=("Consolas", 11, "bold"),
                 fg=self.t.ACCENT_GREEN,
                 bg=self.t.BG_CARD).pack(side="left")
        tk.Label(hrow,
                 text=f"  {protein.get('length','')} aa",
                 font=("Consolas", 9),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_CARD).pack(side="right")

        tk.Label(card,
                 text=protein.get("protein_name", "")[:60],
                 font=("Consolas", 10),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_CARD,
                 anchor="w").pack(fill="x")

        tk.Label(card,
                 text=f"Gene: {protein.get('gene_name','')}  |  "
                      f"{protein.get('organism','')}",
                 font=("Consolas", 9),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_CARD,
                 anchor="w").pack(fill="x")

        card.bind("<Button-1>", lambda e, p=protein: self._show_detail(p))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, p=protein: self._show_detail(p))

    def _show_detail(self, protein):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.detail_frame, bg=self.t.BG_DARK,
                           highlightthickness=0)
        scroll = ttk.Scrollbar(self.detail_frame, orient="vertical",
                               command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.t.BG_DARK, padx=16, pady=12)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))

        uid = protein.get("id", "")

        # Title
        tk.Label(inner,
                 text=f"🧬 {uid}",
                 font=("Consolas", 20, "bold"),
                 fg=self.t.ACCENT_GREEN,
                 bg=self.t.BG_DARK).pack(anchor="w")
        tk.Label(inner,
                 text=protein.get("protein_name", ""),
                 font=("Consolas", 13),
                 fg=self.t.TEXT_MAIN,
                 bg=self.t.BG_DARK,
                 wraplength=540,
                 justify="left").pack(anchor="w", pady=(0, 10))

        # Info grid
        fields = [
            ("Gene Name",      protein.get("gene_name", "—")),
            ("Organism",       protein.get("organism", "—")),
            ("Sequence Length",f"{protein.get('length', '—')} amino acids"),
            ("UniProt ID",     uid),
            ("Reviewed",       protein.get("reviewed", "—")),
            ("Function",       protein.get("function", "—")),
        ]

        for label, value in fields:
            row = tk.Frame(inner, bg=self.t.BG_PANEL, pady=6, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:",
                     font=("Consolas", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_PANEL,
                     width=16, anchor="w").pack(side="left")
            tk.Label(row, text=str(value),
                     font=("Consolas", 10),
                     fg=self.t.TEXT_MAIN,
                     bg=self.t.BG_PANEL,
                     wraplength=400,
                     justify="left",
                     anchor="w").pack(side="left", fill="x")

        # Action buttons
        btn_frame = tk.Frame(inner, bg=self.t.BG_DARK, pady=10)
        btn_frame.pack(fill="x")

        def open_uniprot():
            webbrowser.open(f"https://www.uniprot.org/uniprot/{uid}")

        def open_alphafold():
            webbrowser.open(f"https://alphafold.ebi.ac.uk/entry/{uid}")

        def open_pdb():
            webbrowser.open(f"https://www.rcsb.org/search?query={uid}")

        for label, cmd, color in [
            ("🌐 UniProt Page", open_uniprot, self.t.ACCENT_BLUE),
            ("🤖 AlphaFold",    open_alphafold, self.t.ACCENT_PURPLE),
            ("🔷 PDB Search",   open_pdb,       self.t.ACCENT_ORANGE),
        ]:
            tk.Button(btn_frame,
                      text=label,
                      font=("Consolas", 10),
                      bg=color,
                      fg=self.t.BG_DARK,
                      relief="flat",
                      cursor="hand2",
                      command=cmd).pack(side="left", padx=4, ipady=4, ipadx=6)

        # Fetch full details in background
        self.set_status(f"Loading full details for {uid}...", self.t.ACCENT_BLUE)
        threading.Thread(target=self._fetch_full_detail,
                         args=(uid, inner), daemon=True).start()

    def _fetch_full_detail(self, uid, inner):
        try:
            detail = self.uniprot.get_protein_detail(uid)
            if detail:
                inner.after(0, lambda: self._append_detail(inner, detail))
            self.set_status(f"Details loaded for {uid}.")
        except Exception as e:
            self.set_status(f"Detail error: {e}", self.t.ACCENT_RED)

    def _append_detail(self, inner, detail):
        if detail.get("sequence"):
            tk.Label(inner,
                     text="AMINO ACID SEQUENCE",
                     font=("Consolas", 9, "bold"),
                     fg=self.t.TEXT_DIM,
                     bg=self.t.BG_DARK).pack(anchor="w", pady=(14, 2))

            seq_box = tk.Text(inner,
                              height=6,
                              font=("Consolas", 9),
                              bg=self.t.BG_PANEL,
                              fg=self.t.ACCENT_GREEN,
                              relief="flat",
                              wrap="word",
                              state="disabled",
                              padx=8, pady=6)
            seq_box.pack(fill="x")
            seq_box.configure(state="normal")
            seq = detail["sequence"]
            # Format in blocks of 10
            formatted = " ".join(seq[i:i+10] for i in range(0, len(seq), 10))
            seq_box.insert("end", formatted)
            seq_box.configure(state="disabled")

    def _show_placeholder(self):
        tk.Label(self.detail_frame,
                 text="Select a protein from the results list\nto see detailed information.",
                 font=("Consolas", 12),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_DARK,
                 justify="center").pack(expand=True)
