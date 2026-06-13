# ⬡ BioDiscover — Biotech Discovery Platform

> A comprehensive, open-source biotech research companion for PhD students and researchers.
> Search proteins, explore genes, visualize pathways, and inspect 3D molecular structures — all in one beautiful dark-themed desktop app.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![APIs](https://img.shields.io/badge/APIs-UniProt%20·%20NCBI%20·%20PDB%20·%20KEGG%20·%20AlphaFold-blue?style=flat)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

---

## ✨ Features

| Module | Description | API Source |
|---|---|---|
| 🧬 **Protein Search** | Search 250M+ sequences with full detail view | UniProt REST |
| 🔬 **Gene Explorer** | Explore genes across 6+ organisms | NCBI Entrez |
| 🗺️ **Pathway Viewer** | Browse 500+ biological pathways | KEGG REST |
| 🔷 **3D Structures** | Search & open 210,000+ crystal structures | RCSB PDB |
| 🤖 **AlphaFold** | Link to AI-predicted protein structures | EBI AlphaFold DB |
| 📄 **Literature** | Search PubMed research articles | NCBI PubMed |

---

## 🖥️ Screenshots

> Bright biotech-themed UI with phosphorescent green accents, monospace fonts, and a clean split-panel layout.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/BioDiscover.git
cd BioDiscover
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run BioDiscover
```bash
python src/main.py
```

---

## 📦 Dependencies

Install all with one command:
```bash
pip install requests customtkinter pillow biopython numpy pandas matplotlib scipy tqdm loguru openpyxl python-dotenv
```

| Package | Purpose |
|---|---|
| `requests` | All REST API calls (UniProt, NCBI, KEGG, PDB) |
| `customtkinter` | Modern Tkinter widgets (optional — falls back to standard tk) |
| `pillow` | Image display in GUI |
| `biopython` | Sequence parsing, BLAST, PDB file I/O |
| `numpy` | Array operations for sequence data |
| `pandas` | Tabular data handling and CSV export |
| `matplotlib` | Plotting GC content, protein properties |
| `scipy` | Statistical analysis |
| `tqdm` | Progress bars |
| `loguru` | Logging |
| `openpyxl` | Excel export |

---

## 🧬 APIs Used (All Free, No Key Required)

| API | Base URL | What we use |
|---|---|---|
| **UniProt REST** | `https://rest.uniprot.org` | Protein search, sequences, annotations |
| **NCBI Entrez** | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils` | Gene & PubMed search |
| **RCSB PDB** | `https://search.rcsb.org` | 3D structure search & metadata |
| **KEGG REST** | `https://rest.kegg.jp` | Pathway maps and compound data |
| **EBI AlphaFold** | `https://alphafold.ebi.ac.uk/api` | AI-predicted structure links |

> ℹ️ **NCBI recommends** adding your email in `src/api/ncbi_api.py` for higher rate limits (10 req/s vs 3 req/s). Get a free API key at [NCBI](https://www.ncbi.nlm.nih.gov/account/).

---

## 📁 Project Structure

```
BioDiscover/
│
├── src/
│   ├── main.py                  # Application entry point
│   ├── ui/
│   │   ├── main_window.py       # Main window & layout
│   │   ├── theme.py             # Color palette & typography
│   │   ├── dashboard_panel.py   # Home dashboard
│   │   ├── protein_panel.py     # Protein search module
│   │   ├── gene_panel.py        # Gene explorer module
│   │   ├── pathway_panel.py     # Pathway viewer module
│   │   ├── structure_panel.py   # 3D structure module
│   │   └── components.py        # Shared UI components
│   │
│   └── api/
│       ├── uniprot_api.py       # UniProt REST API
│       ├── ncbi_api.py          # NCBI Entrez API
│       ├── kegg_api.py          # KEGG REST API
│       ├── pdb_api.py           # RCSB PDB API
│       └── alphafold_api.py     # AlphaFold DB API
│
├── data/
│   ├── cache/                   # API response cache (auto-generated)
│   └── samples/                 # Sample FASTA / sequence files
│
├── docs/                        # Documentation
├── tests/                       # Unit tests
├── assets/                      # Icons, fonts
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔬 Example Use Cases

- **Search insulin** → Get UniProt entry, sequence, GO terms, linked PDB structures
- **Explore BRCA1** → See gene summary, chromosome location, open NCBI entry
- **Browse MAPK signaling** → View KEGG pathway, open interactive map
- **Find p53 structure** → Get 3EAM entry, open 3D viewer at RCSB PDB
- **AlphaFold preview** → One-click link to AI-predicted structure for any protein

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first for major changes.

```bash
# Run tests
python -m pytest tests/
```

---

## 📄 License

MIT License — free for academic and research use.

---

## 🙏 Acknowledgements

- [UniProt Consortium](https://www.uniprot.org)
- [NCBI / NLM](https://www.ncbi.nlm.nih.gov)
- [RCSB PDB](https://www.rcsb.org)
- [KEGG](https://www.kegg.jp)
- [DeepMind / EBI AlphaFold](https://alphafold.ebi.ac.uk)

---

*Built with ❤️ for the biotech research community.*
