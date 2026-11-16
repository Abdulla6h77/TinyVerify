import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request

API = "https://agent.tinyfish.ai"
DRY_RUN = False
REQUEST_PLAN = []

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def request(url, body=None, *, method=None):
    method = method or ("GET" if body is None else "POST")
    if DRY_RUN:
        REQUEST_PLAN.append({"method": method, "url": url, "body": body})
        return {}
    key = os.environ.get("TINYFISH_API_KEY", "").strip()
    private_config = Path(__file__).with_name(".env")
    if not key and private_config.is_file():
        for line in private_config.read_text(encoding="utf-8-sig").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "TINYFISH_API_KEY":
                key = value.strip().strip("\"'")
                break
    if not key:
        raise SystemExit("Set TINYFISH_API_KEY for this process.")
    req = Request(url, data=json.dumps(body).encode() if body is not None else None,
                  headers={"X-API-Key": key, "Content-Type": "application/json"}, method=method)
    try:
        with build_opener(NoRedirect()).open(req, timeout=90) as result:
            return json.load(result)
    except HTTPError as error:
        raise SystemExit(f"TinyFish HTTP {error.code}. Check saved jobs before retrying a start.") from None
    except OSError as error:
        raise SystemExit(f"TinyFish request failed ({type(error).__name__}). Check saved jobs before retrying a start.") from None

def official_url(value, hosts):
    url = urlsplit(value)
    if url.scheme != "https" or url.hostname not in hosts or url.username or url.password or url.port not in (None, 443):
        raise ValueError("Expected an HTTPS URL on an explicitly configured official hostname")
    return value

def discover(url, goal, hosts):
    data = request(API + "/v1/automation/run", {
        "url": official_url(url, hosts), "goal": goal,
        "max_steps": 12, "max_duration_seconds": 60,
    })
    if data.get("status") != "COMPLETED":
        raise ValueError("Agent did not complete the lookup")
    result = data.get("result") or data.get("resultJson")
    result = json.loads(result) if isinstance(result, str) else result
    if not isinstance(result, dict):
        raise ValueError("Agent did not return a structured result")
    return result, data.get("run_id")

def fetch_text(url, hosts):
    official_url(url, hosts)
    payload = request("https://api.fetch.tinyfish.ai", {"urls": [url], "format": "markdown", "ttl": 0})
    for row in payload.get("results", []):
        if row.get("url") == url and isinstance(row.get("text"), str):
            official_url(row.get("final_url") or url, hosts)
            return row["text"]
    raise ValueError("Fetch could not corroborate the official record")

def company_status(text):
    lines = [re.sub(r"^[*#> -]+", "", line.replace("**", "")).strip()
             for line in text.splitlines() if line.strip()]
    lines = [line for line in lines if line]
    for label, value in zip(lines, lines[1:]):
        if label.casefold().rstrip(":") == "company status":
            return value
    raise ValueError("Fetch did not expose the Companies House status field")


def create_monitor(url, hosts, purpose):
    return request(API + "/v1/monitors", {
        "type": "fetch", "config": {"url": official_url(url, hosts), "format": "markdown"},
        "schedule_cron": "0 */6 * * *", "purpose": purpose,
    })

