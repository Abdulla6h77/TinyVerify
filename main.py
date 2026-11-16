import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

def verify(request):
    candidates = {}
    for row in request["records"]:
        registry = row["registry"]
        url = urlsplit(row["source_url"])
        if registry not in request["registry_hosts"] or url.scheme != "https" or url.hostname not in request["registry_hosts"][registry] or url.username or url.password:
            raise ValueError("Record source must belong to the configured official registry")
        if not all(str(row[field]).strip() for field in ("number", "name", "status", "checked_at")):
            raise ValueError("Record is missing identity, status, or check time")
        fields = {"name": "name", "record_type": "record_type", "jurisdiction": "jurisdiction"}
        if all(" ".join(row[field].casefold().split()) == " ".join(request[key].casefold().split()) for key, field in fields.items()):
            identity = (registry, row["number"])
            if identity in candidates and candidates[identity]["status"] != row["status"]:
                return {"status": "conflicting_records", "matches": [candidates[identity], row]}
            candidates[identity] = row
    prior = {(item["registry"], item["number"]): item["status"] for item in request.get("previous", [])}
    matches = list(candidates.values())
    changes = [{"registry": r["registry"], "number": r["number"], "previous_status": prior[key],
                "current_status": r["status"], "source_url": r["source_url"], "checked_at": r["checked_at"]}
               for key, r in candidates.items() if key in prior and prior[key] != r["status"]]
    status = {0: "no_match", 1: "matched"}.get(len(matches), "ambiguous")
    if request.get("unavailable_registries"):
        status = "incomplete"
    return {"status": status, "matches": matches, "status_changes": changes,
            "unavailable_registries": request.get("unavailable_registries", [])}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = verify(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps({"mode": "offline_input", **result}, indent=2))

if __name__ == "__main__":
    main()
