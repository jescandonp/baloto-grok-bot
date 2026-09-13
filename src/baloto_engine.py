#!/usr/bin/env python3
"""Compatibilidad: reexporta el motor unificado. Usa --game para elegir sorteo."""
from family_engine import FamilyEngine, Ticket, load_engine, main
BalotoEngine = FamilyEngine
if __name__ == "__main__":
    raise SystemExit(main())
