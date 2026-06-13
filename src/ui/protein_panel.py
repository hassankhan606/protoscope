"""
Protein Panel - Bright UI with Name → Desc → Summary + Molecule Image panel
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
import math

from src.api.uniprot_api import UniProtAPI
from src.api.alphafold_api import AlphaFoldAPI


class ProteinPanel:
    def __init__(self, parent, theme, set_status):
        self.parent = parent
        self.t = theme
        self.set_status = set_status
        self.uniprot = UniProtAPI()
        self.alphafold = AlphaFoldAPI()
        self.results = []
        self._build()

    def _build(self):
        # ── Search bar row ──────────────────────────────────────────
        sb = tk.Frame(self.parent, bg=self.t.BG_PANEL,
                      pady=12, padx=20)
        sb.pack(fill="x")
        tk.Frame(self.parent, bg=self.t.BORDER, height=1).pack(fill="x")

        tk.Label(sb, text="Search Proteins",
                 font=("Segoe UI", 13, "bold"),
                 fg=self.t.TEXT_MAIN, bg=self.t.BG_PANEL).pack(anchor="w")
        tk.Label(sb, text="UniProt · 250 million sequences",
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL).pack(anchor="w")

        row = tk.Frame(sb, bg=self.t.BG_PANEL)
        row.pack(fill="x", pady=(8, 0))

        self.q = tk.StringVar()
        entry = tk.Entry(row, textvariable=self.q,
                         font=("Segoe UI", 12),
                         bg=self.t.BG_CARD,
                         fg=self.t.TEXT_MAIN,
                         insertbackground=self.t.ACCENT_TEAL,
                         relief="flat", bd=0, width=38)
        entry.pack(side="left", ipady=9, ipadx=10)
        entry.bind("<Return>", self._search)

        # Organism dropdown
        self.org = tk.StringVar(value="Human")
        ttk.Combobox(row, textvariable=self.org,
                     values=["Human", "Mouse", "E. coli", "Yeast", "Rat"],
                     width=12, state="readonly",
                     font=("Segoe UI", 10)).pack(side="left", padx=8, ipady=7)

        tk.Button(row, text="Search",
                  font=("Segoe UI", 11, "bold"),
                  bg=self.t.ACCENT_TEAL, fg="#0a1628",
                  relief="flat", cursor="hand2", padx=18,
                  command=self._search).pack(side="left", ipady=7)

        # Filter chips
        chips_f = tk.Frame(sb, bg=self.t.BG_PANEL)
        chips_f.pack(fill="x", pady=(8, 0))
        tk.Label(chips_f, text="Try: ",
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL).pack(side="left")
        for q in ["insulin", "p53", "hemoglobin", "BRCA1", "ATP synthase", "collagen"]:
            c = tk.Label(chips_f, text=f" {q} ",
                         font=("Segoe UI", 9),
                         fg=self.t.ACCENT_BLUE,
                         bg="#e6f1fb", cursor="hand2", padx=2, pady=2)
            c.pack(side="left", padx=3)
            c.bind("<Button-1>", lambda e, v=q: self._quick(v))

        # ── Main split ─────────────────────────────────────────────
        paned = tk.PanedWindow(self.parent, orient="horizontal",
                               bg=self.t.BG_MAIN, sashwidth=4,
                               sashrelief="flat")
        paned.pack(fill="both", expand=True)

        # Left: results list
        left = tk.Frame(paned, bg=self.t.BG_MAIN)
        paned.add(left, width=300)

        tk.Label(left, text="RESULTS",
                 font=("Segoe UI", 8, "bold"),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_MAIN).pack(anchor="w", padx=10, pady=(10, 4))

        lf = tk.Frame(left, bg=self.t.BG_MAIN)
        lf.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(lf, bg=self.t.BG_MAIN, highlightthickness=0)
        sc = ttk.Scrollbar(lf, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sc.set)
        sc.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=self.t.BG_MAIN)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))

        # Right: detail pane
        self.detail = tk.Frame(paned, bg=self.t.BG_MAIN)
        paned.add(self.detail)
        self._placeholder()

    def _quick(self, q):
        self.q.set(q)
        self._search()

    def _search(self, event=None):
        q = self.q.get().strip()
        if not q:
            return
        self.set_status(f"Searching UniProt for '{q}'...", self.t.ACCENT_BLUE)
        for w in self.inner.winfo_children():
            w.destroy()
        tk.Label(self.inner, text="Fetching...",
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_MAIN).pack(pady=20)
        org = self.org.get()
        threading.Thread(target=self._fetch, args=(q, org), daemon=True).start()

    def _fetch(self, q, org):
        try:
            self.results = self.uniprot.search(q, organism=org, limit=20)
            self.inner.after(0, self._populate)
        except Exception as e:
            self.inner.after(0, lambda: self.set_status(str(e), self.t.ACCENT_RED))

    def _populate(self):
        for w in self.inner.winfo_children():
            w.destroy()
        if not self.results:
            tk.Label(self.inner, text="No results.",
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_DIM, bg=self.t.BG_MAIN).pack(pady=20)
            return
        self.set_status(f"Found {len(self.results)} proteins.")
        for p in self.results:
            self._card(p)

    def _card(self, p):
        card = tk.Frame(self.inner, bg=self.t.BG_PANEL,
                        padx=10, pady=8, cursor="hand2",
                        relief="flat")
        card.pack(fill="x", pady=2, padx=6)
        tk.Frame(card, bg=self.t.BORDER, height=0).pack(fill="x")

        hr = tk.Frame(card, bg=self.t.BG_PANEL)
        hr.pack(fill="x")
        tk.Label(hr, text=p.get("id", ""),
                 font=("Consolas", 11, "bold"),
                 fg=self.t.ACCENT_TEAL, bg=self.t.BG_PANEL).pack(side="left")
        tk.Label(hr, text=f"{p.get('length','')} aa",
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL).pack(side="right")

        tk.Label(card, text=p.get("protein_name", "")[:55],
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_MAIN, bg=self.t.BG_PANEL,
                 anchor="w").pack(fill="x")
        tk.Label(card, text=p.get("organism", ""),
                 font=("Segoe UI", 9),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL,
                 anchor="w").pack(fill="x")

        # Bottom border
        tk.Frame(card, bg=self.t.BORDER, height=1).pack(fill="x", pady=(6, 0))

        for w in [card] + card.winfo_children():
            w.bind("<Button-1>", lambda e, pr=p: self._detail(pr))

    def _detail(self, p):
        for w in self.detail.winfo_children():
            w.destroy()

        uid = p.get("id", "")

        # Scrollable right pane
        c = tk.Canvas(self.detail, bg=self.t.BG_MAIN, highlightthickness=0)
        sb = ttk.Scrollbar(self.detail, orient="vertical", command=c.yview)
        c.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        c.pack(side="left", fill="both", expand=True)
        outer = tk.Frame(c, bg=self.t.BG_MAIN)
        c.create_window((0, 0), window=outer, anchor="nw")
        outer.bind("<Configure>",
                   lambda e: c.configure(scrollregion=c.bbox("all")))

        # ── Top: Name + image side by side ─────────────────────────
        top = tk.Frame(outer, bg=self.t.BG_PANEL, pady=16, padx=20)
        top.pack(fill="x")
        tk.Frame(outer, bg=self.t.BORDER, height=1).pack(fill="x")

        left_info = tk.Frame(top, bg=self.t.BG_PANEL)
        left_info.pack(side="left", fill="both", expand=True)

        # ── NAME ───────────────────────────────────────────────────
        tk.Label(left_info, text="NAME",
                 font=("Segoe UI", 8, "bold"),
                 fg=self.t.SECTION_LABEL,
                 bg=self.t.BG_PANEL).pack(anchor="w")
        tk.Label(left_info,
                 text=p.get("protein_name", uid),
                 font=("Segoe UI", 18, "bold"),
                 fg=self.t.TEXT_MAIN, bg=self.t.BG_PANEL,
                 wraplength=380, justify="left").pack(anchor="w")

        # meta pills
        meta = tk.Frame(left_info, bg=self.t.BG_PANEL)
        meta.pack(anchor="w", pady=(4, 0))
        for txt, color in [
            (uid, "#e1f5ee"), 
            (p.get("organism",""), "#e6f1fb"),
            (f"{p.get('length','')} aa", "#f1f4f9"),
            (f"Gene: {p.get('gene_name','')}", "#faeeda"),
        ]:
            if not txt.strip():
                continue
            tk.Label(meta, text=f" {txt} ",
                     font=("Segoe UI", 9),
                     fg=self.t.TEXT_MAIN,
                     bg=color, padx=2, pady=2).pack(side="left", padx=2)

        # ── Molecule image (right side) ─────────────────────────────
        img_frame = tk.Frame(top, bg=self.t.BG_DARK,
                             width=160, height=160,
                             relief="flat")
        img_frame.pack(side="right", padx=(20, 0))
        img_frame.pack_propagate(False)

        mol_c = tk.Canvas(img_frame, width=160, height=160,
                          bg=self.t.BG_DARK, highlightthickness=0)
        mol_c.pack()
        self._draw_molecule(mol_c, uid)

        # Name label under molecule
        mol_label_f = tk.Frame(top, bg=self.t.BG_PANEL)
        # We'll place label below via packing order workaround
        # Actually pack below img_frame
        name_lbl_f = tk.Frame(outer, bg=self.t.BG_PANEL)
        # Place molecule name right-aligned
        tk.Label(top, text=p.get("protein_name","")[:20],
                 font=("Segoe UI", 8),
                 fg=self.t.TEXT_DIM,
                 bg=self.t.BG_PANEL,
                 wraplength=160, justify="center").place(
                     in_=img_frame, relx=0.5, rely=1.05, anchor="n")

        # ── Action buttons ─────────────────────────────────────────
        bf = tk.Frame(left_info, bg=self.t.BG_PANEL)
        bf.pack(anchor="w", pady=(10, 0))
        for label, url, bg in [
            ("UniProt", f"https://www.uniprot.org/uniprot/{uid}", self.t.ACCENT_TEAL),
            ("AlphaFold", f"https://alphafold.ebi.ac.uk/entry/{uid}", self.t.ACCENT_PURPLE),
            ("PDB", f"https://www.rcsb.org/search?query={uid}", self.t.ACCENT_BLUE),
        ]:
            tk.Button(bf, text=label,
                      font=("Segoe UI", 9),
                      bg=bg, fg="#fff" if bg != self.t.ACCENT_TEAL else "#0a1628",
                      relief="flat", cursor="hand2", padx=10,
                      command=lambda u=url: webbrowser.open(u)).pack(
                          side="left", padx=(0, 6), ipady=4)

        # ── DESCRIPTION ────────────────────────────────────────────
        body = tk.Frame(outer, bg=self.t.BG_MAIN, padx=20, pady=14)
        body.pack(fill="x")

        self._section(body, "DESCRIPTION")
        fn_text = p.get("function", "") or \
                  f"{p.get('protein_name','')} is a protein from {p.get('organism','')}. " \
                  f"It has {p.get('length','')} amino acids and is encoded by the {p.get('gene_name','')} gene."
        tk.Label(body, text=fn_text,
                 font=("Segoe UI", 11),
                 fg=self.t.TEXT_MAIN, bg=self.t.BG_MAIN,
                 wraplength=560, justify="left",
                 anchor="w").pack(fill="x", pady=(0, 14))

        # ── SUMMARY ────────────────────────────────────────────────
        self._section(body, "SUMMARY")
        summary = (f"{p.get('protein_name','')} (UniProt: {uid}) belongs to the proteome of "
                   f"{p.get('organism','')}. The protein sequence consists of {p.get('length','')} "
                   f"amino acids. It is encoded by the {p.get('gene_name','')} gene. "
                   f"Review status: {p.get('reviewed','')}. "
                   f"For full functional annotation, pathway associations, and post-translational "
                   f"modifications, refer to the UniProt entry and linked databases.")
        tk.Label(body, text=summary,
                 font=("Segoe UI", 10),
                 fg=self.t.TEXT_SUB, bg=self.t.BG_MAIN,
                 wraplength=560, justify="left",
                 anchor="w").pack(fill="x", pady=(0, 14))

        # ── INFO GRID ─────────────────────────────────────────────
        self._section(body, "QUICK FACTS")
        grid = tk.Frame(body, bg=self.t.BG_MAIN)
        grid.pack(fill="x", pady=(0, 12))
        facts = [
            ("UniProt ID",     uid),
            ("Gene",           p.get("gene_name","—")),
            ("Organism",       p.get("organism","—")),
            ("Length",         f"{p.get('length','—')} aa"),
            ("Status",         p.get("reviewed","—")),
        ]
        for i, (lbl, val) in enumerate(facts):
            cell = tk.Frame(grid, bg=self.t.BG_PANEL,
                            padx=12, pady=8, relief="flat")
            cell.grid(row=i//2, column=i%2, padx=4, pady=3, sticky="ew")
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)
            tk.Label(cell, text=lbl,
                     font=("Segoe UI", 8, "bold"),
                     fg=self.t.TEXT_DIM, bg=self.t.BG_PANEL,
                     anchor="w").pack(fill="x")
            tk.Label(cell, text=val,
                     font=("Segoe UI", 10),
                     fg=self.t.TEXT_MAIN, bg=self.t.BG_PANEL,
                     anchor="w").pack(fill="x")

        # Fetch full detail for sequence
        threading.Thread(target=self._fetch_full,
                         args=(uid, body), daemon=True).start()

    def _section(self, parent, text):
        f = tk.Frame(parent, bg=self.t.BG_MAIN)
        f.pack(fill="x", pady=(0, 4))
        tk.Label(f, text=text,
                 font=("Segoe UI", 8, "bold"),
                 fg=self.t.SECTION_LABEL, bg=self.t.BG_MAIN).pack(side="left")
        tk.Frame(f, bg=self.t.BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6)

    def _draw_molecule(self, canvas, uid):
        """Draw a stylized molecular diagram on dark background."""
        import math, hashlib
        # Use uid to seed a deterministic but varied pattern
        seed = int(hashlib.md5(uid.encode()).hexdigest()[:8], 16)
        cx, cy, r = 80, 80, 46
        n_atoms = 6 + (seed % 3)
        colors = ["#00d4aa", "#58a6ff", "#bc8cff"]

        # Outer ring
        canvas.create_oval(cx-r-12, cy-r-12, cx+r+12, cy+r+12,
                           outline="#00d4aa", width=1, dash=(4, 6))
        # Inner ring
        canvas.create_oval(cx-r+8, cy-r+8, cx+r-8, cy+r-8,
                           outline="#1e3252", width=1)

        # Spokes + atoms
        pts = []
        for i in range(n_atoms):
            angle = math.radians(360/n_atoms * i - 30)
            x = cx + r*math.cos(angle)
            y = cy + r*math.sin(angle)
            pts.append((x, y))
            col = colors[i % len(colors)]
            canvas.create_line(cx, cy, x, y, fill=col, width=1)
            canvas.create_oval(x-5, y-5, x+5, y+5, fill=col, outline="")

        # Inner connections
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i+2) % len(pts)]
            canvas.create_line(x1, y1, x2, y2,
                               fill="#1e3252", width=1)

        # Center atom
        canvas.create_oval(cx-10, cy-10, cx+10, cy+10,
                           fill="#00d4aa", outline="")
        canvas.create_text(cx, cy, text=uid[:3],
                           font=("Consolas", 7, "bold"),
                           fill="#0a1628")

        # Floating small atoms
        for i in range(4):
            angle = math.radians(45 + 90*i + seed*7)
            ox = cx + (r*0.5)*math.cos(angle)
            oy = cy + (r*0.5)*math.sin(angle)
            canvas.create_oval(ox-3, oy-3, ox+3, oy+3,
                               fill="#1a2a3a", outline="")

    def _fetch_full(self, uid, body):
        try:
            detail = self.uniprot.get_protein_detail(uid)
            if detail and detail.get("sequence"):
                body.after(0, lambda: self._append_seq(body, detail["sequence"]))
            self.set_status(f"Details loaded for {uid}.")
        except Exception:
            pass

    def _append_seq(self, body, seq):
        self._section(body, "AMINO ACID SEQUENCE")
        txt = tk.Text(body, height=5,
                      font=("Consolas", 9),
                      bg=self.t.BG_CARD,
                      fg=self.t.ACCENT_TEAL,
                      relief="flat", wrap="word",
                      state="disabled", padx=10, pady=8)
        txt.pack(fill="x")
        txt.configure(state="normal")
        txt.insert("end", " ".join(seq[i:i+10] for i in range(0, len(seq), 10)))
        txt.configure(state="disabled")

    def _placeholder(self):
        tk.Label(self.detail,
                 text="← Search and select a protein\nto see details here",
                 font=("Segoe UI", 12),
                 fg=self.t.TEXT_DIM, bg=self.t.BG_MAIN,
                 justify="center").pack(expand=True)
