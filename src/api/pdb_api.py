"""
RCSB PDB REST API Wrapper
Docs: https://data.rcsb.org/
"""

import requests
import json


RCSB_BASE    = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_DATA    = "https://data.rcsb.org/rest/v1/core/entry"
RCSB_GRAPHQL = "https://data.rcsb.org/graphql"


class PDBAPI:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        Search RCSB PDB by keyword.
        Returns list of structure dicts.
        """
        # Check if it's a direct PDB ID (4 characters)
        if len(query) == 4 and query.replace("-", "").isalnum():
            entry = self.get_entry(query.upper())
            if entry:
                return [entry]

        payload = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {"value": query}
            },
            "request_options": {
                "paginate": {"start": 0, "rows": limit},
                "sort": [{"sort_by": "score", "direction": "descending"}]
            },
            "return_type": "entry"
        }

        try:
            r = self.session.post(RCSB_BASE, json=payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            result_set = data.get("result_set", [])
            ids = [item["identifier"] for item in result_set]

            structures = []
            # Fetch details in bulk via GraphQL
            if ids:
                structures = self._get_entries_graphql(ids[:20])
            return structures

        except requests.exceptions.ConnectionError:
            raise Exception("No internet. Check your network.")
        except Exception as e:
            raise Exception(f"PDB search error: {e}")

    def _get_entries_graphql(self, ids: list[str]) -> list[dict]:
        """Fetch multiple entries using RCSB GraphQL."""
        query = """
        query getEntries($ids: [String!]!) {
          entries(entry_ids: $ids) {
            rcsb_id
            struct { title }
            rcsb_entry_info {
              resolution_combined
              experimental_method
              deposit_date
              release_date
            }
            audit_author { name }
          }
        }
        """
        try:
            r = self.session.post(
                RCSB_GRAPHQL,
                json={"query": query, "variables": {"ids": ids}},
                timeout=self.timeout
            )
            r.raise_for_status()
            entries = r.json().get("data", {}).get("entries", [])
            return [self._parse_graphql_entry(e) for e in entries if e]
        except Exception:
            # Fallback: return minimal dicts
            return [{"id": i, "title": "", "resolution": ""} for i in ids]

    def _parse_graphql_entry(self, e: dict) -> dict:
        info = e.get("rcsb_entry_info", {})
        res = info.get("resolution_combined", [])
        resolution = f"{res[0]:.2f} Å" if res else ""
        authors = e.get("audit_author", [])
        author_str = ", ".join(a.get("name", "") for a in authors[:3])
        if len(authors) > 3:
            author_str += " et al."
        return {
            "id":           e.get("rcsb_id", ""),
            "title":        (e.get("struct", {}) or {}).get("title", ""),
            "resolution":   resolution,
            "method":       info.get("experimental_method", ""),
            "release_date": info.get("release_date", "")[:10] if info.get("release_date") else "",
            "authors":      author_str,
        }

    def get_entry(self, pdb_id: str) -> dict:
        """Fetch a single PDB entry by ID."""
        try:
            r = self.session.get(f"{RCSB_DATA}/{pdb_id}",
                                 timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            info = data.get("rcsb_entry_info", {})
            struct = data.get("struct", {})
            res = info.get("resolution_combined", [])
            resolution = f"{res[0]:.2f} Å" if res else ""

            return {
                "id":           pdb_id,
                "title":        struct.get("title", ""),
                "resolution":   resolution,
                "method":       info.get("experimental_method", ""),
                "release_date": data.get("rcsb_accession_info", {}).get(
                                    "initial_release_date", "")[:10],
                "abstract":     struct.get("pdbx_descriptor", ""),
                "authors":      "",
            }
        except Exception:
            return {}
