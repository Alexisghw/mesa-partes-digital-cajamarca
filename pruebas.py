#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 5: SIMULACIÓN DE PRUEBAS AUTOMÁTICAS CON DATOS DE CAMPO (CAJAMARCA)
"""

import os
import sqlite3
from contextlib import closing

from datos import ARCHIVO_DATOS, ARCHIVO_PRUEBAS, ARREGLOS, codigos, ciudadanos, areas, fechas
from validacion import normalizar_texto
from persistencia import cargar_padron, usar_base, conectar
from algoritmos import (insertar_expediente, ordenar_expedientes_por_ciudadano,
                        buscar_por_codigo_binaria, mostrar_tabla_expedientes,
                        actualizar_estado_expediente)


def ejecutar_simulacion_cajamarca() -> None:
    """
    Carga los datos recogidos en la práctica de campo en la Municipalidad Distrital
    de Los Baños del Inca (Cajamarca) y ejecuta las pruebas de validación, ordenamiento,
    búsqueda, persistencia, estados y seguridad.
    Las pruebas corren en una base SQLite aparte (ARCHIVO_PRUEBAS): la base real nunca se
    abre. Al terminar se restauran los arreglos del padrón real.
    """
    respaldo_arreglos = [lista.copy() for lista in ARREGLOS]
    for lista in ARREGLOS:
        lista.clear()
    if os.path.exists(ARCHIVO_PRUEBAS):
        os.remove(ARCHIVO_PRUEBAS)          # cada simulación empieza con una base de prueba vacía
    base_real = usar_base(ARCHIVO_PRUEBAS)
    try:
        _ejecutar_fases_de_prueba()
    finally:
        usar_base(base_real)
        for lista, copia in zip(ARREGLOS, respaldo_arreglos):
            lista.clear()
            lista.extend(copia)
        print(f"\n[FIN DE PRUEBAS] Resultado guardado en '{ARCHIVO_PRUEBAS}'. "
              f"La base real '{ARCHIVO_DATOS}' quedó sin cambios.")


def _ejecutar_fases_de_prueba() -> None:
    """Fases 1 a 7: registro, validación, ordenamiento, búsqueda, persistencia, estados y seguridad."""
    print("=" * 116)
    print("   SISTEMA DE MESA DE PARTES DIGITAL - MUNICIPALIDAD DISTRITAL DE LOS BAÑOS DEL INCA (CAJAMARCA)")
    print("   Contribuye al cumplimiento de la Ley N.° 31170 y Decreto Legislativo N.° 1412 - Prototipo v1.0")
    print("=" * 116)

    datos_campo = [
        ("71458923", "Chilón Chuquimango, Jorge Luis", "Solicitud de Licencia de Edificación en C.P. Otuzco", 0, 18, "2026-10-14 08:35:10"),
        ("42891034", "Vásquez Rabanal, María Elena", "Reclamo por Arbitrios Municipales 2026 - Jr. Manco Cápac", 1, 6, "2026-10-14 09:12:45"),
        ("20453891201", "Lácteos Huacariz Cajamarca S.A.C.", "Renovación de Licencia de Funcionamiento Industrial", 2, 24, "2026-10-14 10:05:19"),
        ("26704512", "portal Minchán, Segundo Teófilo", "Copia Certificada de Acta de Matrimonio Civil 1998", 3, 2, "2026-10-15 11:20:00"),
        ("73901248", "Cabrera Bazán, Rocío del Pilar", "Inspección Técnica de Saneamiento en Tartar Grande", 4, 9, "2026-10-15 14:40:33"),
        ("40129876", "Tirado Gallardo, Carlos Alberto", "Constancia de Posesión para Electrificación Rural Shaullo", 0, 15, "2026-10-16 08:50:12"),
    ]

    print("\n[FASE 1] REGISTRO DE EXPEDIENTES RECOGIDOS EN PRÁCTICA DE CAMPO (CAJAMARCA):")
    for dni, nom, asu, area_idx, fol, fec in datos_campo:
        exito, msg = insertar_expediente(dni, nom, asu, area_idx, fol, fec)
        print(f"  -> Registro {'[EXITOSO]' if exito else '[FALLIDO]'}: Código asignado = {msg} | Administrado: {normalizar_texto(nom)}")

    print("\n[FASE 2] PRUEBAS DE VALIDACIÓN DE REGLAS DE NEGOCIO (DETECCIÓN DE ERRORES):")
    casos_error = [
        ("7145AB23", "Terán Silva, Pedro", "Solicitud de poda de árboles en parque", 4, 3),
        ("12345", "Salazar Rojas, Ana", "Certificado de parámetros urbanísticos", 0, 5),
        ("74892011", "Lu", "Solicitud de exoneración predial adulto mayor", 1, 4),
        ("74892011", "Mendoza Quispe, Rosa", "Trámite", 2, 4),
        ("74892011", "Mendoza Quispe, Rosa", "Solicitud de alineamiento vial en Av. Atahualpa", 0, 0),
    ]
    for dni_e, nom_e, asu_e, area_e, fol_e in casos_error:
        exito, msg = insertar_expediente(dni_e, nom_e, asu_e, area_e, fol_e)
        print(f"  -> Prueba con entrada inválida (DNI='{dni_e}', Nom='{nom_e}', Folios={fol_e}): {msg}")

    print("\n[FASE 3] ORDENAMIENTO ALFABÉTICO POR CIUDADANO Y LISTADO GENERAL:")
    ordenar_expedientes_por_ciudadano()
    print(mostrar_tabla_expedientes())

    print("\n[FASE 4] BÚSQUEDA BINARIA O(log2 n) POR CÓDIGO DE EXPEDIENTE:")
    for cod_consulta in ["EXP-2026-0004", "EXP-2026-0099"]:
        pos = buscar_por_codigo_binaria(cod_consulta)
        if pos != -1:
            print(f"  [ENCONTRADO] {codigos[pos]} | Ciudadano: {ciudadanos[pos]} | Área: {areas[pos]} | Fecha: {fechas[pos]}")
        else:
            print(f"  [NO ENCONTRADO] El código '{cod_consulta}' no existe en el padrón de expedientes.")

    print("\n[FASE 5] VERIFICACIÓN DE PERSISTENCIA EN SQLITE:")
    total_reconstruidos = cargar_padron()
    print(f"  -> Base de datos leída correctamente. Registros recuperados del disco: {total_reconstruidos}")

    print("\n[FASE 6] SEGUIMIENTO: ACTUALIZACIÓN DE ESTADO DE EXPEDIENTES:")
    cambios = [("EXP-2026-0002", "EN EVALUACIÓN"), ("EXP-2026-0002", "atendido"),
               ("EXP-2026-0002", "OBSERVADO"), ("EXP-2026-0003", "ARCHIVADO"),
               ("EXP-2026-0099", "ATENDIDO")]
    for cod, estado in cambios:
        exito, msg = actualizar_estado_expediente(cod, estado)
        print(f"  -> {cod} a '{estado}': {'[ACEPTADO] ' if exito else '[RECHAZADO] '}{msg}")

    print("\n[FASE 7] SEGURIDAD: INTENTOS DE INYECCIÓN SQL (CONSULTAS PARAMETRIZADAS):")
    with closing(conectar()) as con:
        antes = con.execute("SELECT COUNT(*) FROM expedientes").fetchone()[0]
    ataque = "Robert'); DROP TABLE expedientes; --"
    exito, msg = insertar_expediente("74892011", ataque, "Prueba de inyeccion SQL en el nombre", 5, 1)
    print(f"  -> Nombre malicioso: {'[GUARDADO COMO TEXTO] ' + msg if exito else '[RECHAZADO] ' + msg}")
    for cod in ["' OR '1'='1", "EXP-2026-0001' OR 1=1 --"]:
        print(f"  -> Búsqueda con código malicioso {cod!r}: posición {buscar_por_codigo_binaria(cod)} (no existe)")
        exito, msg = actualizar_estado_expediente(cod, "ATENDIDO")
        print(f"  -> Cambio de estado con ese código: {'[ACEPTADO] ' if exito else '[RECHAZADO] '}{msg}")
    with closing(conectar()) as con:
        despues = con.execute("SELECT COUNT(*) FROM expedientes").fetchone()[0]
        atendidos = con.execute("SELECT COUNT(*) FROM expedientes WHERE estado = 'ATENDIDO'").fetchone()[0]
    print(f"  -> La tabla sigue existiendo: {antes} expedientes antes y {despues} después; "
          f"ATENDIDOS: {atendidos} (solo el cambio legítimo de la fase 6).")
    try:
        with closing(conectar()) as con, con:
            con.execute("UPDATE expedientes SET folios = 999 WHERE codigo = 'EXP-2026-0001'")
        print("  -> [FALLA] La base aceptó 999 folios.")
    except sqlite3.IntegrityError as error:
        print(f"  -> Escritura directa con 999 folios: [RECHAZADA POR LA BASE] {error}")
