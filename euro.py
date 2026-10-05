#!/usr/bin/env python3
"""
canvi_monedes_euro.py

Consulta el valor de les monedes del món respecte a l'euro (EUR).

Fa servir l'API pública i gratuïta de Frankfurter (https://frankfurter.dev),
que es basa en els tipus de canvi de referència del Banc Central Europeu (BCE).
No cal cap clau d'API (API key).

Ús:
    python3 canvi_monedes_euro.py                # mostra totes les monedes
    python3 canvi_monedes_euro.py USD GBP JPY     # mostra només aquestes monedes
    python3 canvi_monedes_euro.py --csv fitxer.csv   # guarda el resultat en CSV
    python3 canvi_monedes_euro.py --data 2026-01-15  # tipus de canvi d'una data concreta

Requereix la llibreria "requests":
    pip install requests
"""

import sys
import csv
import argparse
from datetime import date

import requests

API_BASE = "https://api.frankfurter.dev/v1"


def obtenir_taxes(monedes=None, data=None):
    """
    Consulta les taxes de canvi respecte a l'euro (EUR).

    monedes: llista opcional de codis ISO (p.ex. ["USD", "GBP"]).
             Si és None, retorna totes les monedes disponibles.
    data: data en format "YYYY-MM-DD". Si és None, fa servir la data més recent.

    Retorna una tupla (data_efectiva, diccionari {codi_moneda: taxa})
    """
    endpoint = data if data else "latest"
    url = f"{API_BASE}/{endpoint}"
    params = {"base": "EUR"}
    if monedes:
        params["symbols"] = ",".join(m.upper() for m in monedes)

    resposta = requests.get(url, params=params, timeout=10)
    resposta.raise_for_status()
    dades = resposta.json()

    return dades["date"], dades["rates"]


def mostrar_taula(data_efectiva, taxes):
    print(f"\nTipus de canvi respecte a 1 EUR (data: {data_efectiva})\n")
    print(f"{'Moneda':<10}{'Valor':>15}")
    print("-" * 25)
    for codi in sorted(taxes):
        print(f"{codi:<10}{taxes[codi]:>15.4f}")
    print()


def guardar_csv(nom_fitxer, data_efectiva, taxes):
    with open(nom_fitxer, "w", newline="", encoding="utf-8") as f:
        escriptor = csv.writer(f)
        escriptor.writerow(["data", "moneda", "valor_per_1_eur"])
        for codi in sorted(taxes):
            escriptor.writerow([data_efectiva, codi, taxes[codi]])
    print(f"Resultat guardat a: {nom_fitxer}")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta el valor de les monedes del món respecte a l'euro."
    )
    parser.add_argument(
        "monedes",
        nargs="*",
        help="Codis de moneda a consultar (p.ex. USD GBP JPY). Si no se n'indica cap, es mostren totes.",
    )
    parser.add_argument(
        "--data",
        default=None,
        help="Data concreta en format YYYY-MM-DD (per defecte: la més recent disponible).",
    )
    parser.add_argument(
        "--csv",
        default=None,
        help="Nom del fitxer CSV on guardar el resultat (opcional).",
    )
    args = parser.parse_args()

    if args.data:
        try:
            date.fromisoformat(args.data)
        except ValueError:
            print("Error: la data ha de tindre el format YYYY-MM-DD.")
            sys.exit(1)

    try:
        data_efectiva, taxes = obtenir_taxes(args.monedes or None, args.data)
    except requests.exceptions.RequestException as e:
        print(f"Error en connectar amb l'API de tipus de canvi: {e}")
        sys.exit(1)

    if not taxes:
        print("No s'ha trobat cap taxa de canvi per als codis indicats.")
        sys.exit(1)

    mostrar_taula(data_efectiva, taxes)

    if args.csv:
        guardar_csv(args.csv, data_efectiva, taxes)


if __name__ == "__main__":
    main()
