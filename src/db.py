from __future__ import annotations

import json
from typing import Iterable, List, Dict, Tuple, Optional

import psycopg

from .config import DbConfig


def get_conn(cfg: DbConfig) -> psycopg.Connection:
    return psycopg.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        dbname=cfg.name,
    )


def init_db(cfg: DbConfig) -> None:
    ddl_runs = (
        """
        CREATE TABLE IF NOT EXISTS moderation_runs (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            acceptable BOOLEAN NOT NULL,
            source_id TEXT,
            verdict_json JSONB
        );
        """
    )

    ddl_detections = (
        """
        CREATE TABLE IF NOT EXISTS moderation_detections (
            id BIGSERIAL PRIMARY KEY,
            run_id BIGINT NOT NULL REFERENCES moderation_runs(id) ON DELETE CASCADE,
            type TEXT,
            category TEXT,
            value TEXT,
            image_path TEXT,
            object_key TEXT
        );
        """
    )

    with get_conn(cfg) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl_runs)
            cur.execute(ddl_detections)
        conn.commit()


def health_check(cfg: DbConfig) -> bool:
    try:
        with get_conn(cfg) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                _ = cur.fetchone()
        return True
    except Exception:
        return False


def fetch_paid_ads(conn: psycopg.Connection, limit: Optional[int] = None) -> List[Tuple[str, str, str]]:
    sql = (
        """
        select au.id, au.description, ai.image_url
        from advertisement_auto au
        inner join public.advertisement_images ai on au.id = ai.advertisement_id
        where au.status = 'PAID'
        order by au.created_at asc
        """
    )
    if limit is not None:
        sql += " limit %s"
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return [(str(r[0]), r[1], r[2]) for r in cur.fetchall()]
    else:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [(str(r[0]), r[1], r[2]) for r in cur.fetchall()]


def group_ads(rows: Iterable[Tuple[str, str, str]]) -> Dict[str, Dict[str, object]]:
    grouped: Dict[str, Dict[str, object]] = {}
    for ad_id, description, image_url in rows:
        g = grouped.setdefault(ad_id, {"description": description, "image_urls": []})
        # На случай, если у одной записи пустое description, сохраняем непустое
        if not g.get("description") and description:
            g["description"] = description
        if image_url:
            g["image_urls"].append(image_url)
    return grouped


def save_run(conn: psycopg.Connection, acceptable: bool, source_id: str, verdict_json: dict) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO moderation_runs(acceptable, source_id, verdict_json)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (acceptable, source_id, json.dumps(verdict_json, ensure_ascii=False)),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    return int(run_id)


def save_detections(conn: psycopg.Connection, run_id: int, items: List[dict]) -> None:
    if not items:
        return
    rows = []
    for it in items:
        rows.append(
            (
                run_id,
                it.get("type"),
                it.get("category"),
                it.get("value"),
                it.get("image"),
                it.get("object_key"),
            )
        )
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO moderation_detections(run_id, type, category, value, image_path, object_key)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
    conn.commit()
