#!/usr/bin/env python3
"""Descarga indicadores oficiales del Banco de México (API SIE) y los guarda versionados.

Escribe un CSV por serie en docs/data/ y un resumen en docs/datos.json para la página.
La primera vez descarga el histórico completo desde FECHA_INICIO; después solo los
últimos días y los mezcla con lo que ya había, así que correrlo dos veces el mismo
día no cambia nada.

Requiere la variable de entorno BANXICO_TOKEN (token gratuito del SIE).
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "docs" / "data"
SALIDA_PAGINA = RAIZ / "docs" / "datos.json"

API = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
FECHA_INICIO = date(2024, 1, 1)
DIAS_REFRESCO = 60  # Banxico a veces corrige datos recientes; se vuelven a pedir.

# Las primeras seis son las mismas de mcp-banxico (mcp_banxico/constants.py); el resto
# se consulta igual que con su herramienta consultar_serie_sie. Todos los IDs se
# verificaron contra el catálogo del SIE el 2026-10-08.
SERIES = [
    # Tipo de cambio
    {"clave": "tipo_cambio_fix", "id": "SF43718", "nombre": "Tipo de cambio FIX",
     "unidad": "pesos por dólar", "frecuencia": "diaria", "decimales": 4},
    {"clave": "tipo_cambio_liquidacion", "id": "SF60653", "nombre": "Tipo de cambio de liquidación (DOF)",
     "unidad": "pesos por dólar", "frecuencia": "diaria", "decimales": 4},
    {"clave": "euro", "id": "SF46410", "nombre": "Euro",
     "unidad": "pesos por euro", "frecuencia": "diaria", "decimales": 4},
    {"clave": "libra", "id": "SF46407", "nombre": "Libra esterlina",
     "unidad": "pesos por libra", "frecuencia": "diaria", "decimales": 4},
    {"clave": "yen", "id": "SF46406", "nombre": "Yen japonés",
     "unidad": "pesos por yen", "frecuencia": "diaria", "decimales": 4},
    {"clave": "dolar_canadiense", "id": "SF60632", "nombre": "Dólar canadiense",
     "unidad": "pesos por dólar canadiense", "frecuencia": "diaria", "decimales": 4},
    # Inflación (INPC)
    {"clave": "inflacion_anual", "id": "SP30578", "nombre": "Inflación anual (INPC)",
     "unidad": "%", "frecuencia": "mensual", "decimales": 2},
    {"clave": "inflacion_mensual", "id": "SP30577", "nombre": "Inflación mensual (INPC)",
     "unidad": "%", "frecuencia": "mensual", "decimales": 2},
    {"clave": "inflacion_subyacente", "id": "SP74662", "nombre": "Inflación subyacente anual",
     "unidad": "%", "frecuencia": "mensual", "decimales": 2},
    {"clave": "inflacion_no_subyacente", "id": "SP74665", "nombre": "Inflación no subyacente anual",
     "unidad": "%", "frecuencia": "mensual", "decimales": 2},
    {"clave": "inpc", "id": "SP1", "nombre": "Índice Nacional de Precios al Consumidor",
     "unidad": "índice", "frecuencia": "mensual", "decimales": 3},
    {"clave": "udis", "id": "SP68257", "nombre": "Valor de la UDI",
     "unidad": "pesos por UDI", "frecuencia": "diaria", "decimales": 6},
    # Tasas de interés
    {"clave": "tasa_objetivo", "id": "SF61745", "nombre": "Tasa objetivo",
     "unidad": "%", "frecuencia": "diaria", "decimales": 2},
    {"clave": "tiie_fondeo", "id": "SF331451", "nombre": "TIIE de fondeo a un día",
     "unidad": "%", "frecuencia": "diaria", "decimales": 2},
    {"clave": "tiie_28", "id": "SF43783", "nombre": "TIIE 28 días",
     "unidad": "%", "frecuencia": "diaria", "decimales": 4},
    {"clave": "tiie_91", "id": "SF43878", "nombre": "TIIE 91 días",
     "unidad": "%", "frecuencia": "diaria", "decimales": 4},
    {"clave": "tiie_182", "id": "SF111916", "nombre": "TIIE 182 días",
     "unidad": "%", "frecuencia": "diaria", "decimales": 4},
    {"clave": "cetes_28", "id": "SF43936", "nombre": "CETES 28 días",
     "unidad": "%", "frecuencia": "semanal", "decimales": 2},
    {"clave": "cetes_91", "id": "SF43939", "nombre": "CETES 91 días",
     "unidad": "%", "frecuencia": "semanal", "decimales": 2},
    {"clave": "cetes_182", "id": "SF43942", "nombre": "CETES 182 días",
     "unidad": "%", "frecuencia": "semanal", "decimales": 2},
    {"clave": "cetes_364", "id": "SF43945", "nombre": "CETES 364 días",
     "unidad": "%", "frecuencia": "semanal", "decimales": 2},
    # Reservas
    {"clave": "reservas", "id": "SF43707", "nombre": "Reservas internacionales",
     "unidad": "millones de dólares", "frecuencia": "semanal", "decimales": 1},
]


def pedir(id_serie: str, desde: date, hasta: date, token: str) -> list[tuple[str, float]]:
    url = f"{API}/{id_serie}/datos/{desde.isoformat()}/{hasta.isoformat()}"
    req = urllib.request.Request(url, headers={"Bmx-Token": token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        cuerpo = json.load(resp)
    datos = cuerpo["bmx"]["series"][0].get("datos") or []
    filas = []
    for d in datos:
        valor = d["dato"].replace(",", "")
        if valor in ("N/E", ""):
            continue
        fecha = datetime.strptime(d["fecha"], "%d/%m/%Y").date().isoformat()
        filas.append((fecha, float(valor)))
    return filas


def leer_csv(ruta: Path) -> dict[str, float]:
    if not ruta.exists():
        return {}
    with ruta.open(newline="") as f:
        return {fila["fecha"]: float(fila["valor"]) for fila in csv.DictReader(f)}


def escribir_csv(ruta: Path, valores: dict[str, float], decimales: int) -> None:
    with ruta.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["fecha", "valor"])
        for fecha in sorted(valores):
            w.writerow([fecha, f"{valores[fecha]:.{decimales}f}"])


def main() -> int:
    token = os.environ.get("BANXICO_TOKEN", "").strip()
    if not token:
        print("Falta BANXICO_TOKEN", file=sys.stderr)
        return 1

    DIR_DATOS.mkdir(exist_ok=True)
    hoy = date.today()
    resumen = {"actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "fuente": "Banco de México, Sistema de Información Económica (SIE)",
               "series": {}}

    for s in SERIES:
        ruta = DIR_DATOS / f"{s['clave']}.csv"
        existentes = leer_csv(ruta)
        desde = FECHA_INICIO if not existentes else hoy - timedelta(days=DIAS_REFRESCO)
        nuevos = pedir(s["id"], desde, hoy, token)
        antes = len(existentes)
        existentes.update(dict(nuevos))
        escribir_csv(ruta, existentes, s["decimales"])
        print(f"{s['clave']:16} {s['id']:8} {len(existentes):5} datos (+{len(existentes) - antes})")

        puntos = sorted(existentes.items())
        resumen["series"][s["clave"]] = {
            "id": s["id"], "nombre": s["nombre"], "unidad": s["unidad"],
            "frecuencia": s["frecuencia"], "decimales": s["decimales"],
            "datos": [[f, v] for f, v in puntos],
        }

    # Solo se reescribe si cambió algún dato: así un día sin publicaciones
    # (fin de semana, feriado) no genera un commit vacío por la fecha.
    if SALIDA_PAGINA.exists():
        previo = json.loads(SALIDA_PAGINA.read_text())
        if previo.get("series") == resumen["series"]:
            print("sin datos nuevos; datos.json no cambia")
            return 0
    SALIDA_PAGINA.parent.mkdir(exist_ok=True)
    SALIDA_PAGINA.write_text(json.dumps(resumen, ensure_ascii=False, separators=(",", ":")))
    print(f"página: {SALIDA_PAGINA.relative_to(RAIZ)} ({SALIDA_PAGINA.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
