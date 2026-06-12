"""
AlphaFold DB API Wrapper
Docs: https://alphafold.ebi.ac.uk/api-docs
"""

import requests


ALPHAFOLD_BASE = "https://alphafold.ebi.ac.uk/api"


class AlphaFoldAPI:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get_prediction(self, uniprot_accession: str) -> dict:
        """
        Get AlphaFold structure prediction for a UniProt accession.
        Returns model metadata including confidence score info.
        """
        try:
            url = f"{ALPHAFOLD_BASE}/prediction/{uniprot_accession}"
            r = self.session.get(url, timeout=self.timeout)
            if r.status_code == 404:
                return {}
            r.raise_for_status()
            data = r.json()
            if data:
                entry = data[0]
                return {
                    "uniprot_accession": entry.get("uniprotAccession", ""),
                    "entry_id":          entry.get("entryId", ""),
                    "gene":              entry.get("gene", ""),
                    "uniprot_id":        entry.get("uniprotId", ""),
                    "protein_name":      entry.get("uniprotDescription", ""),
                    "organism":          entry.get("organismScientificName", ""),
                    "model_created":     entry.get("modelCreatedDate", ""),
                    "pdb_url":           entry.get("pdbUrl", ""),
                    "cif_url":           entry.get("cifUrl", ""),
                    "confidence_url":    entry.get("paeImageUrl", ""),
                    "alphafold_db_url":  f"https://alphafold.ebi.ac.uk/entry/{uniprot_accession}",
                }
            return {}
        except requests.exceptions.ConnectionError:
            return {}
        except Exception:
            return {}

    def check_available(self, uniprot_accession: str) -> bool:
        """Check if AlphaFold has a prediction for this accession."""
        result = self.get_prediction(uniprot_accession)
        return bool(result)
