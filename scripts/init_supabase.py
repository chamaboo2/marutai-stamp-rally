from __future__ import annotations

import csv
import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "sql" / "001_schema.sql"
CSV_PATH = ROOT / "data" / "facilities.csv"


def prompt(label: str, *, secret: bool = False, default: str = "") -> str:
    current = os.getenv(label, "").strip()
    if current:
        return current
    suffix = f" [{default}]" if default else ""
    reader = getpass.getpass if secret else input
    value = reader(f"{label}{suffix}: ").strip()
    return value or default


def as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def main() -> int:
    try:
        import psycopg
    except ImportError:
        print("psycopg is not installed. Run: pip install -r requirements.txt")
        return 2

    print("=== まるたいスタンプラリー / Supabase 初期化 ===")
    print("Supabase Dashboard の Connect から PostgreSQL connection string をコピーしてください。")
    db_url = prompt("SUPABASE_DB_URL", secret=True)
    if not db_url:
        print("SUPABASE_DB_URL が必要です。")
        return 2

    if not SQL_PATH.exists():
        print(f"SQL file not found: {SQL_PATH}")
        return 2

    sql = SQL_PATH.read_text(encoding="utf-8")

    try:
        with psycopg.connect(db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, prepare=False)
                imported = 0
                if CSV_PATH.exists():
                    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
                        for row in csv.DictReader(fh):
                            if not row.get("name"):
                                continue
                            cur.execute(
                                """
                                insert into public.facilities (
                                    id, name, category, ward, address, latitude, longitude,
                                    has_open_air_bath, has_natural_hot_spring, website_url, active
                                ) values (
                                    nullif(%s, '')::uuid, %s, %s, %s, %s,
                                    nullif(%s, '')::double precision,
                                    nullif(%s, '')::double precision,
                                    %s, %s, nullif(%s, ''), %s
                                )
                                on conflict (id) do update set
                                    name = excluded.name,
                                    category = excluded.category,
                                    ward = excluded.ward,
                                    address = excluded.address,
                                    latitude = excluded.latitude,
                                    longitude = excluded.longitude,
                                    has_open_air_bath = excluded.has_open_air_bath,
                                    has_natural_hot_spring = excluded.has_natural_hot_spring,
                                    website_url = excluded.website_url,
                                    active = excluded.active;
                                """,
                                (
                                    row.get("id", ""),
                                    row.get("name", ""),
                                    row.get("category", "other"),
                                    row.get("ward", ""),
                                    row.get("address", ""),
                                    row.get("latitude", ""),
                                    row.get("longitude", ""),
                                    as_bool(row.get("has_open_air_bath")),
                                    as_bool(row.get("has_natural_hot_spring")),
                                    row.get("website_url", ""),
                                    as_bool(row.get("active", "true")),
                                ),
                            )
                            imported += 1
    except Exception as exc:
        print("\n初期化に失敗しました。")
        print(str(exc))
        return 1

    print("\n初期化完了")
    print("- facilities テーブル: OK")
    print("- visits テーブル: OK")
    print("- visit-photos Storage bucket: OK")
    print(f"- facilities.csv 取込: {imported}件")
    print("\n次は Streamlit Cloud の Secrets に SUPABASE_URL と SUPABASE_SERVICE_ROLE_KEY を登録してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
