from __future__ import annotations

import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "facilities.csv"
load_dotenv(ROOT / ".env")


def _secret(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


def supabase_configured() -> bool:
    return bool(_secret("SUPABASE_URL") and _secret("SUPABASE_SERVICE_ROLE_KEY"))


@st.cache_resource(show_spinner=False)
def _client():
    if not supabase_configured():
        return None
    from supabase import create_client

    return create_client(_secret("SUPABASE_URL"), _secret("SUPABASE_SERVICE_ROLE_KEY"))


def _csv_records() -> list[dict[str, Any]]:
    if not CSV_PATH.exists():
        return []
    df = pd.read_csv(CSV_PATH)
    if df.empty:
        return []
    for col in ["has_open_air_bath", "has_natural_hot_spring", "active"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def _demo_visits() -> list[dict[str, Any]]:
    return st.session_state.setdefault("demo_visits", [])


def list_facilities(active_only: bool = True) -> list[dict[str, Any]]:
    client = _client()
    if client:
        q = client.table("facilities").select("*").order("ward").order("name")
        if active_only:
            q = q.eq("active", True)
        return q.execute().data or []
    rows = _csv_records()
    return [r for r in rows if (not active_only or bool(r.get("active", True)))]


def get_facility(facility_id: str) -> dict[str, Any] | None:
    if not facility_id:
        return None
    client = _client()
    if client:
        data = client.table("facilities").select("*").eq("id", facility_id).limit(1).execute().data or []
        return data[0] if data else None
    return next((r for r in _csv_records() if str(r.get("id")) == str(facility_id)), None)


def list_visits() -> list[dict[str, Any]]:
    client = _client()
    if client:
        return (
            client.table("visits")
            .select("*, facilities(name,ward,category,has_open_air_bath,has_natural_hot_spring)")
            .order("visited_date", desc=True)
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
    visits = list(_demo_visits())
    facilities = {str(f.get("id")): f for f in _csv_records()}
    for visit in visits:
        visit["facilities"] = facilities.get(str(visit.get("facility_id")), {})
    return visits


def visits_for_facility(facility_id: str) -> list[dict[str, Any]]:
    return [v for v in list_visits() if str(v.get("facility_id")) == str(facility_id)]


def visited_facility_ids() -> set[str]:
    return {str(v.get("facility_id")) for v in list_visits()}


def _upload_private(path: str, data: bytes, content_type: str) -> str:
    client = _client()
    bucket = _secret("SUPABASE_STORAGE_BUCKET", "visit-photos")
    client.storage.from_(bucket).upload(
        path=path,
        file=data,
        file_options={"content-type": content_type, "upsert": "false"},
    )
    return path


def signed_photo_url(path: str | None, expires_in: int = 3600):
    if not path:
        return None
    client = _client()
    if not client:
        if path.startswith("data:image/") and "," in path:
            import base64
            try:
                return base64.b64decode(path.split(",", 1)[1])
            except Exception:
                return None
        return None
    bucket = _secret("SUPABASE_STORAGE_BUCKET", "visit-photos")
    try:
        data = client.storage.from_(bucket).create_signed_url(path, expires_in)
        return data.get("signedURL") or data.get("signedUrl")
    except Exception:
        return None


def create_visit(
    facility_id: str,
    visited_date: str,
    original_bytes: bytes,
    stamped_bytes: bytes,
) -> dict[str, Any]:
    client = _client()
    visit_id = str(uuid4())
    if client:
        original_path = f"original/{facility_id}/{visit_id}.jpg"
        stamped_path = f"stamped/{facility_id}/{visit_id}.jpg"
        _upload_private(original_path, original_bytes, "image/jpeg")
        try:
            _upload_private(stamped_path, stamped_bytes, "image/jpeg")
            row = {
                "id": visit_id,
                "facility_id": facility_id,
                "visited_date": visited_date,
                "original_photo_url": original_path,
                "stamped_photo_url": stamped_path,
            }
            return client.table("visits").insert(row).execute().data[0]
        except Exception:
            # Do not leave an orphaned original file after a partial failure.
            try:
                client.storage.from_(_secret("SUPABASE_STORAGE_BUCKET", "visit-photos")).remove([original_path])
            finally:
                raise

    import base64

    stamped_uri = "data:image/jpeg;base64," + base64.b64encode(stamped_bytes).decode("ascii")
    original_uri = "data:image/jpeg;base64," + base64.b64encode(original_bytes).decode("ascii")
    row = {
        "id": visit_id,
        "facility_id": facility_id,
        "visited_date": visited_date,
        "original_photo_url": original_uri,
        "stamped_photo_url": stamped_uri,
        "created_at": visited_date,
    }
    _demo_visits().append(row)
    return row


def import_csv_to_supabase() -> tuple[int, str]:
    """Optional admin helper for initial data loading. Not exposed in the MVP UI."""
    client = _client()
    if not client:
        return 0, "Supabase is not configured."
    rows = _csv_records()
    if not rows:
        return 0, "facilities.csv is empty."
    payload = [{k: v for k, v in r.items() if v is not None and str(v) != "nan"} for r in rows]
    client.table("facilities").upsert(payload, on_conflict="id").execute()
    return len(payload), "Imported."
