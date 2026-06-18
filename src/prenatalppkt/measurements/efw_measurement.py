"""Build a Phenopacket v2 Measurement dict for Estimated Fetal Weight (EFW).

EFW is calculated from biometry (Hadlock formula etc.) rather than measured
directly, so it lives outside the TermBin pipeline. The `parse_estimated_fetal_weight()`
section parser returns a dict with `efw_grams`, `percentile`, `method`, etc.;
this builder turns that into a LOINC-coded Measurement parallel to the
biometry Measurements produced by `TermBin.to_measurement_dict()`.

LOINC code: 11727-5 "Fetal Body weight estimated by US" (Active).
Unit: UO:0000021 (gram), not UO:0000016 (millimeter).
"""

from __future__ import annotations

from typing import Any

LOINC_CODE = "LOINC:11727-5"
LOINC_LABEL = "Fetal Body weight estimated by US"
UNIT_CODE = "UO:0000021"
UNIT_LABEL = "gram"


def build_efw_measurement(efw: dict[str, Any] | None) -> dict | None:
    """Return the Phenopacket v2 `Measurement` JSON shape for EFW, or None.

    Returns None when:
    - `efw` is None or empty
    - `efw['efw_grams']` is missing or None

    Output shape matches `TermBin.to_measurement_dict()` so the same downstream
    serialiser (proto builder, JSON exporter) can consume both.
    """
    if not efw:
        return None
    grams = efw.get("efw_grams")
    if grams is None:
        return None
    return {
        "assay": {"id": LOINC_CODE, "label": LOINC_LABEL},
        "value": {
            "quantity": {
                "unit": {"id": UNIT_CODE, "label": UNIT_LABEL},
                "value": float(grams),
            }
        },
    }
