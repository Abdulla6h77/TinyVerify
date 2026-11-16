"""Watch a corroborated Companies House record through TinyFish Monitor."""

import argparse
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from urllib.parse import urlsplit

from tinyfish import API, company_status, create_monitor, official_url, request

HOSTS = ["find-and-update.company-information.service.gov.uk"]
def read_snapshot(run, url, number):
    for page in run.get("results", []):
        if page.get("url") != url or (page.get("final_url") or url) != url:
            continue
        text = page.get("text") or ""
        if re.search(r"(?<!\w)" + re.escape(number) + r"(?!\w)", text, re.IGNORECASE):
            return company_status(text)
    raise ValueError("Monitor did not return a readable status for the selected official record.")


def record_run(db, monitor_id, run):
    db.execute("BEGIN IMMEDIATE")
    watch = db.execute(
        "SELECT url, number, status FROM watches WHERE id = ?", (monitor_id,)
    ).fetchone()
    if watch is None:
        raise ValueError("Unknown local monitor.")
    url, number, previous = watch
    current = read_snapshot(run, url, number)
    inserted = db.execute(
        "INSERT OR IGNORE INTO observations VALUES (?, ?, ?, ?, ?)",
        (monitor_id, str(UUID(run["id"])), current, run.get("outcome"),
         datetime.now(timezone.utc).isoformat()),
    ).rowcount
    if inserted:
        db.execute("UPDATE watches SET status = ? WHERE id = ?", (current, monitor_id))
    return {"monitor_id": monitor_id, "source_url": url, "number": number,
            "previous_status": previous, "current_status": current if inserted else previous,
            "status_changed": bool(inserted and previous.casefold() != current.casefold()),
            "duplicate": not inserted}


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".local/watches.sqlite"))
    sub = parser.add_subparsers(dest="action", required=True)
    add = sub.add_parser("add")
    add.add_argument("lookup", type=Path)
    add.add_argument("number")
    for name in ("check", "pause"):
        action = sub.add_parser(name)
        action.add_argument("monitor_id", type=UUID)
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(args.db)) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS watches (
              id TEXT PRIMARY KEY, url TEXT NOT NULL UNIQUE, number TEXT NOT NULL, status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS observations (
              monitor_id TEXT NOT NULL, run_id TEXT NOT NULL, status TEXT NOT NULL,
              outcome TEXT, checked_at TEXT NOT NULL, PRIMARY KEY (monitor_id, run_id)
            );
        """)
        if args.action == "add":
            lookup = json.loads(args.lookup.read_text(encoding="utf-8-sig"))
            candidates = [r for r in lookup["matches"] if r["registry"] == "companies_house"
                          and r["number"].casefold() == args.number.casefold()]
            if lookup.get("mode") != "provider_lookup" or len(candidates) != 1:
                raise ValueError("A watch needs one live Companies House match with the selected number.")
            row = candidates[0]
            url = official_url(row["source_url"], HOSTS)
            if urlsplit(url).path.rstrip('/') != '/company/' + row['number']:
                raise ValueError("Use the Companies House overview for the exact record.")
            if db.execute("SELECT 1 FROM watches WHERE url = ?", (url,)).fetchone():
                raise ValueError("This record already has a saved watch.")
            created = create_monitor(url, HOSTS, "Flag only changes in the Company status field.")
            monitor_id = str(UUID(created["monitor"]["id"]))
            db.execute("INSERT INTO watches VALUES (?, ?, ?, ?)",
                       (monitor_id, url, row["number"], row["status"]))
            db.commit()
            print(json.dumps({"monitor_id": monitor_id, "provider_status": created["monitor"]["status"]}))
            print(json.dumps(record_run(db, monitor_id, created["run"])))
        else:
            monitor_id = str(args.monitor_id)
            if db.execute("SELECT 1 FROM watches WHERE id = ?", (monitor_id,)).fetchone() is None:
                raise ValueError("Unknown local monitor.")
            path = API + "/v1/monitors/" + monitor_id
            if args.action == "pause":
                result = request(path, {"status": "paused"}, method="PATCH")
                print(json.dumps({"monitor_id": monitor_id, "provider_status": (result.get("monitor") or result)["status"]}))
            else:
                result = request(path + "/runs", {}, method="POST")
                print(json.dumps(record_run(db, monitor_id, result["run"])))


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        raise SystemExit(str(error))
