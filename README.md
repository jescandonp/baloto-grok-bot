# Baloto Analyst — motor + Grok Bot

Especialista para [Baloto Colombia](https://baloto.com/). Combina el alcance real de un juego de suerte y azar con analítica descriptiva del histórico: frecuencias, atrasos, pares y generadores de jugadas **aleatorias**, **ponderadas** y **mixtas**.

> Cada combinación 5/43 + Superbalota 1/16 tiene la **misma** probabilidad teórica: **1 en 15.401.568**.  
> Este proyecto no predice el sorteo. Ordena información para jugar con los ojos abiertos.

## Qué incluye

| Pieza | Para qué |
|---|---|
| `docs/GROK_BOT_PROFILE.md` | Perfil listo para pegar en Grok Bot (nombre, job, reglas, primera tarea, rutinas) |
| `src/baloto_engine.py` | Motor Python: informe + 4 modos de generación |
| `data/baloto.csv` | Histórico 2021-05-01 → 2026-09-12 (628 sorteos, formato actual 5/43+1/16) |
| `docs/ALCANCE.md` | Suerte vs datos, plan de premios, juego responsable |

Fuente del CSV: [resultadosloteriascol.com](https://resultadosloteriascol.com/api/download/baloto.csv) (CC BY 4.0 — citar). Verificar siempre contra [baloto.com/resultados](https://baloto.com/resultados).

## Cómo jugar Baloto (resumen)

1. Elige **5 números del 1 al 43** sin repetir.
2. Elige **1 Superbalota del 1 al 16**.
3. Opcional: **Revancha** (+$3.000) con los mismos números, premio aparte.
4. Sorteos **lunes, miércoles y sábado**.
5. Precio de referencia Baloto: **$6.000**. Prohibida la venta a menores.

## Uso del motor

```bash
python -m pip install -r requirements.txt
curl -sL https://resultadosloteriascol.com/api/download/baloto.csv -o data/baloto.csv
python src/baloto_engine.py --report
python src/baloto_engine.py --mode aleatorio --n 5
python src/baloto_engine.py --mode frecuencia --n 5
python src/baloto_engine.py --mode atraso --n 5
python src/baloto_engine.py --mode mixto --n 5
python src/baloto_engine.py --mode all --n 6 --json
```

## Cómo crear el Grok Bot

1. Abre la app [Grok Bot](https://docs.x.ai/grok-bot/get-started) y **Create your own**.
2. Pega el contenido de `docs/GROK_BOT_PROFILE.md`.
3. Deja este repo (o la carpeta) al alcance del Bot y dale la primera tarea del mismo documento.
4. Opcional: rutina post-sorteo a las 22:30 COT lun/mié/sáb.

## Modelos de recomendación

- **Aleatorio:** uniforme. Equivale a la jugada automática oficial. Es el único modo matemáticamente “honesto” respecto al sorteo.
- **Probabilístico-frecuencia:** muestreo ponderado por cuántas veces salió cada número en el histórico.
- **Probabilístico-atraso:** favorece números que llevan más sorteos sin aparecer.
- **Mixto:** 2 calientes + 2 atrasados + 1 del resto, con filtros de suma (70–150), no 0/5 impares y no 0/5 bajos.

Los tres últimos son **heurísticas**. Si alguien te dice que “rompen” el 1/15.401.568, está mintiendo.

## Juego responsable

Define un tope semanal antes de comprar. No recuperes pérdidas subiendo la apuesta. Premios: 1 año para reclamar. Usa los límites de baloto.com. 18+.
