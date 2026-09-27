from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "facilities.csv"
DB_PATH = DATA_DIR / "marutai.db"
STORAGE_DIR = ROOT / "storage"
ORIGINAL_DIR = STORAGE_DIR / "original"
STAMPED_DIR = STORAGE_DIR / "stamped"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
    STAMPED_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _bool(v: Any) -> int:
    if isinstance(v, bool):
        return int(v)
    return int(str(v).strip().lower() in {"1", "true", "yes", "y"})


def init_storage() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS facilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'sento',
                ward TEXT NOT NULL DEFAULT '',
                address TEXT NOT NULL DEFAULT '',
                latitude REAL,
                longitude REAL,
                has_open_air_bath INTEGER NOT NULL DEFAULT 0,
                has_natural_hot_spring INTEGER NOT NULL DEFAULT 0,
                website_url TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS visits (
                id TEXT PRIMARY KEY,
                facility_id TEXT NOT NULL,
                visited_date TEXT NOT NULL,
                original_photo_path TEXT NOT NULL,
                stamped_photo_path TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) AS n FROM facilities").fetchone()["n"]
        if count == 0 and CSV_PATH.exists():
            try:
                df = pd.read_csv(CSV_PATH)
            except Exception:
                df = pd.DataFrame()
            if not df.empty:
                for _, row in df.iterrows():
                    if not str(row.get("name", "")).strip():
                        continue
                    conn.execute(
                        """INSERT OR REPLACE INTO facilities
                        (id,name,category,ward,address,latitude,longitude,has_open_air_bath,
                         has_natural_hot_spring,website_url,active)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            str(row.get("id") or uuid4()),
                            str(row.get("name") or ""),
                            str(row.get("category") or "sento"),
                            str(row.get("ward") or ""),
                            str(row.get("address") or ""),
                            None if pd.isna(row.get("latitude")) else float(row.get("latitude")),
                            None if pd.isna(row.get("longitude")) else float(row.get("longitude")),
                            _bool(row.get("has_open_air_bath", False)),
                            _bool(row.get("has_natural_hot_spring", False)),
                            "" if pd.isna(row.get("website_url")) else str(row.get("website_url") or ""),
                            _bool(row.get("active", True)),
                        ),
                    )


def _row_to_facility(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["has_open_air_bath"] = bool(d.get("has_open_air_bath"))
    d["has_natural_hot_spring"] = bool(d.get("has_natural_hot_spring"))
    d["active"] = bool(d.get("active"))
    return d


def list_facilities(active_only: bool = True) -> list[dict[str, Any]]:
    init_storage()
    sql = "SELECT * FROM facilities"
    args: tuple[Any, ...] = ()
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY ward, name"
    with _connect() as conn:
        return [_row_to_facility(r) for r in conn.execute(sql, args).fetchall()]


def get_facility(facility_id: str) -> dict[str, Any] | None:
    init_storage()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM facilities WHERE id=? LIMIT 1", (str(facility_id),)).fetchone()
        return _row_to_facility(row) if row else None


def _visit_with_facility(row: sqlite3.Row, facility_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    d = dict(row)
    d["facility_id"] = str(d["facility_id"])
    d["facilities"] = facility_map.get(d["facility_id"], {})
    return d


def list_visits() -> list[dict[str, Any]]:
    init_storage()
    facilities = {str(f["id"]): f for f in list_facilities(active_only=False)}
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM visits ORDER BY visited_date DESC, created_at DESC").fetchall()
    return [_visit_with_facility(r, facilities) for r in rows]


def visits_for_facility(facility_id: str) -> list[dict[str, Any]]:
    return [v for v in list_visits() if str(v.get("facility_id")) == str(facility_id)]


def visited_facility_ids() -> set[str]:
    return {str(v.get("facility_id")) for v in list_visits()}


def photo_path(path: str | None):
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p) if p.exists() else None


def create_visit(facility_id: str, visited_date: str, original_bytes: bytes, stamped_bytes: bytes) -> dict[str, Any]:
    init_storage()
    visit_id = str(uuid4())
    original_rel = Path("storage") / "original" / f"{visit_id}.jpg"
    stamped_rel = Path("storage") / "stamped" / f"{visit_id}.jpg"
    original_abs = ROOT / original_rel
    stamped_abs = ROOT / stamped_rel
    try:
        original_abs.write_bytes(original_bytes)
        stamped_abs.write_bytes(stamped_bytes)
        with _connect() as conn:
            conn.execute(
                "INSERT INTO visits (id,facility_id,visited_date,original_photo_path,stamped_photo_path) VALUES (?,?,?,?,?)",
                (visit_id, str(facility_id), visited_date, original_rel.as_posix(), stamped_rel.as_posix()),
            )
        return {
            "id": visit_id,
            "facility_id": str(facility_id),
            "visited_date": visited_date,
            "original_photo_path": original_rel.as_posix(),
            "stamped_photo_path": stamped_rel.as_posix(),
        }
    except Exception:
        original_abs.unlink(missing_ok=True)
        stamped_abs.unlink(missing_ok=True)
        raise


def export_backup(target_zip: Path) -> Path:
    init_storage()
    base = target_zip.with_suffix("")
    archive = shutil.make_archive(str(base), "zip", ROOT, "data")
    # append storage directory to same archive is awkward with make_archive; create a staging dir instead
    staging = ROOT / ".backup_tmp"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    shutil.copytree(DATA_DIR, staging / "data")
    shutil.copytree(STORAGE_DIR, staging / "storage")
    final = shutil.make_archive(str(base), "zip", staging)
    shutil.rmtree(staging, ignore_errors=True)
    return Path(final)


init_storage()
