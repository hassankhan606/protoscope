"""
UniProt REST API Wrapper
Docs: https://www.uniprot.org/help/api
"""

import requests
import json


UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"


class UniProtAPI:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def search(self, query: str, organism: str = "All organisms",
               limit: int = 20) -> list[dict]:
        """
        Search UniProt proteins by keyword/ID.
        Returns list of simplified protein dicts.
        """
        # Build query
        q = query
        if "Human" in organism:
            q += " AND (organism_id:9606)"
        elif "Mouse" in organism:
            q += " AND (organism_id:10090)"
        elif "E. coli" in organism:
            q += " AND (organism_id:511145)"
        elif "Yeast" in organism:
            q += " AND (organism_id:4932)"
        elif "Rat" in organism:
            q += " AND (organism_id:10116)"

        params = {
            "query": q,
            "format": "json",
            "size": limit,
            "fields": "accession,id,protein_name,gene_names,organism_name,"
                      "length,reviewed,cc_function",
        }

        try:
            resp = self.session.get(f"{UNIPROT_BASE}/search",
                                    params=params,
                                    timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            return [self._parse_entry(r) for r in results]
        except requests.exceptions.ConnectionError:
            raise Exception("No internet connection. Check your network.")
        except requests.exceptions.Timeout:
            raise Exception("UniProt request timed out.")
        except Exception as e:
            raise Exception(f"UniProt API error: {e}")

    def _parse_entry(self, entry: dict) -> dict:
        """Extract key fields from a UniProt entry."""
        # Protein names
        pname = ""
        pn = entry.get("proteinDescription", {})
        rec = pn.get("recommendedName", {})
        if rec:
            pname = rec.get("fullName", {}).get("value", "")
        if not pname:
            sub = pn.get("submissionNames", [{}])
            if sub:
                pname = sub[0].get("fullName", {}).get("value", "")

        # Gene name
        gene_names = entry.get("genes", [])
        gene = ""
        if gene_names:
            gn = gene_names[0]
            gene = gn.get("geneName", {}).get("value", "")

        # Organism
        org = entry.get("organism", {}).get("scientificName", "")

        # Function (CC comments)
        function = ""
        comments = entry.get("comments", [])
        for c in comments:
            if c.get("commentType") == "FUNCTION":
                texts = c.get("texts", [{}])
                if texts:
                    function = texts[0].get("value", "")[:300]
                    break

        reviewed = "Reviewed (Swiss-Prot)" if entry.get("entryType") == "UniProtKB reviewed (Swiss-Prot)" \
                   else "Unreviewed (TrEMBL)"

        return {
            "id":           entry.get("primaryAccession", ""),
            "entry_name":   entry.get("uniProtkbId", ""),
            "protein_name": pname,
            "gene_name":    gene,
            "organism":     org,
            "length":       entry.get("sequence", {}).get("length", ""),
            "reviewed":     reviewed,
            "function":     function,
        }

    def get_protein_detail(self, accession: str) -> dict:
        """Fetch full details for a single protein by accession."""
        try:
            params = {
                "format": "json",
                "fields": "accession,protein_name,gene_names,organism_name,"
                          "length,sequence,cc_function,cc_disease,go_p,go_f,"
                          "ft_domain,keyword,xref_pdb",
            }
            resp = self.session.get(f"{UNIPROT_BASE}/{accession}",
                                    params=params,
                                    timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            parsed = self._parse_entry(data)
            # Add full sequence
            seq_data = data.get("sequence", {})
            parsed["sequence"] = seq_data.get("value", "")
            parsed["mass"]     = seq_data.get("molWeight", "")

            # GO terms
            go_terms = []
            for ref in data.get("uniProtKBCrossReferences", []):
                if ref.get("database") in ("GO",):
                    props = {p["key"]: p["value"]
                             for p in ref.get("properties", [])}
                    go_terms.append(props.get("GoTerm", ""))
            parsed["go_terms"] = go_terms[:10]

            # PDB cross-references
            pdb_ids = []
            for ref in data.get("uniProtKBCrossReferences", []):
                if ref.get("database") == "PDB":
                    pdb_ids.append(ref.get("id", ""))
            parsed["pdb_ids"] = pdb_ids[:5]

            return parsed
        except Exception as e:
            return {}
