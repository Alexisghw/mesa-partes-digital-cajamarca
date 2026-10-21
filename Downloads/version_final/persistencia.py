#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 3: PERSISTENCIA DE DATOS EN ARCHIVOS (CSV Y BITÁCORA DE AUDITORÍA)
"""

import csv
import os
from datetime import datetime

from datos import (ARCHIVO_DATOS, ARCHIVO_AUDITORIA,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)


def registrar_auditoria(accion: str, detalle: str) -> None:
    """Registra eventos del sistema en un archivo de texto plano para trazabilidad."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca_tiempo}] [{accion}] {detalle}\n"
    try:
        with open(ARCHIVO_AUDITORIA, mode="a", encoding="utf-8") as f_log:
            f_log.write(linea)
    except OSError as e:
        print(f"[ADVERTENCIA] No se pudo escribir en la bitácora: {e}")


def guardar_en_archivo(ruta_archivo: str = ARCHIVO_DATOS) -> bool:
    """
    Almacena de forma permanente todos los arreglos paralelos en un archivo CSV
    codificado en UTF-8 con delimitador punto y coma (;).
    """
    try:
        with open(ruta_archivo, mode="w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow([
                "CODIGO", "DNI_RUC", "CIUDADANO", "ASUNTO",
                "AREA_DESTINO", "FOLIOS", "FECHA_HORA", "ESTADO"
            ])
            for i in range(len(codigos)):
                escritor.writerow([
                    codigos[i], dnis[i], ciudadanos[i], asuntos[i],
                    areas[i], folios[i], fechas[i], estados[i]
                ])
        registrar_auditoria("PERSISTENCIA", f"Se guardaron {len(codigos)} expedientes en {ruta_archivo}.")
        return True
    except OSError as error:
        print(f"[ERROR CRÍTICO] Fallo al guardar el archivo: {error}")
        return False


def cargar_desde_archivo(ruta_archivo: str = ARCHIVO_DATOS) -> int:
    """
    Lee el archivo CSV al iniciar el programa y reconstruye los arreglos paralelos.
    Retorna la cantidad de registros cargados.
    """
    if not os.path.exists(ruta_archivo):
        return 0

    codigos.clear()
    dnis.clear()
    ciudadanos.clear()
    asuntos.clear()
    areas.clear()
    folios.clear()
    fechas.clear()
    estados.clear()

    contador = 0
    descartadas = 0  # Filas dañadas (cantidad de campos distinta de 8)
    try:
        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            lector = csv.reader(archivo, delimiter=";")
            next(lector, None)  # Omitir cabecera
            for fila in lector:
                if len(fila) == 8:
                    codigos.append(fila[0])
                    dnis.append(fila[1])
                    ciudadanos.append(fila[2])
                    asuntos.append(fila[3])
                    areas.append(fila[4])
                    folios.append(int(fila[5]) if fila[5].isdigit() else 1)
                    fechas.append(fila[6])
                    estados.append(fila[7])
                    contador += 1
                elif len(fila) > 0:
                    descartadas += 1
        if descartadas > 0:
            print(f"[ADVERTENCIA] Se ignoraron {descartadas} línea(s) dañada(s) del archivo {ruta_archivo}.")
        registrar_auditoria("CARGA_INICIAL", f"Se cargaron {contador} expedientes desde {ruta_archivo}.")
    except OSError as error:
        print(f"[ERROR] No se pudo leer el archivo de datos: {error}")
    return contador
