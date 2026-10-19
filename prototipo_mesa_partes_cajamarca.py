#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTOTIPO DE MESA DE PARTES DIGITAL - MUNICIPALIDAD DISTRITAL DE LOS BAÑOS DEL INCA (CAJAMARCA)
Etapa 5: Integración de Persistencia de Datos en Archivos CSV (UTF-8) y Bitácora.
"""

import csv
import os
from datetime import datetime
PROTOTIPO DE MESA DE PARTES DIGITAL - MUNICIPALIDAD DISTRITAL DE LOS BAÑOS DEL INCA (CAJAMARCA)
Etapa 1: Estructura inicial y declaración de arreglos paralelos.
"""

ARCHIVO_DATOS = "expedientes_cajamarca.csv"
ARCHIVO_AUDITORIA = "auditoria_mesa_partes.log"

AREAS_MUNICIPALES = [
    "Subgerencia de Desarrollo Urbano y Rural",
    "Subgerencia de Administración Tributaria (SAT)",
    "Subgerencia de Licencias y Comercialización",
    "Oficina de Registro Civil",
    "Subgerencia de Medio Ambiente y Servicios Públicos",
    "Gerencia Municipal"
]

# Arreglos paralelos (listas unidimensionales sincronizadas por índice i)
codigos = []
dnis = []
ciudadanos = []
asuntos = []
areas = []
folios = []
fechas = []
estados = []


# ==============================================================================
# MÓDULO 2: FUNCIONES DE VALIDACIÓN PRELIMINAR (DNI/RUC, NOMBRE Y FOLIOS)
# ==============================================================================
def validar_dni_o_ruc(documento):
    doc_limpio = documento.strip()
    if not doc_limpio.isdigit():
        return False, "Error: El documento debe contener únicamente dígitos numéricos (0-9)."
    if len(doc_limpio) == 8:
        return True, doc_limpio
    if len(doc_limpio) == 11 and (doc_limpio.startswith("10") or doc_limpio.startswith("20")):
        return True, doc_limpio
    return False, "Error: Ingrese un DNI válido (8 dígitos) o RUC válido (11 dígitos iniciando en 10 o 20)."


def validar_folios(valor_texto):
    limpio = str(valor_texto).strip()
    if not limpio.isdigit():
        return False, 0
    num = int(limpio)
    if 1 <= num <= 500:
        return True, num
    return False, 0


# ==============================================================================
# MÓDULO 4 (PRELIMINAR): ORDENAMIENTO BURBUJA Y BÚSQUEDA BINARIA EN ARREGLOS
# ==============================================================================
def intercambiar_indices(i, j):
    codigos[i], codigos[j] = codigos[j], codigos[i]
    dnis[i], dnis[j] = dnis[j], dnis[i]
    ciudadanos[i], ciudadanos[j] = ciudadanos[j], ciudadanos[i]
    asuntos[i], asuntos[j] = asuntos[j], asuntos[i]
    areas[i], areas[j] = areas[j], areas[i]
    folios[i], folios[j] = folios[j], folios[i]
    fechas[i], fechas[j] = fechas[j], fechas[i]
    estados[i], estados[j] = estados[j], estados[i]


def ordenar_expedientes_por_codigo(ascendente=True):
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


def buscar_por_codigo_binaria(codigo_buscado):
    ordenar_expedientes_por_codigo(ascendente=True)
    objetivo = codigo_buscado.strip().upper()
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


# ==============================================================================
# MÓDULO DE CADENAS DE CARACTERES Y GENERADOR DE CORRELATIVO EXP-2026-XXXX
# ==============================================================================
def normalizar_texto(texto):
    palabras = texto.strip().upper().split()
    return " ".join(palabras)


def validar_nombre_ciudadano(nombre):
    nombre_norm = normalizar_texto(nombre)
    if len(nombre_norm) < 5:
        return False, "Error: El nombre del ciudadano debe tener al menos 5 caracteres."
    return True, nombre_norm


def validar_asunto(asunto):
    asunto_norm = normalizar_texto(asunto).replace(";", ",")
    if len(asunto_norm) < 8:
        return False, "Error: El asunto debe detallar el trámite (mínimo 8 caracteres)."
    return True, asunto_norm


def generar_codigo_expediente(lista_codigos, anio=2026):
    if len(lista_codigos) == 0:
        return f"EXP-{anio}-0001"
    max_correlativo = 0
    for cod in lista_codigos:
        partes = cod.split("-")
        if len(partes) == 3 and partes[2].isdigit():
            corr = int(partes[2])
            if corr > max_correlativo:
                max_correlativo = corr
    return f"EXP-{anio}-{max_correlativo + 1:04d}"


# ==============================================================================
# MÓDULO 3: PERSISTENCIA DE DATOS EN ARCHIVOS CSV (UTF-8)
# ==============================================================================
def guardar_en_archivo(ruta_archivo=ARCHIVO_DATOS):
    try:
        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(["CODIGO", "DNI_RUC", "CIUDADANO", "ASUNTO", "AREA_DESTINO", "FOLIOS", "FECHA_HORA", "ESTADO"])
            for i in range(len(codigos)):
                escritor.writerow([codigos[i], dnis[i], ciudadanos[i], asuntos[i], areas[i], folios[i], fechas[i], estados[i]])
        return True
    except OSError as error:
        print(f"[ERROR] Fallo al guardar el archivo: {error}")
        return False


def cargar_desde_archivo(ruta_archivo=ARCHIVO_DATOS):
    if not os.path.exists(ruta_archivo):
        return 0
    codigos.clear(); dnis.clear(); ciudadanos.clear(); asuntos.clear()
    areas.clear(); folios.clear(); fechas.clear(); estados.clear()
    contador = 0
    with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
        lector = csv.reader(archivo, delimiter=";")
        next(lector, None)
        for fila in lector:
            if len(fila) == 8:
                codigos.append(fila[0]); dnis.append(fila[1]); ciudadanos.append(fila[2])
                asuntos.append(fila[3]); areas.append(fila[4]); folios.append(int(fila[5]))
                fechas.append(fila[6]); estados.append(fila[7])
                contador += 1
    return contador
