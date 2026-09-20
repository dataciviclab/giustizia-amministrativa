#!/usr/bin/env python3
"""Download all OpenGA data for a given dataset type into a single CSV.

Supported types:
  - ricorsi-appalto: Ricorsi in materia d'appalto (31 sedi)
  - sentenze: Sentenze (31 sedi)
  - decreti: Decreti (31 sedi)
  - ordinanze: Ordinanze (31 sedi)
  - ricorsi-definiti: Ricorsi definiti per classificazione ed esito (31 sedi)
  - ricorsi-pervenuti-class: Ricorsi pervenuti per classificazione (31 sedi)
  - provvedimenti: Provvedimenti pubblicati (31 sedi)

Usage:
    python prefetch.py output.csv                          # default: ricorsi-appalto
    python prefetch.py output.csv --type sentenze
    python prefetch.py output.csv --type decreti
    python prefetch.py output.csv --dry-run
"""

import argparse
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

CKAN_API = "https://openga.giustizia-amministrativa.it/api/3/action/package_show"

DATASET_TYPES = {
    "ricorsi-appalto": {
        "suffix": "ricorsi-pervenuti-in-materia-d-appalto",
        "year_col": "ANNO_DEPOSITO_RICORSO",
    },
    "sentenze": {
        "suffix": "sentenze",
        "year_col": "ANNO_PUBBLICAZIONE",
    },
    "decreti": {
        "suffix": "decreti",
        "year_col": "ANNO_PUBBLICAZIONE",
    },
    "ordinanze": {
        "suffix": "ordinanze",
        "year_col": "ANNO_PUBBLICAZIONE",
    },
    "ricorsi-definiti": {
        "suffix": "ricorsi-definiti-per-classificazione-ed-esito",
        "year_col": "ANNO_SENTENZA",
    },
    "ricorsi-pervenuti-class": {
        "suffix": "ricorsi-pervenuti-per-classificazione",
        "year_col": "ANNO_DEPOSITO",
    },
    "provvedimenti": {
        "suffix": "provvedimenti-pubblicati",
        "year_col": "ANNO_PUBBLICAZIONE",
    },
}

SEDI = [
    "cds", "cga-sicilia",
    "tar-abruzzo-l-aquila", "tar-abruzzo-pescara", "tar-basilicata",
    "tar-calabria-catanzaro", "tar-calabria-reggio-calabria",
    "tar-campania-napoli", "tar-campania-salerno",
    "tar-emilia-romagna-bologna", "tar-emilia-romagna-parma",
    "tar-friuli-venezia-giulia", "tar-lazio-latina", "tar-lazio-roma",
    "tar-liguria", "tar-lombardia-brescia", "tar-lombardia-milano",
    "tar-marche", "tar-molise", "tar-piemonte",
    "tar-puglia-bari", "tar-puglia-lecce", "tar-sardegna",
    "tar-sicilia-catania", "tar-sicilia-palermo", "tar-toscana",
    "tar-umbria", "tar-valle-d-aosta", "tar-veneto",
    "trga-bolzano", "trga-trento",
]


def fetch_csv_urls(dataset_id: str) -> list[str]:
    """Return CSV download URLs for a CKAN dataset."""
    url = f"{CKAN_API}?id={dataset_id}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    if not data.get("success"):
        raise RuntimeError(f"CKAN API failed for {dataset_id}")
    return [r["url"] for r in data["result"].get("resources", []) if r.get("format") == "CSV"]


def main():
    parser = argparse.ArgumentParser(description="Download OpenGA data")
    parser.add_argument("output", help="Output CSV path")
    parser.add_argument("--type", choices=DATASET_TYPES.keys(), default="ricorsi-appalto",
                        help="Dataset type (default: ricorsi-appalto)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-dir", help="Directory to cache downloads")
    args = parser.parse_args()

    ds_config = DATASET_TYPES[args.type]
    cache_dir = Path(args.cache_dir) if args.cache_dir else None
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    fieldnames: list[str] | None = None

    for i, src_slug in enumerate(SEDI):
        ds_id = f"{src_slug}-{ds_config['suffix']}"
        print(f"[{i+1}/{len(SEDI)}] {src_slug}...", end=" ", flush=True)

        if args.dry_run:
            print("(dry-run)")
            continue

        try:
            urls = fetch_csv_urls(ds_id)
            count = 0
            for url in urls:
                if cache_dir:
                    uuid_part = url.split("/resource/")[1].split("/")[0]
                    cache_file = cache_dir / f"{uuid_part}.csv"
                    if cache_file.exists():
                        content = cache_file.read_text(encoding="utf-8")
                    else:
                        content = urllib.request.urlopen(url).read().decode("utf-8")
                        cache_file.write_text(content, encoding="utf-8")
                else:
                    content = urllib.request.urlopen(url).read().decode("utf-8")

                reader = csv.DictReader(io.StringIO(content))
                if fieldnames is None:
                    fieldnames = reader.fieldnames
                for row in reader:
                    all_rows.append(row)
                    count += 1
            print(f"{count} rows")
        except Exception as e:
            print(f"ERROR: {e}")

    if args.dry_run:
        print(f"\nWould concatenate {len(SEDI)} sources into {args.output}")
        return

    if not all_rows:
        print("No data downloaded!", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    size_kb = output_path.stat().st_size / 1024
    print(f"\n{len(all_rows)} rows -> {output_path} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
