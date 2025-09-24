"""
download_hpo.py

Convenience script to fetch the latest Human Phenotype Ontology (HPO)
and store it in src/prenatalppkt/data/hp.json.
"""

import logging
from prenatalppkt.ontology import download_hpo

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    path = download_hpo(force=True)
    logger.info("Downloaded HPO ontology to %s", path)
