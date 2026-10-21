#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 4: OPERACIONES ALGORÍTMICAS (INSERCIÓN, ORDENAMIENTO Y BÚSQUEDA)
"""

from datetime import datetime
from typing import List, Tuple

from datos import (AREAS_MUNICIPALES,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)
from validacion import (normalizar_texto, validar_dni_o_ruc, validar_nombre_ciudadano,
                        validar_asunto, generar_codigo_expediente)
from persistencia import guardar_en_archivo, registrar_auditoria


def insertar_expediente(
    dni_doc: str,
    nombre_ciud: str,
    asunto_tramite: str,
    indice_area: int,
    num_folios: int,
    fecha_manual: str = ""
) -> Tuple[bool, str]:
    """
    Valida las entradas, genera el código único, inserta en los arreglos paralelos
    y sincroniza inmediatamente con el archivo CSV.
    """
    ok_dni, res_dni = validar_dni_o_ruc(dni_doc)
    if not ok_dni:
        return False, res_dni

    ok_nom, res_nom = validar_nombre_ciudadano(nombre_ciud)
    if not ok_nom:
        return False, res_nom

    ok_asu, res_asu = validar_asunto(asunto_tramite)
    if not ok_asu:
        return False, res_asu

    if not (0 <= indice_area < len(AREAS_MUNICIPALES)):
        return False, "Error: El índice de área municipal seleccionada no es válido."

    if not (1 <= num_folios <= 500):
        return False, "Error: El número de folios debe estar entre 1 y 500."

    nuevo_codigo = generar_codigo_expediente(codigos)
    marca_fecha = fecha_manual if fecha_manual else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Inserción sincronizada en arreglos paralelos
    codigos.append(nuevo_codigo)
    dnis.append(res_dni)
    ciudadanos.append(res_nom)
    asuntos.append(res_asu)
    areas.append(AREAS_MUNICIPALES[indice_area])
    folios.append(num_folios)
    fechas.append(marca_fecha)
    estados.append("REGISTRADO")

    guardar_en_archivo()
    registrar_auditoria("REGISTRO", f"Nuevo expediente {nuevo_codigo} - DNI/RUC: {res_dni}")
    return True, nuevo_codigo


def intercambiar_indices(i: int, j: int) -> None:
    """Intercambia los elementos de las posiciones i y j en todos los arreglos paralelos."""
    codigos[i], codigos[j] = codigos[j], codigos[i]
    dnis[i], dnis[j] = dnis[j], dnis[i]
    ciudadanos[i], ciudadanos[j] = ciudadanos[j], ciudadanos[i]
    asuntos[i], asuntos[j] = asuntos[j], asuntos[i]
    areas[i], areas[j] = areas[j], areas[i]
    folios[i], folios[j] = folios[j], folios[i]
    fechas[i], fechas[j] = fechas[j], fechas[i]
    estados[i], estados[j] = estados[j], estados[i]


def ordenar_expedientes_por_codigo(ascendente: bool = True) -> None:
    """
    Algoritmo de Ordenamiento Burbuja Mejorado (con bandera de corte temprano)
    aplicado sobre el arreglo de códigos y sincronizado con los arreglos paralelos.
    Complejidad: O(n^2) en el peor caso, O(n) si ya se encuentra ordenado.
    """
    n = len(codigos)
    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - i - 1):
            condicion = (codigos[j] > codigos[j + 1]) if ascendente else (codigos[j] < codigos[j + 1])
            if condicion:
                intercambiar_indices(j, j + 1)
                hubo_intercambio = True
        if not hubo_intercambio:
            break
    guardar_en_archivo()


def ordenar_expedientes_por_ciudadano() -> None:
    """Ordena alfabéticamente los expedientes por apellido/nombre del ciudadano."""
    n = len(ciudadanos)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if ciudadanos[j] > ciudadanos[j + 1]:
                intercambiar_indices(j, j + 1)


def buscar_por_codigo_binaria(codigo_buscado: str) -> int:
    """
    Implementa el algoritmo de Búsqueda Binaria O(log2 n) sobre el arreglo de códigos.
    Precondición: Se asegura que los arreglos estén ordenados ascendentemente por código.
    Retorna el índice del expediente o -1 si no existe.
    """
    ordenar_expedientes_por_codigo(ascendente=True)
    objetivo = normalizar_texto(codigo_buscado)
    izquierda = 0
    derecha = len(codigos) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if codigos[medio] == objetivo:
            return medio
        elif codigos[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1


def buscar_por_dni_secuencial(dni_buscado: str) -> List[int]:
    """
    Implementa Búsqueda Lineal/Secuencial O(n) para hallar todos los expedientes
    asociados a un mismo DNI o RUC ciudadano.
    """
    objetivo = dni_buscado.strip()
    indices_encontrados: List[int] = []
    for i in range(len(dnis)):
        if dnis[i] == objetivo:
            indices_encontrados.append(i)
    return indices_encontrados


def mostrar_tabla_expedientes(indices: List[int] = None) -> str:
    """Genera una representación tabular formateada de los expedientes."""
    if len(codigos) == 0:
        return "No existen expedientes registrados en el sistema."

    if indices is None:
        indices = list(range(len(codigos)))

    lineas = []
    separador = "-" * 116
    lineas.append(separador)
    lineas.append(
        f"{'CÓDIGO':<14} | {'DNI/RUC':<11} | {'CIUDADANO / ADMINISTRADO':<28} | "
        f"{'ASUNTO DEL TRÁMITE':<30} | {'FOLIOS':<6} | {'ESTADO':<13}"
    )
    lineas.append(separador)
    for idx in indices:
        ciud_corto = ciudadanos[idx][:27]
        asunto_corto = asuntos[idx][:29]
        lineas.append(
            f"{codigos[idx]:<14} | {dnis[idx]:<11} | {ciud_corto:<28} | "
            f"{asunto_corto:<30} | {folios[idx]:>6} | {estados[idx]:<13}"
        )
    lineas.append(separador)
    lineas.append(f"Total de registros listados: {len(indices)}")
    return "\n".join(lineas)
