# TinyVerify

Check public organization records across configured official registries. TinyFish Agent discovers record pages, TinyFish Fetch corroborates visible names, registration numbers, and statuses, and TinyFish Monitor watches a selected Companies House record.

Requires Python 3.10 or later. Configure `TINYFISH_API_KEY` in the process environment or a private project `.env`.

```powershell
python -B tinyfish.py demo-oxfam.json --dry-run
python -B tinyfish.py demo-oxfam.json | Set-Content -Encoding utf8 .local/oxfam-live.json
```

Create the local output directory first with `New-Item -Force -ItemType Directory .local`. The live output includes a per-registry outcome, checked time, and source link. An unavailable registry is recorded separately from a confirmed no match. Unknown expiry or disciplinary history is returned as null.

Use the saved lookup result to create a watch for the exact company number. Monitor creation registers a schedule and captures a baseline. Check the watch once on demand and pause a demonstration watch when finished.

```powershell
python -B watch.py add .local/oxfam-live.json 00612172
python -B watch.py check MONITOR_ID
python -B watch.py pause MONITOR_ID
```

The watch stores observations in local SQLite. It compares the official status field, checks the record number, and ignores replayed Monitor run IDs. The provider's scheduled Monitor checks use the same status-specific purpose. See [requirements](SPEC.md) and [local workflow](LOCAL.md).

See the [live two-registry and Monitor demo](DEMO.md).
