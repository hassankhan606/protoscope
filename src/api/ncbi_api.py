"""
NCBI Entrez API Wrapper
Docs: https://www.ncbi.nlm.nih.gov/books/NBK25497/
Uses public E-utilities (no API key required for basic use,
but you should add your email and optionally an API key for
higher rate limits - 10 req/s vs 3 req/s).
"""

import requests
import xml.etree.ElementTree as ET
import json
import time


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# ⚠ Add your email here for NCBI's records (optional but recommended)
NCBI_TOOL  = "BioDiscover"
NCBI_EMAIL = "your_email@institution.edu"


class NCBIAPI:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self._common_params = {
            "tool":  NCBI_TOOL,
            "email": NCBI_EMAIL,
        }

    def search_gene(self, query: str, taxid: str = "9606",
                    limit: int = 20) -> list[dict]:
        """
        Search NCBI Gene database.
        taxid: NCBI taxonomy ID (9606 = human)
        Returns list of gene summary dicts.
        """
        try:
            # Step 1: ESearch to get IDs
            esearch_params = {
                **self._common_params,
                "db":     "gene",
                "term":   f"{query}[All Fields] AND {taxid}[Taxonomy ID]",
                "retmax": limit,
                "retmode":"json",
                "usehistory": "y",
            }
            r = self.session.get(f"{EUTILS_BASE}/esearch.fcgi",
                                 params=esearch_params,
                                 timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            ids = data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            # Step 2: ESummary to get details
            time.sleep(0.35)  # respect NCBI rate limit
            esummary_params = {
                **self._common_params,
                "db":     "gene",
                "id":     ",".join(ids),
                "retmode":"json",
            }
            r2 = self.session.get(f"{EUTILS_BASE}/esummary.fcgi",
                                  params=esummary_params,
                                  timeout=self.timeout)
            r2.raise_for_status()
            summary = r2.json()
            uids = summary.get("result", {}).get("uids", [])
            results_data = summary.get("result", {})

            genes = []
            for uid in uids:
                rec = results_data.get(uid, {})
                if rec:
                    genes.append(self._parse_gene(uid, rec))
            return genes

        except requests.exceptions.ConnectionError:
            raise Exception("No internet. Check your network.")
        except Exception as e:
            raise Exception(f"NCBI Gene error: {e}")

    def _parse_gene(self, uid: str, rec: dict) -> dict:
        return {
            "uid":         uid,
            "name":        rec.get("name", ""),
            "description": rec.get("description", ""),
            "status":      rec.get("status", ""),
            "chromosome":  rec.get("chromosome", ""),
            "maplocation": rec.get("maplocation", ""),
            "taxid":       str(rec.get("taxid", "")),
            "organism":    rec.get("organism", {}).get("scientificname", ""),
            "otheraliases":rec.get("otheraliases", ""),
            "summary":     rec.get("summary", "")[:500] if rec.get("summary") else "",
        }

    def search_pubmed(self, query: str, limit: int = 10) -> list[dict]:
        """Search PubMed literature."""
        try:
            params = {
                **self._common_params,
                "db":     "pubmed",
                "term":   query,
                "retmax": limit,
                "retmode":"json",
            }
            r = self.session.get(f"{EUTILS_BASE}/esearch.fcgi",
                                 params=params, timeout=self.timeout)
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            time.sleep(0.35)
            s_params = {
                **self._common_params,
                "db":     "pubmed",
                "id":     ",".join(ids),
                "retmode":"json",
            }
            r2 = self.session.get(f"{EUTILS_BASE}/esummary.fcgi",
                                  params=s_params, timeout=self.timeout)
            r2.raise_for_status()
            data = r2.json().get("result", {})
            uids = data.get("uids", [])
            articles = []
            for uid in uids:
                rec = data.get(uid, {})
                articles.append({
                    "pmid":    uid,
                    "title":   rec.get("title", ""),
                    "authors": [a.get("name", "") for a in rec.get("authors", [])[:3]],
                    "journal": rec.get("source", ""),
                    "pubdate": rec.get("pubdate", ""),
                })
            return articles
        except Exception as e:
            raise Exception(f"PubMed error: {e}")
