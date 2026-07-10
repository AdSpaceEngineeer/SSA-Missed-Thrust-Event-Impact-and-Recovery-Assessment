import pandas as pd

from ssa_mte.catalog import build_local_catalog, normalize_catalog


def test_catalog_normalization_and_local_prefilter():
    raw = pd.DataFrame(
        [
            {
                "OBJECT_NAME": "OP",
                "NORAD_CAT_ID": 1,
                "EPOCH": "2026-01-01T00:00:00Z",
                "MEAN_MOTION": 15.0,
                "ECCENTRICITY": 0.001,
                "INCLINATION": 97.0,
                "RA_OF_ASC_NODE": 10.0,
                "ARG_OF_PERICENTER": 20.0,
                "MEAN_ANOMALY": 30.0,
                "BSTAR": 0.0,
            },
            {
                "OBJECT_NAME": "NEAR",
                "NORAD_CAT_ID": 2,
                "EPOCH": "2026-01-01T00:00:00Z",
                "MEAN_MOTION": 15.01,
                "ECCENTRICITY": 0.001,
                "INCLINATION": 97.5,
                "RA_OF_ASC_NODE": 12.0,
                "ARG_OF_PERICENTER": 20.0,
                "MEAN_ANOMALY": 30.0,
                "BSTAR": 0.0,
            },
        ]
    )

    catalog = normalize_catalog(raw)
    operator, local = build_local_catalog(catalog, operator_catnr=1)

    assert operator["OBJECT_NAME"] == "OP"
    assert len(local) == 1
    assert local.iloc[0]["OBJECT_NAME"] == "NEAR"
