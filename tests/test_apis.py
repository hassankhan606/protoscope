"""
BioDiscover — Basic API Tests
Run: pytest tests/ -v
"""

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.uniprot_api import UniProtAPI
from src.api.ncbi_api import NCBIAPI
from src.api.kegg_api import KEGGAPI
from src.api.pdb_api import PDBAPI
from src.api.alphafold_api import AlphaFoldAPI


# ─── UniProt ──────────────────────────────────────────────────────

class TestUniProt:
    def setup_method(self):
        self.api = UniProtAPI()

    def test_search_insulin(self):
        results = self.api.search("insulin", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "id" in results[0]

    def test_search_returns_keys(self):
        results = self.api.search("hemoglobin", limit=3)
        for r in results:
            assert "protein_name" in r
            assert "organism" in r
            assert "length" in r

    def test_get_detail_insulin(self):
        detail = self.api.get_protein_detail("P01308")  # Human insulin
        assert detail.get("id") == "P01308"
        assert "sequence" in detail


# ─── NCBI ─────────────────────────────────────────────────────────

class TestNCBI:
    def setup_method(self):
        self.api = NCBIAPI()

    def test_search_gene_brca1(self):
        results = self.api.search_gene("BRCA1", taxid="9606", limit=3)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_gene_has_name(self):
        results = self.api.search_gene("p53", taxid="9606", limit=3)
        for r in results:
            assert "name" in r
            assert "uid" in r


# ─── KEGG ─────────────────────────────────────────────────────────

class TestKEGG:
    def setup_method(self):
        self.api = KEGGAPI()

    def test_list_pathways(self):
        pathways = self.api.list_pathways(org="hsa")
        assert len(pathways) > 100

    def test_search_glycolysis(self):
        results = self.api.search_pathway("Glycolysis", org="hsa")
        assert len(results) > 0
        assert any("Glycolysis" in r["name"] for r in results)


# ─── PDB ──────────────────────────────────────────────────────────

class TestPDB:
    def setup_method(self):
        self.api = PDBAPI()

    def test_search_hemoglobin(self):
        results = self.api.search("hemoglobin", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_get_entry_1HHO(self):
        entry = self.api.get_entry("1HHO")
        assert entry.get("id") == "1HHO"
        assert entry.get("title") != ""


# ─── AlphaFold ────────────────────────────────────────────────────

class TestAlphaFold:
    def setup_method(self):
        self.api = AlphaFoldAPI()

    def test_get_insulin_prediction(self):
        result = self.api.get_prediction("P01308")  # Human insulin
        # May or may not be available depending on AlphaFold DB
        assert isinstance(result, dict)
