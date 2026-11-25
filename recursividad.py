#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 7: RECURSIVIDAD (SESIONES 7.1 A 7.4)
Toda función recursiva de este módulo tiene:
    - caso base: la situación que se resuelve sin volver a llamarse;
    - caso recursivo: la llamada a sí misma con un problema más pequeño;
    - condición de parada: garantiza que cada llamada se acerca al caso base.
"""

import math
from typing import List, Optional

from datos import codigos, folios, estados, ESTADOS_VALIDOS
from validacion import normalizar_texto
from algoritmos import ordenar_expedientes_por_codigo, busqueda_binaria_iterativa


def busqueda_binaria_recursiva(lista: List[str], objetivo: str, izquierda: int, derecha: int,
                               contador: Optional[List[int]] = None) -> int:
    """
    Búsqueda binaria recursiva sobre una lista ordenada ascendentemente.
    Caso base 1: izquierda > derecha  -> el tramo está vacío, el objetivo no existe (-1).
    Caso base 2: lista[medio] == objetivo -> se encontró, se retorna medio.
    Caso recursivo: se busca solo en la mitad donde puede estar el objetivo.
    Parada: cada llamada descarta al menos la mitad del tramo, así que llega al caso base
    en a lo más ⌈log2(n+1)⌉ llamadas.
    'contador' (opcional) acumula cuántas posiciones se revisaron, para comparar con la iterativa.
    """
    if izquierda > derecha:
        return -1
    medio = (izquierda + derecha) // 2
    if contador is not None:
        contador[0] += 1
    if lista[medio] == objetivo:
        return medio
    if lista[medio] < objetivo:
        return busqueda_binaria_recursiva(lista, objetivo, medio + 1, derecha, contador)
    return busqueda_binaria_recursiva(lista, objetivo, izquierda, medio - 1, contador)


def buscar_por_codigo_recursiva(codigo_buscado: str) -> int:
    """Ordena el padrón por código (solo en memoria) y aplica la búsqueda binaria recursiva."""
    ordenar_expedientes_por_codigo(ascendente=True, guardar=False)
    return busqueda_binaria_recursiva(codigos, normalizar_texto(codigo_buscado), 0, len(codigos) - 1)


def sumar_folios_recursivo(lista: List[int], izquierda: int, derecha: int) -> int:
    """
    Suma los folios del tramo [izquierda, derecha] partiendo el arreglo en dos mitades
    (divide y vencerás).
    Caso base 1: tramo vacío -> 0.   Caso base 2: un solo elemento -> ese elemento.
    Caso recursivo: suma(mitad izquierda) + suma(mitad derecha).
    Se eligió partir en mitades y no 'primer elemento + resto' porque la profundidad de
    llamadas es ⌈log2 n⌉ y no n: con 1000 expedientes la versión lineal supera el límite
    de recursión de Python (RecursionError) y esta usa unas 10 llamadas anidadas.
    """
    if izquierda > derecha:
        return 0
    if izquierda == derecha:
        return lista[izquierda]
    medio = (izquierda + derecha) // 2
    return (sumar_folios_recursivo(lista, izquierda, medio)
            + sumar_folios_recursivo(lista, medio + 1, derecha))


def contar_por_estado_recursivo(lista: List[str], estado: str, izquierda: int, derecha: int) -> int:
    """
    Cuenta cuántos expedientes del tramo [izquierda, derecha] tienen el estado indicado.
    Mismos casos base y recursivo que sumar_folios_recursivo.
    """
    if izquierda > derecha:
        return 0
    if izquierda == derecha:
        return 1 if lista[izquierda] == estado else 0
    medio = (izquierda + derecha) // 2
    return (contar_por_estado_recursivo(lista, estado, izquierda, medio)
            + contar_por_estado_recursivo(lista, estado, medio + 1, derecha))


def reporte_recursivo() -> str:
    """Resumen del padrón calculado con las funciones recursivas: folios totales y expedientes por estado."""
    n = len(codigos)
    if n == 0:
        return "No existen expedientes registrados en el sistema."
    lineas = ["-" * 50,
              f"{'Expedientes registrados':<35}{n:>10}",
              f"{'Folios recibidos (suma recursiva)':<35}{sumar_folios_recursivo(folios, 0, n - 1):>10}",
              "-" * 50]
    for estado in ESTADOS_VALIDOS:
        lineas.append(f"  {estado:<33}{contar_por_estado_recursivo(estados, estado, 0, n - 1):>10}")
    lineas.append("-" * 50)
    return "\n".join(lineas)


def comparar_iterativa_vs_recursiva() -> bool:
    """
    Tabla de equivalencia (sesión 7.4): busca cada código del padrón y dos códigos
    inexistentes con ambas versiones y compara posición devuelta y posiciones revisadas.
    Retorna True si las dos versiones coinciden en todos los casos.
    """
    ordenar_expedientes_por_codigo(ascendente=True, guardar=False)
    lista = list(codigos)
    n = len(lista)
    maximo = math.ceil(math.log2(n + 1)) if n > 0 else 0
    consultas = lista + ["EXP-0000-0000", "EXP-9999-9999"]   # menor y mayor que todos

    print(f"\nTABLA DE EQUIVALENCIA — n = {n} expedientes, máximo teórico ⌈log2(n+1)⌉ = {maximo} revisiones")
    print("-" * 78)
    print(f"{'CÓDIGO BUSCADO':<16}| {'POS. ITER.':>10} | {'POS. REC.':>9} | {'REVIS. ITER.':>12} | {'REVIS. REC.':>11} | OK")
    print("-" * 78)
    todos_iguales = True
    for objetivo in consultas:
        c_it, c_rec = [0], [0]
        pos_it = busqueda_binaria_iterativa(lista, objetivo, c_it)
        pos_rec = busqueda_binaria_recursiva(lista, objetivo, 0, n - 1, c_rec)
        iguales = pos_it == pos_rec and c_it[0] == c_rec[0] and c_it[0] <= maximo
        todos_iguales = todos_iguales and iguales
        print(f"{objetivo:<16}| {pos_it:>10} | {pos_rec:>9} | {c_it[0]:>12} | {c_rec[0]:>11} | {'Sí' if iguales else 'NO'}")
    print("-" * 78)
    print("Resultado: ambas versiones son equivalentes." if todos_iguales
          else "Resultado: se encontraron diferencias entre las versiones.")
    return todos_iguales
