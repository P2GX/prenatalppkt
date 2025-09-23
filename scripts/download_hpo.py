"""
download_hpo.py

Convenience script to fetch the latest Human Phenotype Ontology (HPO)
and store it in src/prenatalppkt/data/hp.json.
"""

from prenatalppkt.ontology import download_hpo

if __name__ == "__main__":
    path = download_hpo(force=True)
    print(f"Downloaded HPO ontology to {path}")
