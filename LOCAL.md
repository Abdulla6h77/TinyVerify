# Local workflow

Match records returned by registry lookups, preserve ambiguity, and compare status for the same registry record.

Requires Python 3.10 or later. From this project folder:

```powershell
python main.py example.json
```

The example uses synthetic input. Output marked `offline_input` comes from supplied files.

## Provider entry point

Set `TINYFISH_API_KEY` in the process environment. The provider entry point uses TinyFish's documented service endpoints. Live verification is pending.

`python tinyfish.py lookup.json` runs one bounded Agent lookup per configured registry, then Fetch corroborates identity, record number, and status. Use the example's name, record_type, and jurisdiction fields. Add `registries` as an object mapping registry IDs to objects with `url` and `hosts`. See the README for creating a saved Companies House watch with `watch.py` and using it to compare Monitor observations.

Connect Agent and Fetch to two confirmed official registries, then wire Monitor events to the same registry ID and record number.
