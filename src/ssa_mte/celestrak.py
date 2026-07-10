from __future__ import annotations

import io
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests


BASE_GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
HTTP_HEADERS = {"User-Agent": "ssa-missed-thrust-recovery/0.1"}


def build_celestrak_url(**params: object) -> str:
    clean = {k: v for k, v in params.items() if v is not None}
    return f"{BASE_GP_URL}?{urlencode(clean)}"


def parse_tle_text(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 3 or not lines[1].startswith("1 ") or not lines[2].startswith("2 "):
        raise ValueError("Expected a 3-line TLE response.")
    return {"name": lines[0], "line1": lines[1], "line2": lines[2]}


class CelesTrakClient:
    def __init__(self, cache_dir: Path, timeout_seconds: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = int(timeout_seconds)
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def fetch_text_with_cache(self, url: str, cache_path: Path, force_refresh: bool = False) -> str:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists() and not force_refresh:
            return cache_path.read_text(encoding="utf-8")

        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        text = response.text
        if not text.strip():
            raise ValueError(f"Empty response from {url}")
        cache_path.write_text(text, encoding="utf-8")
        return text

    def fetch_operator_tle(self, catnr: int, force_refresh: bool = False) -> dict[str, str]:
        url = build_celestrak_url(CATNR=int(catnr), FORMAT="TLE")
        text = self.fetch_text_with_cache(url, self.cache_dir / f"catnr_{int(catnr)}.tle", force_refresh)
        return parse_tle_text(text)

    def fetch_catalog_csv(self, group: str, force_refresh: bool = False) -> pd.DataFrame:
        url = build_celestrak_url(GROUP=group, FORMAT="CSV")
        text = self.fetch_text_with_cache(
            url,
            self.cache_dir / f"{group.lower()}_catalog.csv",
            force_refresh,
        )
        catalog = pd.read_csv(io.StringIO(text))
        catalog.columns = [str(c).strip().upper() for c in catalog.columns]
        return catalog

    def fetch_tle_for_catnr(self, catnr: int, force_refresh: bool = False) -> dict[str, object] | None:
        try:
            tle = self.fetch_operator_tle(int(catnr), force_refresh=force_refresh)
        except (requests.HTTPError, ValueError):
            return None
        return {"NORAD_CAT_ID": int(catnr), "TLE_LINE1": tle["line1"], "TLE_LINE2": tle["line2"]}