import argparse
from datetime import datetime, timezone
from main import verify

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--monitor-number", help="Explicitly create a billable watch for this unique match")
    parser.add_argument("--dry-run", action="store_true", help="Validate input and print the request plan without network access")
    args = parser.parse_args()
    DRY_RUN = args.dry_run
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    sources = data["registries"]
    if len(sources) < 2:
        parser.error("Configure at least two official registries")
    query = json.dumps({key: data[key] for key in ("name", "record_type", "jurisdiction")})
    for source in sources.values():
        official_url(source["url"], source["hosts"])
    if DRY_RUN:
        print(json.dumps({"mode": "dry_run", "agent_lookups": len(sources),
                          "agent_step_ceiling": len(sources) * 12,
                          "recurring_monitor_requested": bool(args.monitor_number),
                          "fetch": "Up to the corroboration limit per registry"}, indent=2))
        raise SystemExit(0)
    data["records"], data["unavailable_registries"], data["registry_hosts"] = [], [], {}
    diagnostics = {}
    for registry, source in sources.items():
        hosts = data["registry_hosts"][registry] = source["hosts"]
        try:
            entry = source["url"]
            if registry == "companies_house" and urlsplit(entry).path == "/search":
                entry += "?" + urlencode({"q": data["name"]})
            result, agent_run_id = discover(entry, "Read only this official registry. Verify the supplied entity with exact spelling. "
                              "without logging in or bypassing restrictions. Return {records:[{name,number,status,"
                              "source_url,expiry_date,disciplinary_actions}]} with exact visible values. "
                              "Use the official organization record page, never an officer page. For the Charity "
                              "Commission status use the exact registration or charity reporting status shown. "
                              "Return an empty records array only for a confirmed no-match. Query: " + query, hosts)
            diagnostics[registry] = {"agent_run_id": agent_run_id}
            if not isinstance(result.get("records"), list) or len(result["records"]) > 5:
                raise ValueError("Lookup exceeded the five-record corroboration limit")
            verified_rows = []
            for item in result["records"]:
                page_text = fetch_text(item["source_url"], hosts)
                text = " ".join(page_text.casefold().split())
                for key in ("name", "number"):
                    value = " ".join(str(item[key]).casefold().split())
                    if not value or not re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", text):
                        raise ValueError(f"Fetch could not corroborate the record {key}")
                status = company_status(page_text) if registry == "companies_house" else item["status"]
                normalized = " ".join(str(status).casefold().split())
                if not normalized or not re.search(r"(?<!\w)" + re.escape(normalized) + r"(?!\w)", text):
                    raise ValueError("Fetch could not corroborate the record status")
                expiry = item.get("expiry_date")
                if not isinstance(expiry, str) or not expiry.strip() or " ".join(expiry.casefold().split()) not in text:
                    expiry = None
                actions = item.get("disciplinary_actions")
                if not isinstance(actions, list) or not actions or not all(
                    isinstance(action, str) and action.strip() and " ".join(action.casefold().split()) in text
                    for action in actions
                ):
                    actions = None
                verified_rows.append({
                    "name": item["name"], "number": item["number"], "status": status,
                    "source_url": item["source_url"], "expiry_date": expiry, "disciplinary_actions": actions,
                    "registry": registry, "record_type": data["record_type"], "jurisdiction": data["jurisdiction"],
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                })
            data["records"].extend(verified_rows)
        except (ValueError, KeyError, TypeError) as error:
            diagnostics.setdefault(registry, {})["error"] = (
                str(error) if type(error) is ValueError else "Invalid provider record fields"
            )
            data["unavailable_registries"].append(registry)
    result = verify(data)
    result["provider_checks"] = diagnostics
    by_registry = {}
    for row in result["matches"]:
        by_registry.setdefault(row["registry"], []).append(row)
    if result["status"] == "ambiguous" and all(len(rows) == 1 for rows in by_registry.values()):
        result["status"] = "verified_records"
    result["registry_checks"] = {
        registry: ("unavailable" if registry in data["unavailable_registries"] else
                   "matched" if len(by_registry.get(registry, [])) == 1 else
                   "ambiguous" if registry in by_registry else "no_match")
        for registry in sources
    }
    if args.monitor_number:
        if result["status"] != "matched" or result["matches"][0]["number"] != args.monitor_number:
            parser.error("A monitor requires one corroborated record and its exact number")
        row = result["matches"][0]
        result["monitor"] = create_monitor(row["source_url"], data["registry_hosts"][row["registry"]],
                                           "Flag a status change for registry record " + row["number"])
    print(json.dumps({"mode": "provider_lookup", **result}, indent=2))
