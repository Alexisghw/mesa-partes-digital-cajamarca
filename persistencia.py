#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 3: PERSISTENCIA EN BASE DE DATOS SQLITE Y BITÁCORA DE AUDITORÍA
Los ocho arreglos siguen siendo la estructura de trabajo en memoria (ordenar, buscar);
SQLite (módulo sqlite3 de la librería estándar) los guarda de forma permanente.

Reglas de seguridad aplicadas:
  1. Todas las consultas usan parámetros (?) : el texto del usuario nunca se pega dentro
     del SQL, así que una entrada como  '); DROP TABLE expedientes; --  se guarda como
     texto común y no se ejecuta (protección contra inyección SQL).
  2. La tabla tiene restricciones CHECK (DNI/RUC, folios, estado, área, código): aunque
     alguien salte las validaciones de Python, la base rechaza datos inválidos.
  3. Cada escritura es una transacción: o se guarda todo o no se guarda nada.
  4. Al exportar a CSV, los textos que empiezan con = + - @ se neutralizan para que Excel
     no los ejecute como fórmulas (inyección CSV).
"""

import csv
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import List, Tuple

from datos import (ARCHIVO_DATOS, ARCHIVO_AUDITORIA, ARCHIVO_CSV_ORIGEN, ARCHIVO_EXPORTACION,
                   AREAS_MUNICIPALES, ESTADOS_VALIDOS, ARREGLOS,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)
from validacion import (validar_dni_o_ruc, validar_nombre_ciudadano, validar_asunto, validar_folios,
                        validar_estado, validar_codigo_expediente, neutralizar_formula_csv)

_ruta_bd = ARCHIVO_DATOS   # base activa; la simulación de pruebas la cambia temporalmente


def _lista_sql(valores: List[str]) -> str:
    """Convierte una lista de CONSTANTES del programa en  'a', 'b'  para los CHECK del esquema."""
    return ", ".join("'" + v.replace("'", "''") + "'" for v in valores)


ESQUEMA = f"""
CREATE TABLE IF NOT EXISTS expedientes (
    codigo      TEXT PRIMARY KEY
                CHECK (codigo GLOB 'EXP-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    dni_ruc     TEXT NOT NULL
                CHECK (length(dni_ruc) IN (8, 11) AND dni_ruc NOT GLOB '*[^0-9]*'),
    ciudadano   TEXT NOT NULL CHECK (length(ciudadano) BETWEEN 5 AND 120),
    asunto      TEXT NOT NULL CHECK (length(asunto) BETWEEN 8 AND 250),
    area        TEXT NOT NULL CHECK (area IN ({_lista_sql(AREAS_MUNICIPALES)})),
    folios      INTEGER NOT NULL CHECK (folios BETWEEN 1 AND 500),
    fecha_hora  TEXT NOT NULL,
    estado      TEXT NOT NULL CHECK (estado IN ({_lista_sql(ESTADOS_VALIDOS)})),
    orden       INTEGER NOT NULL
)"""

COLUMNAS = "codigo, dni_ruc, ciudadano, asunto, area, folios, fecha_hora, estado, orden"
SQL_INSERTAR = f"INSERT INTO expedientes ({COLUMNAS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"


def usar_base(ruta: str) -> str:
    """Cambia la base de datos activa y devuelve la anterior (lo usa la simulación de pruebas)."""
    global _ruta_bd
    anterior, _ruta_bd = _ruta_bd, ruta
    return anterior


def base_activa() -> str:
    return _ruta_bd


def conectar() -> sqlite3.Connection:
    """Abre la base activa y crea la tabla si todavía no existe."""
    conexion = sqlite3.connect(_ruta_bd)
    conexion.execute(ESQUEMA)
    return conexion


def registrar_auditoria(accion: str, detalle: str) -> None:
    """Registra eventos del sistema en un archivo de texto plano para trazabilidad."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detalle = "".join(c for c in detalle if c.isprintable())   # una entrada no puede partir la bitácora
    try:
        with open(ARCHIVO_AUDITORIA, mode="a", encoding="utf-8") as f_log:
            f_log.write(f"[{marca_tiempo}] [{accion}] {detalle}\n")
    except OSError as e:
        print(f"[ADVERTENCIA] No se pudo escribir en la bitácora: {e}")


def _fila(i: int, orden: int) -> tuple:
    return (codigos[i], dnis[i], ciudadanos[i], asuntos[i], areas[i], folios[i], fechas[i], estados[i], orden)


def insertar_en_bd(i: int) -> Tuple[bool, str]:
    """Inserta el expediente de la posición i de los arreglos (consulta parametrizada)."""
    try:
        with closing(conectar()) as con, con:
            siguiente = con.execute("SELECT COALESCE(MAX(orden), 0) + 1 FROM expedientes").fetchone()[0]
            con.execute(SQL_INSERTAR, _fila(i, siguiente))
        return True, "ok"
    except sqlite3.Error as error:
        return False, f"Error: La base de datos rechazó el registro ({error})."


def actualizar_estado_en_bd(codigo: str, estado: str) -> Tuple[bool, str]:
    """UPDATE parametrizado: el código y el estado viajan como datos, nunca como parte del SQL."""
    try:
        with closing(conectar()) as con, con:
            filas = con.execute("UPDATE expedientes SET estado = ? WHERE codigo = ?", (estado, codigo)).rowcount
        return (filas == 1), ("ok" if filas == 1 else "Error: El expediente no existe en la base de datos.")
    except sqlite3.Error as error:
        return False, f"Error: La base de datos rechazó el cambio ({error})."


def guardar_padron() -> bool:
    """Reescribe la tabla con el contenido y el orden actual de los arreglos, en una sola transacción."""
    try:
        with closing(conectar()) as con, con:
            con.execute("DELETE FROM expedientes")
            con.executemany(SQL_INSERTAR, [_fila(i, i + 1) for i in range(len(codigos))])
        registrar_auditoria("PERSISTENCIA", f"Se guardaron {len(codigos)} expedientes en {_ruta_bd}.")
        return True
    except sqlite3.Error as error:
        print(f"[ERROR CRÍTICO] No se pudo guardar en la base de datos: {error}")
        return False


def validar_fila(fila: List[str]) -> Tuple[bool, tuple]:
    """Valida una fila externa (CSV o base) con las mismas reglas que el registro por teclado."""
    if len(fila) != 8:
        return False, ()
    codigo, dni, nombre, asunto, area, num_folios, fecha, estado = [str(x) for x in fila]
    ok_cod = validar_codigo_expediente(codigo)
    ok_dni, dni = validar_dni_o_ruc(dni)
    ok_nom, nombre = validar_nombre_ciudadano(nombre)
    ok_asu, asunto = validar_asunto(asunto)
    ok_fol, num = validar_folios(num_folios)
    ok_est, estado = validar_estado(estado)
    ok_area = area in AREAS_MUNICIPALES
    if ok_cod and ok_dni and ok_nom and ok_asu and ok_fol and ok_est and ok_area:
        return True, (codigo, dni, nombre, asunto, area, num, fecha.strip(), estado)
    return False, ()


def migrar_csv_a_sqlite(ruta_csv: str = ARCHIVO_CSV_ORIGEN) -> Tuple[int, int]:
    """
    Migración inicial: copia el padrón del CSV del EP a SQLite, validando cada fila.
    Las filas dañadas, inválidas o con código repetido se descartan. Retorna (migradas, descartadas).
    """
    migradas, descartadas = 0, 0
    if not os.path.exists(ruta_csv):
        return 0, 0
    with open(ruta_csv, mode="r", encoding="utf-8", newline="") as archivo, closing(conectar()) as con, con:
        lector = csv.reader(archivo, delimiter=";")
        next(lector, None)
        for fila in lector:
            if not fila:
                continue
            ok, valores = validar_fila(fila)
            if not ok:
                descartadas += 1
                continue
            try:
                con.execute(SQL_INSERTAR, valores + (migradas + 1,))
                migradas += 1
            except sqlite3.IntegrityError:
                descartadas += 1
    registrar_auditoria("MIGRACION", f"{migradas} expedientes migrados de {ruta_csv} a {_ruta_bd}; {descartadas} descartados.")
    return migradas, descartadas


def cargar_padron() -> int:
    """
    Reconstruye los ocho arreglos desde SQLite. Si la base aún no existe y hay un CSV del EP,
    primero hace la migración. Retorna la cantidad de expedientes cargados.
    """
    if not os.path.exists(_ruta_bd) and _ruta_bd == ARCHIVO_DATOS and os.path.exists(ARCHIVO_CSV_ORIGEN):
        migradas, descartadas = migrar_csv_a_sqlite()
        print(f"[MIGRACIÓN] {migradas} expedientes pasaron de {ARCHIVO_CSV_ORIGEN} a {ARCHIVO_DATOS}"
              + (f" ({descartadas} filas inválidas descartadas)." if descartadas else "."))
    for lista in ARREGLOS:
        lista.clear()
    descartadas = 0
    try:
        with closing(conectar()) as con:
            filas = con.execute(f"SELECT {COLUMNAS} FROM expedientes ORDER BY orden").fetchall()
    except sqlite3.Error as error:
        print(f"[ERROR] No se pudo leer la base de datos: {error}")
        return 0
    for fila in filas:
        ok, v = validar_fila(list(fila[:8]))
        if not ok:
            descartadas += 1
            continue
        for lista, valor in zip(ARREGLOS, v):
            lista.append(valor)
    if descartadas:
        print(f"[ADVERTENCIA] Se ignoraron {descartadas} registro(s) inválido(s) de la base de datos.")
    registrar_auditoria("CARGA_INICIAL", f"Se cargaron {len(codigos)} expedientes desde {_ruta_bd}.")
    return len(codigos)


def exportar_csv(ruta: str = ARCHIVO_EXPORTACION) -> bool:
    """Exporta el padrón a CSV (UTF-8 con BOM, ';') para abrirlo en Excel, neutralizando fórmulas."""
    try:
        with open(ruta, mode="w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(["CODIGO", "DNI_RUC", "CIUDADANO", "ASUNTO", "AREA_DESTINO", "FOLIOS", "FECHA_HORA", "ESTADO"])
            for i in range(len(codigos)):
                escritor.writerow([neutralizar_formula_csv(str(x)) for x in _fila(i, 0)[:8]])
        registrar_auditoria("EXPORTACION", f"Se exportaron {len(codigos)} expedientes a {ruta}.")
        return True
    except OSError as error:
        print(f"[ERROR] No se pudo exportar: {error}")
        return False
