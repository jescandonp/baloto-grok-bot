#!/usr/bin/env python3
"""Baloto Analyst Engine. Cada jugada 5/43+1/16 tiene p = 1/15_401_568."""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
from typing import Iterable

import pandas as pd

MAIN_MAX = 43
SB_MAX = 16
PICK = 5
TOTAL_COMBOS = math.comb(MAIN_MAX, PICK) * SB_MAX
DATA_DEFAULT = Path(__file__).resolve().parents[1] / "data" / "baloto.csv"


@dataclass
class Ticket:
    mains: list[int]
    superbalota: int
    method: str
    notes: str = ""

    def pretty(self) -> str:
        nums = " - ".join(f"{n:02d}" for n in self.mains)
        return f"{nums}  +  SB {self.superbalota:02d}   [{self.method}]"


class BalotoEngine:
    def __init__(self, csv_path: Path | str = DATA_DEFAULT):
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"No se encontró el histórico: {self.csv_path}")
        raw = pd.read_csv(self.csv_path)
        required = {"draw_date", "sorteo", "n1", "n2", "n3", "n4", "n5", "balota"}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(f"CSV incompleto, faltan columnas: {missing}")
        raw["draw_date"] = pd.to_datetime(raw["draw_date"])
        self.df = raw.sort_values("draw_date").reset_index(drop=True)
        self.draws = len(self.df)
        self.expected_main = self.draws * PICK / MAIN_MAX
        self.expected_sb = self.draws / SB_MAX
        self._compute()

    def _compute(self) -> None:
        mains = self.df[["n1", "n2", "n3", "n4", "n5"]]
        flat = mains.values.flatten()
        self.freq_main = Counter(int(x) for x in flat)
        self.freq_sb = Counter(int(x) for x in self.df["balota"])
        last_main = {n: None for n in range(1, MAIN_MAX + 1)}
        last_sb = {n: None for n in range(1, SB_MAX + 1)}
        for i, row in self.df.iterrows():
            for col in ("n1", "n2", "n3", "n4", "n5"):
                last_main[int(row[col])] = i
            last_sb[int(row["balota"])] = i
        last_idx = self.draws - 1
        self.delay_main = {
            n: (last_idx - last_main[n]) if last_main[n] is not None else self.draws
            for n in range(1, MAIN_MAX + 1)
        }
        self.delay_sb = {
            n: (last_idx - last_sb[n]) if last_sb[n] is not None else self.draws
            for n in range(1, SB_MAX + 1)
        }
        self.last_date_main = {
            n: (self.df.loc[last_main[n], "draw_date"].date() if last_main[n] is not None else None)
            for n in range(1, MAIN_MAX + 1)
        }
        self.last_date_sb = {
            n: (self.df.loc[last_sb[n], "draw_date"].date() if last_sb[n] is not None else None)
            for n in range(1, SB_MAX + 1)
        }
        pair_c: Counter = Counter()
        for _, row in mains.iterrows():
            nums = sorted(int(x) for x in row.tolist())
            for p in combinations(nums, 2):
                pair_c[p] += 1
        self.top_pairs = pair_c.most_common(20)
        sums = mains.sum(axis=1)
        self.sum_mean = float(sums.mean())
        self.sum_std = float(sums.std())
        self.sum_median = float(sums.median())
        self.latest = self.df.iloc[-1]

    def snapshot(self) -> dict:
        last = self.latest
        mains = sorted(int(last[c]) for c in ("n1", "n2", "n3", "n4", "n5"))
        return {
            "sorteos": self.draws,
            "desde": str(self.df["draw_date"].iloc[0].date()),
            "hasta": str(last["draw_date"].date()),
            "ultimo_sorteo": int(last["sorteo"]),
            "ultimo_resultado": {
                "fecha": str(last["draw_date"].date()),
                "numeros": mains,
                "superbalota": int(last["balota"]),
            },
            "esperados": {
                "frecuencia_principal": round(self.expected_main, 2),
                "frecuencia_superbalota": round(self.expected_sb, 2),
            },
            "suma_5_numeros": {
                "media": round(self.sum_mean, 2),
                "mediana": round(self.sum_median, 2),
                "desviacion": round(self.sum_std, 2),
            },
            "espacio_combinatorio": TOTAL_COMBOS,
            "prob_jackpot": f"1 en {TOTAL_COMBOS:,}".replace(",", "."),
        }

    def ranked_main(self, by: str = "freq") -> list[tuple[int, float]]:
        if by == "freq":
            return sorted(((n, float(self.freq_main[n])) for n in range(1, MAIN_MAX + 1)), key=lambda x: (-x[1], x[0]))
        if by == "delay":
            return sorted(((n, float(self.delay_main[n])) for n in range(1, MAIN_MAX + 1)), key=lambda x: (-x[1], x[0]))
        raise ValueError(by)

    def analysis_report(self) -> str:
        snap = self.snapshot()
        hot = self.ranked_main("freq")[:10]
        cold = list(reversed(self.ranked_main("freq")))[:10]
        late = self.ranked_main("delay")[:10]
        hot_sb = sorted(self.freq_sb.items(), key=lambda x: (-x[1], x[0]))[:5]
        late_sb = sorted(self.delay_sb.items(), key=lambda x: (-x[1], x[0]))[:5]
        lines = [
            "# Informe histórico Baloto",
            "",
            f"- Sorteos analizados: **{snap['sorteos']}** ({snap['desde']} → {snap['hasta']})",
            f"- Último sorteo #{snap['ultimo_sorteo']} ({snap['ultimo_resultado']['fecha']}): "
            f"{' - '.join(f'{n:02d}' for n in snap['ultimo_resultado']['numeros'])} + SB {snap['ultimo_resultado']['superbalota']:02d}",
            f"- Frecuencia esperada por número principal: {snap['esperados']['frecuencia_principal']}",
            f"- Frecuencia esperada por Superbalota: {snap['esperados']['frecuencia_superbalota']}",
            f"- Suma típica de los 5 números: media {snap['suma_5_numeros']['media']} / mediana {snap['suma_5_numeros']['mediana']}",
            f"- Jackpot teórico: **{snap['prob_jackpot']}** combinaciones igualmente probables.",
            "",
            "## Números principales más frecuentes (calientes)",
        ]
        for n, f in hot:
            delta = f - self.expected_main
            lines.append(f"- {n:02d}: {int(f)} veces (Δ {delta:+.1f}) · atraso {self.delay_main[n]} · última {self.last_date_main[n]}")
        lines += ["", "## Números principales menos frecuentes (fríos)"]
        for n, f in cold:
            delta = f - self.expected_main
            lines.append(f"- {n:02d}: {int(f)} veces (Δ {delta:+.1f}) · atraso {self.delay_main[n]} · última {self.last_date_main[n]}")
        lines += ["", "## Números principales más atrasados"]
        for n, d in late:
            lines.append(f"- {n:02d}: {int(d)} sorteos sin salir · freq {self.freq_main[n]} · última {self.last_date_main[n]}")
        lines += ["", "## Superbalota"]
        lines.append("Más frecuentes: " + ", ".join(f"{n:02d} ({c})" for n, c in hot_sb))
        lines.append("Más atrasadas: " + ", ".join(f"{n:02d} ({d} sorteos)" for n, d in late_sb))
        lines += ["", "## Pares que más han coincidido"]
        for (a, b), c in self.top_pairs[:10]:
            lines.append(f"- {a:02d}-{b:02d}: {c} veces")
        lines += [
            "",
            "## Lectura correcta de estos datos",
            "La frecuencia y el atraso describen el pasado. En un sorteo con bolas",
            "independientes y sin memoria, un número 'caliente' no tiene más probabilidad",
            "matemática de salir mañana que uno 'frío'.",
        ]
        return "\n".join(lines)

    def _weighted_sample(self, weights: dict[int, float], k: int, rng: random.Random) -> list[int]:
        pool = list(range(1, MAIN_MAX + 1))
        w = [max(weights[n], 1e-9) for n in pool]
        chosen: list[int] = []
        for _ in range(k):
            total = sum(w)
            r = rng.random() * total
            acc = 0.0
            idx = 0
            for i, wi in enumerate(w):
                acc += wi
                if acc >= r:
                    idx = i
                    break
            chosen.append(pool[idx])
            del pool[idx]
            del w[idx]
        return sorted(chosen)

    def _sb_weighted(self, weights: dict[int, float], rng: random.Random) -> int:
        pool = list(range(1, SB_MAX + 1))
        w = [max(weights[n], 1e-9) for n in pool]
        total = sum(w)
        r = rng.random() * total
        acc = 0.0
        for n, wi in zip(pool, w):
            acc += wi
            if acc >= r:
                return n
        return pool[-1]

    def generate_random(self, n: int = 5, seed: int | None = None) -> list[Ticket]:
        rng = random.Random(seed)
        tickets, seen = [], set()
        while len(tickets) < n:
            mains = sorted(rng.sample(range(1, MAIN_MAX + 1), PICK))
            sb = rng.randint(1, SB_MAX)
            key = (*mains, sb)
            if key in seen:
                continue
            seen.add(key)
            tickets.append(Ticket(mains, sb, "aleatorio", "Uniforme: misma p que cualquier otra jugada."))
        return tickets

    def generate_hot(self, n: int = 5, seed: int | None = None) -> list[Ticket]:
        rng = random.Random(seed)
        w_main = {i: float(self.freq_main[i]) ** 1.4 for i in range(1, MAIN_MAX + 1)}
        w_sb = {i: float(self.freq_sb[i]) ** 1.4 for i in range(1, SB_MAX + 1)}
        tickets, seen = [], set()
        while len(tickets) < n:
            mains = self._weighted_sample(w_main, PICK, rng)
            sb = self._sb_weighted(w_sb, rng)
            key = (*mains, sb)
            if key in seen:
                continue
            seen.add(key)
            tickets.append(Ticket(mains, sb, "probabilistico-frecuencia", "Muestreo ponderado por frecuencia histórica (pasado ≠ futuro)."))
        return tickets

    def generate_overdue(self, n: int = 5, seed: int | None = None) -> list[Ticket]:
        rng = random.Random(seed)
        w_main = {i: float(self.delay_main[i] + 1) ** 1.3 for i in range(1, MAIN_MAX + 1)}
        w_sb = {i: float(self.delay_sb[i] + 1) ** 1.3 for i in range(1, SB_MAX + 1)}
        tickets, seen = [], set()
        while len(tickets) < n:
            mains = self._weighted_sample(w_main, PICK, rng)
            sb = self._sb_weighted(w_sb, rng)
            key = (*mains, sb)
            if key in seen:
                continue
            seen.add(key)
            tickets.append(Ticket(mains, sb, "probabilistico-atraso", "Favorece números atrasados (falacia del jugador si se toma como predicción)."))
        return tickets

    def generate_mixed(self, n: int = 5, seed: int | None = None) -> list[Ticket]:
        rng = random.Random(seed)
        by_freq = [n for n, _ in self.ranked_main("freq")]
        by_delay = [n for n, _ in self.ranked_main("delay")]
        hot_pool = by_freq[:14]
        late_pool = [x for x in by_delay[:14] if x not in hot_pool[:8]]
        rest_pool = [x for x in range(1, MAIN_MAX + 1) if x not in set(hot_pool[:8]) | set(late_pool[:8])]
        tickets, seen = [], set()
        attempts = 0
        while len(tickets) < n and attempts < n * 80:
            attempts += 1
            pick = rng.sample(hot_pool, 2) + rng.sample(late_pool, 2) + rng.sample(rest_pool, 1)
            if len(set(pick)) < PICK:
                continue
            mains = sorted(pick)
            s = sum(mains)
            odds = sum(1 for x in mains if x % 2)
            lows = sum(1 for x in mains if x <= 21)
            if not (70 <= s <= 150) or odds in (0, 5) or lows in (0, 5):
                continue
            if rng.random() < 0.5:
                sb = self._sb_weighted({i: float(self.freq_sb[i]) for i in range(1, SB_MAX + 1)}, rng)
            else:
                sb = self._sb_weighted({i: float(self.delay_sb[i] + 1) for i in range(1, SB_MAX + 1)}, rng)
            key = (*mains, sb)
            if key in seen:
                continue
            seen.add(key)
            tickets.append(Ticket(mains, sb, "mixto", f"2 calientes + 2 atrasados + 1 resto · suma={s} · impares={odds} · bajos={lows}"))
        while len(tickets) < n:
            tickets.extend(self.generate_random(1, None if seed is None else seed + len(tickets)))
            tickets[-1].method = "mixto-fallback"
        return tickets[:n]

    def generate(self, mode: str, n: int = 5, seed: int | None = None) -> list[Ticket]:
        mode = mode.lower()
        if mode in {"random", "aleatorio", "rng"}:
            return self.generate_random(n, seed)
        if mode in {"hot", "frecuencia", "calientes", "probabilistico"}:
            return self.generate_hot(n, seed)
        if mode in {"atraso", "overdue", "frios", "delay"}:
            return self.generate_overdue(n, seed)
        if mode in {"mixto", "mixed", "hibrido"}:
            return self.generate_mixed(n, seed)
        if mode in {"all", "todo"}:
            out = []
            out += self.generate_random(max(1, n // 3 + n % 3), seed)
            out += self.generate_hot(max(1, n // 3), None if seed is None else seed + 17)
            out += self.generate_mixed(max(1, n // 3), None if seed is None else seed + 31)
            return out[:n] if n < len(out) else out
        raise ValueError(f"Modo desconocido: {mode}")


def tickets_to_json(tickets: Iterable[Ticket]) -> str:
    return json.dumps([asdict(t) for t in tickets], ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Motor de análisis y recomendaciones Baloto")
    p.add_argument("--data", default=str(DATA_DEFAULT))
    p.add_argument("--mode", default="all")
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--report", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    engine = BalotoEngine(args.data)
    if args.report:
        print(engine.analysis_report())
        print()
    tickets = engine.generate(args.mode, args.n, args.seed)
    if args.json:
        print(tickets_to_json(tickets))
    else:
        snap = engine.snapshot()
        print(f"Baloto · {snap['sorteos']} sorteos · último {snap['ultimo_resultado']['fecha']}")
        print(f"Jackpot teórico: {snap['prob_jackpot']}")
        print("-" * 56)
        for i, t in enumerate(tickets, 1):
            print(f"{i:02d}. {t.pretty()}")
            if t.notes:
                print(f"    {t.notes}")
        print("-" * 56)
        print("Juega legal, define un presupuesto y no persigas pérdidas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
