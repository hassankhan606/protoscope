"""
KEGG REST API Wrapper
Docs: https://www.kegg.jp/kegg/rest/keggapi.html
"""

import requests


KEGG_BASE = "https://rest.kegg.jp"


class KEGGAPI:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()

    def list_pathways(self, org: str = "hsa") -> list[dict]:
        """List all KEGG pathways for an organism."""
        try:
            r = self.session.get(f"{KEGG_BASE}/list/pathway/{org}",
                                 timeout=self.timeout)
            r.raise_for_status()
            pathways = []
            for line in r.text.strip().split("\n"):
                if "\t" in line:
                    pid, name = line.split("\t", 1)
                    pathways.append({
                        "id":   pid.strip(),
                        "name": name.strip(),
                    })
            return pathways
        except Exception as e:
            raise Exception(f"KEGG list error: {e}")

    def search_pathway(self, query: str, org: str = "hsa") -> list[dict]:
        """Search KEGG pathways by keyword."""
        try:
            # First list all, then filter
            all_pathways = self.list_pathways(org)
            q_lower = query.lower()
            filtered = [p for p in all_pathways
                        if q_lower in p["name"].lower()
                        or q_lower in p["id"].lower()]
            return filtered
        except Exception as e:
            raise Exception(f"KEGG search error: {e}")

    def get_pathway_info(self, pathway_id: str) -> dict:
        """Get detailed info for a specific pathway."""
        try:
            r = self.session.get(f"{KEGG_BASE}/get/{pathway_id}",
                                 timeout=self.timeout)
            r.raise_for_status()
            info = {}
            current_key = None
            current_val = []

            for line in r.text.split("\n"):
                if not line.strip() or line.startswith("///"):
                    if current_key and current_val:
                        info[current_key] = " ".join(current_val).strip()
                    break

                if not line.startswith(" "):
                    if current_key and current_val:
                        info[current_key] = " ".join(current_val).strip()
                    parts = line.split(None, 1)
                    current_key = parts[0].title()
                    current_val = [parts[1]] if len(parts) > 1 else []
                else:
                    current_val.append(line.strip())

            return {k: v for k, v in info.items()
                    if k in ("Name", "Class", "Description", "Disease",
                             "Drug", "Compound", "Module")}
        except Exception as e:
            return {}

    def get_compound(self, compound_id: str) -> dict:
        """Get info on a KEGG compound."""
        try:
            r = self.session.get(f"{KEGG_BASE}/get/{compound_id}",
                                 timeout=self.timeout)
            r.raise_for_status()
            lines = r.text.strip().split("\n")
            info = {}
            for line in lines:
                if not line.startswith(" ") and "  " in line:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        info[parts[0].lower()] = parts[1].strip()
            return info
        except Exception:
            return {}
