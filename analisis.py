#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 8: ANÁLISIS EXPERIMENTAL DE ALGORITMOS (BURBUJA MEJORADO VS. SELECCIÓN)
Mide comparaciones e intercambios ejecutando las MISMAS funciones del Módulo 4 sobre
padrones de prueba de distinto tamaño y orden. El padrón real se respalda antes y se
restaura al final, sin tocar el archivo CSV (se ordena con guardar=False).
"""

import random
from typing import Dict, List

from datos import ARREGLOS, codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados
from algoritmos import ordenar_expedientes_por_codigo, ordenar_expedientes_por_codigo_seleccion

TAMANIOS = [6, 100, 500]
SEMILLA = 2026   # semilla fija: la prueba "aleatoria" da los mismos números en cada ejecución


def _cargar_padron_de_prueba(lista_codigos: List[str]) -> None:
    """Llena los 8 arreglos con expedientes ficticios en el orden de lista_codigos."""
    for lista in ARREGLOS:
        lista.clear()
    for cod in lista_codigos:
        codigos.append(cod)
        dnis.append("00000000")
        ciudadanos.append("PRUEBA")
        asuntos.append("PRUEBA DE RENDIMIENTO")
        areas.append("Gerencia Municipal")
        folios.append(1)
        fechas.append("2026-01-01 00:00:00")
        estados.append("REGISTRADO")


def _medir(ordenar, lista_codigos: List[str]) -> Dict[str, int]:
    """Ejecuta un ordenamiento sobre una copia del padrón de prueba y devuelve sus contadores."""
    _cargar_padron_de_prueba(lista_codigos)
    contador = {"comparaciones": 0, "intercambios": 0}
    ordenar(guardar=False, contador=contador)
    if codigos != sorted(lista_codigos):
        raise AssertionError("El ordenamiento no dejó los códigos en orden ascendente.")
    return contador


def comparar_burbuja_vs_seleccion() -> List[Dict]:
    """
    Imprime y retorna la tabla comparativa para n = 6, 100 y 500 con padrones
    ya ordenados, en orden inverso y aleatorios.
    """
    respaldo = [lista.copy() for lista in ARREGLOS]
    filas: List[Dict] = []
    generador = random.Random(SEMILLA)
    try:
        for n in TAMANIOS:
            ordenada = [f"EXP-2026-{k:04d}" for k in range(1, n + 1)]
            aleatoria = ordenada.copy()
            generador.shuffle(aleatoria)
            casos = [("ordenado", ordenada), ("inverso", ordenada[::-1]), ("aleatorio", aleatoria)]
            for nombre_caso, lista in casos:
                burbuja = _medir(ordenar_expedientes_por_codigo, lista)
                seleccion = _medir(ordenar_expedientes_por_codigo_seleccion, lista)
                filas.append({"n": n, "caso": nombre_caso,
                              "burbuja_comp": burbuja["comparaciones"],
                              "burbuja_inter": burbuja["intercambios"],
                              "seleccion_comp": seleccion["comparaciones"],
                              "seleccion_inter": seleccion["intercambios"],
                              "teorico": n * (n - 1) // 2})
    finally:
        for lista, copia in zip(ARREGLOS, respaldo):
            lista.clear()
            lista.extend(copia)

    print("\nBURBUJA MEJORADO VS. SELECCIÓN (conteo real de operaciones)")
    print("-" * 92)
    print(f"{'n':>4} | {'PADRÓN':<9} | {'BURBUJA COMP.':>13} | {'BURBUJA INTERC.':>15} | "
          f"{'SELECC. COMP.':>13} | {'SELECC. INTERC.':>15} | {'n(n-1)/2':>8}")
    print("-" * 92)
    for f in filas:
        print(f"{f['n']:>4} | {f['caso']:<9} | {f['burbuja_comp']:>13} | {f['burbuja_inter']:>15} | "
              f"{f['seleccion_comp']:>13} | {f['seleccion_inter']:>15} | {f['teorico']:>8}")
    print("-" * 92)
    print("Lectura: Burbuja Mejorado gana si el padrón ya está ordenado (n-1 comparaciones, el caso\n"
          "habitual porque los códigos se generan en orden); Selección hace muchos menos intercambios\n"
          "cuando el padrón está desordenado, y cada intercambio mueve los 8 arreglos paralelos.")
    return filas
