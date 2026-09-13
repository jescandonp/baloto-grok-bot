"""Especificaciones de la familia Baloto. Matrices independientes: no mezclar."""

from __future__ import annotations
from dataclasses import dataclass

COLORS = ("amarillo", "azul", "rojo", "verde", "blanco", "negro")

@dataclass(frozen=True)
class GameSpec:
    key: str
    name: str
    kind: str
    main_max: int
    pick: int
    sb_max: int | None
    csv_name: str
    csv_url: str
    draw_days: str
    price_cop: int
    official: str
    notes: str
    jackpot_combos: int

GAMES: dict[str, GameSpec] = {
    "baloto": GameSpec("baloto", "Baloto", "main_plus_sb", 43, 5, 16, "baloto.csv", "https://resultadosloteriascol.com/api/download/baloto.csv", "lunes, miercoles y sabado", 6000, "https://baloto.com/", "Premio mayor: 5 + Superbalota. Revancha es un segundo sorteo con los mismos numeros.", 15401568),
    "revancha": GameSpec("revancha", "Revancha", "main_plus_sb", 43, 5, 16, "revancha.csv", "https://resultadosloteriascol.com/api/download/baloto_revancha.csv", "lunes, miercoles y sabado (mismo dia que Baloto)", 3000, "https://baloto.com/", "No se compra sola: hay que jugar Baloto y pagar $3000 extra. Los numeros del tiquete son los mismos; el sorteo es independiente.", 15401568),
    "miloto": GameSpec("miloto", "MiLoto", "main_only", 39, 5, None, "miloto.csv", "https://resultadosloteriascol.com/api/download/miloto.csv", "lunes, martes, jueves y viernes", 4000, "https://www.baloto.com/miloto/", "5 numeros del 1 al 39, sin Superbalota. Mecanica aparte de Baloto.", 575757),
    "colorloto": GameSpec("colorloto", "ColorLoto", "color_number", 7, 6, None, "colorloto.csv", "https://resultadosloteriascol.com/api/download/colorloto.csv", "lunes y jueves", 5000, "https://baloto.com/colorloto", "6 balotas distintas de un universo de 42 (6 colores x numeros 1-7). Se puede repetir color o numero, nunca el par. Jackpot: 6 pares exactos en cualquier orden.", 5245786),
}

ALIASES = {"baloto": "baloto", "revancha": "revancha", "baloto-revancha": "revancha", "baloto_revancha": "revancha", "miloto": "miloto", "mi-loto": "miloto", "colorloto": "colorloto", "color-loto": "colorloto", "color": "colorloto"}

def resolve_game(name: str) -> GameSpec:
    key = ALIASES.get(name.strip().lower())
    if not key:
        raise ValueError(f"Juego desconocido: {name}. Usa: {', '.join(GAMES)}")
    return GAMES[key]
