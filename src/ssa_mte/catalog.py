from __future__ import annotations

import numpy as np
import pandas as pd


MU_EARTH_KM3_S2 = 398600.4418
R_EARTH_KM = 6378.137

REQUIRED_CATALOG_COLUMNS = {
    "OBJECT_NAME",
    "NORAD_CAT_ID",
    "EPOCH",
    "MEAN_MOTION",
    "ECCENTRICITY",
    "INCLINATION",
    "RA_OF_ASC_NODE",
    "ARG_OF_PERICENTER",
    "MEAN_ANOMALY",
    "BSTAR",
}


def wrap_angle_delta_deg(a_deg: pd.Series, b_deg: float) -> pd.Series:
    return np.abs((a_deg - b_deg + 180.0) % 360.0 - 180.0)


def mean_motion_to_semimajor_axis_km(mean_motion_rev_day: pd.Series) -> pd.Series:
    n_rad_s = mean_motion_rev_day * (2.0 * np.pi / 86400.0)
    return (MU_EARTH_KM3_S2 / (n_rad_s**2)) ** (1.0 / 3.0)


def normalize_catalog(catalog_raw: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(REQUIRED_CATALOG_COLUMNS.difference(catalog_raw.columns))
    if missing:
        raise KeyError(f"GP catalog is missing required columns: {missing}")

    catalog = catalog_raw.copy()
    for col in [
        "NORAD_CAT_ID",
        "MEAN_MOTION",
        "ECCENTRICITY",
        "INCLINATION",
        "RA_OF_ASC_NODE",
        "ARG_OF_PERICENTER",
        "MEAN_ANOMALY",
        "BSTAR",
    ]:
        catalog[col] = pd.to_numeric(catalog[col], errors="coerce")

    catalog["EPOCH"] = pd.to_datetime(catalog["EPOCH"], utc=True, errors="coerce")
    catalog = catalog.dropna(
        subset=["NORAD_CAT_ID", "MEAN_MOTION", "ECCENTRICITY", "INCLINATION", "RA_OF_ASC_NODE"]
    ).copy()
    catalog["NORAD_CAT_ID"] = catalog["NORAD_CAT_ID"].astype(int)
    catalog["SEMIMAJOR_AXIS_KM"] = mean_motion_to_semimajor_axis_km(catalog["MEAN_MOTION"])
    catalog["PERIGEE_ALT_KM"] = catalog["SEMIMAJOR_AXIS_KM"] * (1.0 - catalog["ECCENTRICITY"]) - R_EARTH_KM
    catalog["APOGEE_ALT_KM"] = catalog["SEMIMAJOR_AXIS_KM"] * (1.0 + catalog["ECCENTRICITY"]) - R_EARTH_KM
    catalog["PERIOD_MIN"] = 1440.0 / catalog["MEAN_MOTION"]
    return catalog


def build_local_catalog(
    catalog: pd.DataFrame,
    operator_catnr: int,
    altitude_gate_km: float = 100.0,
    inclination_gate_deg: float = 5.0,
    raan_gate_deg: float = 30.0,
    mean_motion_gate_rev_day: float = 0.35,
) -> tuple[pd.Series, pd.DataFrame]:
    operator_mask = catalog["NORAD_CAT_ID"] == int(operator_catnr)
    if int(operator_mask.sum()) != 1:
        raise ValueError(f"Expected one operator row for CATNR={operator_catnr}, found {int(operator_mask.sum())}.")

    operator_row = catalog.loc[operator_mask].iloc[0].copy()
    work = catalog.copy()
    work["DELTA_INC_DEG"] = np.abs(work["INCLINATION"] - operator_row["INCLINATION"])
    work["DELTA_RAAN_DEG"] = wrap_angle_delta_deg(work["RA_OF_ASC_NODE"], float(operator_row["RA_OF_ASC_NODE"]))
    work["DELTA_MEAN_MOTION"] = np.abs(work["MEAN_MOTION"] - operator_row["MEAN_MOTION"])
    work["DELTA_PERIGEE_ALT_KM"] = np.abs(work["PERIGEE_ALT_KM"] - operator_row["PERIGEE_ALT_KM"])
    work["DELTA_APOGEE_ALT_KM"] = np.abs(work["APOGEE_ALT_KM"] - operator_row["APOGEE_ALT_KM"])

    radial_overlap_gate = (
        (np.abs(work["PERIGEE_ALT_KM"] - operator_row["APOGEE_ALT_KM"]) <= altitude_gate_km)
        | (np.abs(work["APOGEE_ALT_KM"] - operator_row["PERIGEE_ALT_KM"]) <= altitude_gate_km)
        | (np.abs(work["PERIGEE_ALT_KM"] - operator_row["PERIGEE_ALT_KM"]) <= altitude_gate_km)
        | (np.abs(work["APOGEE_ALT_KM"] - operator_row["APOGEE_ALT_KM"]) <= altitude_gate_km)
    )
    broad_gate = (
        (work["NORAD_CAT_ID"] != int(operator_catnr))
        & radial_overlap_gate
        & (work["DELTA_INC_DEG"] <= inclination_gate_deg)
        & (work["DELTA_RAAN_DEG"] <= raan_gate_deg)
        & (work["DELTA_MEAN_MOTION"] <= mean_motion_gate_rev_day)
    )
    return operator_row, work.loc[broad_gate].copy().reset_index(drop=True)
