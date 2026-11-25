#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 4: OPERACIONES ALGORÍTMICAS (INSERCIÓN, ACTUALIZACIÓN, ORDENAMIENTO Y BÚSQUEDA)
Los ordenamientos aceptan un diccionario 'contador' opcional donde suman comparaciones
e intercambios; así el Módulo 8 compara Burbuja y Selección usando estas mismas funciones.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from datos import (AREAS_MUNICIPALES,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)
from validacion import (normalizar_texto, clave_orden_alfabetico, validar_dni_o_ruc,
                        validar_nombre_ciudadano, validar_asunto, validar_folios,
                        validar_indice_area, validar_estado, generar_codigo_expediente)
from persistencia import guardar_padron, insertar_en_bd, actualizar_estado_en_bd, registrar_auditoria
from datos import ARREGLOS


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
    y lo guarda de inmediato en SQLite con un INSERT parametrizado. Si la base lo
    rechaza (restricciones CHECK), se deshace la inserción en los arreglos.
    indice_area es el índice interno 0-5 (el menú convierte la opción 1-6 con validar_opcion_area).
    Todas las reglas se consultan en validacion.py, para no repetirlas aquí (principio DRY).
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

    if not validar_indice_area(indice_area):
        return False, "Error: El área municipal seleccionada no es válida (opciones 1 a 6)."

    ok_fol, num_folios = validar_folios(str(num_folios))
    if not ok_fol:
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

    ok_bd, msg_bd = insertar_en_bd(len(codigos) - 1)
    if not ok_bd:
        for lista in ARREGLOS:      # la memoria y la base siempre coinciden
            lista.pop()
        return False, msg_bd
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


def ordenar_expedientes_por_codigo(ascendente: bool = True, guardar: bool = True,
                                   contador: Optional[Dict[str, int]] = None) -> None:
    """
    Algoritmo de Ordenamiento Burbuja Mejorado (con bandera de corte temprano)
    aplicado sobre el arreglo de códigos y sincronizado con los arreglos paralelos.
    Complejidad: O(n^2) en el peor caso, O(n) si ya se encuentra ordenado.
    El parámetro 'guardar' permite ordenar solo en memoria (lo usa la búsqueda binaria).
    """
    n = len(codigos)
    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - i - 1):
            condicion = (codigos[j] > codigos[j + 1]) if ascendente else (codigos[j] < codigos[j + 1])
            if contador is not None:
                contador["comparaciones"] += 1
            if condicion:
                intercambiar_indices(j, j + 1)
                hubo_intercambio = True
                if contador is not None:
                    contador["intercambios"] += 1
        if not hubo_intercambio:
            break
    if guardar:
        guardar_padron()


def ordenar_expedientes_por_ciudadano() -> None:
    """
    Ordena alfabéticamente (A-Z) los expedientes por apellido/nombre del ciudadano
    con el mismo Burbuja Mejorado (bandera de corte temprano) y guarda el nuevo orden.
    Compara con clave_orden_alfabetico para que 'ÁLVAREZ' quede con la A y 'ÑONTOL'
    después de la N, como en un directorio en español.
    """
    n = len(ciudadanos)
    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - i - 1):
            if clave_orden_alfabetico(ciudadanos[j]) > clave_orden_alfabetico(ciudadanos[j + 1]):
                intercambiar_indices(j, j + 1)
                hubo_intercambio = True
        if not hubo_intercambio:
            break
    guardar_padron()


def busqueda_binaria_iterativa(lista: List[str], objetivo: str,
                               contador: Optional[List[int]] = None) -> int:
    """
    Búsqueda Binaria iterativa O(log2 n) sobre una lista ordenada ascendentemente.
    Retorna la posición del objetivo o -1. 'contador' (opcional) acumula cuántas
    posiciones se revisaron; lo usa la comparación con la versión recursiva (Módulo 7).
    """
    izquierda, derecha = 0, len(lista) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if contador is not None:
            contador[0] += 1
        if lista[medio] == objetivo:
            return medio
        if lista[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1


def buscar_por_codigo_binaria(codigo_buscado: str) -> int:
    """
    Busca un expediente por código con la Búsqueda Binaria iterativa O(log2 n).
    Precondición: Se asegura que los arreglos estén ordenados ascendentemente por código
    (si ya lo están, la burbuja mejorada hace una sola pasada O(n)); se ordena solo en
    memoria para no reescribir el archivo en cada consulta.
    Retorna el índice del expediente o -1 si no existe.
    """
    ordenar_expedientes_por_codigo(ascendente=True, guardar=False)
    return busqueda_binaria_iterativa(codigos, normalizar_texto(codigo_buscado))


def ordenar_expedientes_por_codigo_seleccion(guardar: bool = True,
                                             contador: Optional[Dict[str, int]] = None) -> None:
    """
    Ordenamiento por Selección (ascendente por código), alternativa comparada con Burbuja.
    En cada pasada i busca el menor código entre i y n-1 y lo lleva a la posición i
    con un solo intercambio sincronizado de los 8 arreglos.
    Comparaciones: siempre n(n-1)/2, aunque el padrón ya esté ordenado.
    Intercambios: a lo más n-1 (Burbuja puede hacer hasta n(n-1)/2).
    """
    n = len(codigos)
    for i in range(n - 1):
        pos_menor = i
        for j in range(i + 1, n):
            if contador is not None:
                contador["comparaciones"] += 1
            if codigos[j] < codigos[pos_menor]:
                pos_menor = j
        if pos_menor != i:
            intercambiar_indices(i, pos_menor)
            if contador is not None:
                contador["intercambios"] += 1
    if guardar:
        guardar_padron()


def actualizar_estado_expediente(codigo_buscado: str, estado_nuevo: str) -> Tuple[bool, str]:
    """
    Cambia el estado de un expediente (REGISTRADO -> EN EVALUACIÓN -> OBSERVADO / ATENDIDO).
    Pasos: valida el estado, ubica el expediente con la búsqueda binaria, aplica las reglas
    y guarda el cambio en SQLite (UPDATE parametrizado) y en la bitácora. Reglas: un expediente ATENDIDO ya no se modifica y no se
    acepta "cambiar" al mismo estado que ya tiene.
    """
    ok_est, estado_oficial = validar_estado(estado_nuevo)
    if not ok_est:
        return False, estado_oficial
    pos = buscar_por_codigo_binaria(codigo_buscado)
    if pos == -1:
        return False, f"Error: No existe el expediente '{normalizar_texto(codigo_buscado)}'."
    estado_anterior = estados[pos]
    if estado_anterior == "ATENDIDO":
        return False, f"Error: {codigos[pos]} ya fue ATENDIDO; su estado no puede cambiar."
    if estado_anterior == estado_oficial:
        return False, f"Error: {codigos[pos]} ya se encuentra en estado {estado_oficial}."
    estados[pos] = estado_oficial
    ok_bd, msg_bd = actualizar_estado_en_bd(codigos[pos], estado_oficial)
    if not ok_bd:
        estados[pos] = estado_anterior
        return False, msg_bd
    registrar_auditoria("ESTADO", f"{codigos[pos]}: {estado_anterior} -> {estado_oficial}")
    return True, f"{codigos[pos]}: {estado_anterior} -> {estado_oficial}"


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
