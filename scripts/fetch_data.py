#!/usr/bin/env python3
"""Descarga o actualiza los CSV historicos de la familia Baloto."""
from __future__ import annotations
import sys
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from games import GAMES
DATA = ROOT / "data"
UA = "BalotoAnalyst/1.0"

def fetch(game: str | None = None) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    specs = [GAMES[game]] if game else list(GAMES.values())
    for spec in specs:
        dest = DATA / spec.csv_name
        req = urllib.request.Request(spec.csv_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        lines = data.count(b"\n")
        print(f"{spec.name:12} {dest.name:16} {len(data):6} bytes  ~{max(0, lines-1)} sorteos")

if __name__ == "__main__":
    fetch(sys.argv[1] if len(sys.argv) > 1 else None)
