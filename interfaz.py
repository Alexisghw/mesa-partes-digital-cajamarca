#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 6: MENÚ INTERACTIVO POR TECLADO (INTERFAZ DE USUARIO EN CONSOLA)
"""

from datos import (ARCHIVO_DATOS, ARCHIVO_EXPORTACION, AREAS_MUNICIPALES,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)
from datos import ESTADOS_VALIDOS
from validacion import (normalizar_texto, validar_dni_o_ruc, validar_nombre_ciudadano,
                        validar_asunto, validar_folios, validar_opcion_area, es_numero_ascii)
from persistencia import guardar_padron, cargar_padron, exportar_csv, registrar_auditoria
from algoritmos import (insertar_expediente, ordenar_expedientes_por_codigo,
                        ordenar_expedientes_por_ciudadano, buscar_por_codigo_binaria,
                        buscar_por_dni_secuencial, mostrar_tabla_expedientes,
                        actualizar_estado_expediente)
from pruebas import ejecutar_simulacion_cajamarca
from recursividad import (reporte_recursivo, comparar_iterativa_vs_recursiva,
                          buscar_por_codigo_recursiva)
from analisis import comparar_burbuja_vs_seleccion


def _opcion_registrar() -> None:
    """Opción 1: pide los datos por teclado, los valida campo por campo y registra el expediente."""
    print("\n--- INGRESO DE DATOS DEL EXPEDIENTE ---")
    dni_in = input("Ingrese DNI (8 dígitos) o RUC (11 dígitos): ").strip()
    ok_dni, msg_dni = validar_dni_o_ruc(dni_in)
    if not ok_dni:
        print(f"[ERROR] {msg_dni.removeprefix('Error: ')}")
        return

    nombre_in = input("Ingrese Apellidos y Nombres (o Razón Social): ").strip()
    ok_nom, msg_nom = validar_nombre_ciudadano(nombre_in)
    if not ok_nom:
        print(f"[ERROR] {msg_nom.removeprefix('Error: ')}")
        return

    asunto_in = input("Ingrese Asunto del trámite: ").strip()
    ok_asu, msg_asu = validar_asunto(asunto_in)
    if not ok_asu:
        print(f"[ERROR] {msg_asu.removeprefix('Error: ')}")
        return

    print("\nÁreas de destino municipal disponibles:")
    for i, area in enumerate(AREAS_MUNICIPALES, start=1):
        print(f"  [{i}] {area}")
    area_str = input(f"Seleccione el número de área (1-{len(AREAS_MUNICIPALES)}): ").strip()
    ok_area, area_idx = validar_opcion_area(area_str)   # área 1 -> índice 0
    if not ok_area:
        print("[ERROR] Selección de área inválida.")
        return

    folios_str = input("Ingrese número de folios (1-500): ").strip()
    ok_fol, num_fol = validar_folios(folios_str)
    if not ok_fol:
        print("[ERROR] El número de folios debe ser un entero entre 1 y 500.")
        return

    exito, cod_generado = insertar_expediente(dni_in, nombre_in, asunto_in, area_idx, num_fol)
    if exito:
        print("\n" + "*" * 60)
        print(f"  ¡TRÁMITE REGISTRADO CON ÉXITO!")
        print(f"  Código Asignado: {cod_generado}")
        print(f"  Administrado:    {normalizar_texto(nombre_in)}")
        print(f"  Destino:         {AREAS_MUNICIPALES[area_idx]}")
        print(f"  Guardado en:     {ARCHIVO_DATOS} (SQLite)")
        print("*" * 60)
    else:
        print(f"[ERROR] No se pudo registrar: {cod_generado.removeprefix('Error: ')}")


def _opcion_buscar_codigo() -> None:
    """Opción 2: búsqueda binaria por código."""
    cod_in = input("\nIngrese código a buscar (ej. EXP-2026-0001): ").strip()
    pos = buscar_por_codigo_binaria(cod_in)
    pos_recursiva = buscar_por_codigo_recursiva(cod_in)
    print(f"  (Binaria iterativa -> posición {pos} | binaria recursiva -> posición {pos_recursiva})")
    if pos != -1:
        print("\n" + "=" * 60)
        print(f"  EXPEDIENTE ENCONTRADO (Posición {pos}):")
        print(f"  Código:      {codigos[pos]}")
        print(f"  DNI/RUC:     {dnis[pos]}")
        print(f"  Ciudadano:   {ciudadanos[pos]}")
        print(f"  Asunto:      {asuntos[pos]}")
        print(f"  Área:        {areas[pos]}")
        print(f"  Folios:      {folios[pos]}")
        print(f"  Fecha/Hora:  {fechas[pos]}")
        print(f"  Estado:      {estados[pos]}")
        print("=" * 60)
    else:
        print(f"\n[AVISO] No se encontró ningún trámite con el código '{cod_in}'.")


def _opcion_buscar_dni() -> None:
    """Opción 3: búsqueda secuencial de todos los expedientes de un DNI/RUC."""
    dni_in = input("\nIngrese DNI o RUC a consultar: ").strip()
    hallados = buscar_por_dni_secuencial(dni_in)
    if hallados:
        print(f"\nExpedientes encontrados para el documento {dni_in}:")
        print(mostrar_tabla_expedientes(hallados))
    else:
        print(f"\n[AVISO] No hay expedientes registrados para el DNI/RUC '{dni_in}'.")


def _opcion_actualizar_estado() -> None:
    """Opción 4: cambia el estado de un expediente (seguimiento del trámite)."""
    cod_in = input("\nIngrese el código del expediente (ej. EXP-2026-0001): ").strip()
    print("Estados disponibles:")
    for i, estado in enumerate(ESTADOS_VALIDOS, start=1):
        print(f"  [{i}] {estado}")
    eleccion = input(f"Seleccione el nuevo estado (1-{len(ESTADOS_VALIDOS)}): ").strip()
    if es_numero_ascii(eleccion) and len(eleccion) == 1 and 1 <= int(eleccion) <= len(ESTADOS_VALIDOS):
        eleccion = ESTADOS_VALIDOS[int(eleccion) - 1]
    exito, mensaje = actualizar_estado_expediente(cod_in, eleccion)
    print(f"[ESTADO ACTUALIZADO] {mensaje}" if exito else f"[RECHAZADO] {mensaje.removeprefix('Error: ')}")


def _opcion_comparar_algoritmos() -> None:
    """Opción 8: tabla iterativa vs. recursiva y tabla Burbuja vs. Selección."""
    comparar_iterativa_vs_recursiva()
    comparar_burbuja_vs_seleccion()


def _opcion_listar_por_codigo() -> None:
    """Lista el padrón ordenado por código (Burbuja Mejorado)."""
    ordenar_expedientes_por_codigo(ascendente=True)
    print("\nPADRÓN ORDENADO POR CÓDIGO:")
    print(mostrar_tabla_expedientes())


def _opcion_listar_por_ciudadano() -> None:
    """Lista el padrón ordenado alfabéticamente por ciudadano (Burbuja Mejorado con clave sin tildes)."""
    ordenar_expedientes_por_ciudadano()
    print("\nPADRÓN ORDENADO ALFABÉTICAMENTE POR CIUDADANO:")
    print(mostrar_tabla_expedientes())


def _opcion_reporte_recursivo() -> None:
    """Resumen de folios y estados calculado con funciones recursivas (Módulo 7)."""
    print("\nREPORTE DEL PADRÓN (CÁLCULO RECURSIVO):")
    print(reporte_recursivo())


def _opcion_exportar_csv() -> None:
    """Opción 10: copia del padrón en CSV para abrir en Excel (con fórmulas neutralizadas)."""
    if exportar_csv():
        print(f"\n[EXPORTADO] {len(codigos)} expedientes en '{ARCHIVO_EXPORTACION}' (se abre con Excel).")


# Opciones del menú: número -> (texto que se muestra, función que se ejecuta)
OPCIONES_MENU = {
    "1": ("Registrar nuevo expediente por teclado", _opcion_registrar),
    "2": ("Buscar expediente por código (Búsqueda Binaria O(log2 n))", _opcion_buscar_codigo),
    "3": ("Buscar expedientes por DNI/RUC del ciudadano", _opcion_buscar_dni),
    "4": ("Actualizar el estado de un expediente", _opcion_actualizar_estado),
    "5": ("Listar expedientes ordenados por código", _opcion_listar_por_codigo),
    "6": ("Listar expedientes ordenados alfabéticamente por ciudadano", _opcion_listar_por_ciudadano),
    "7": ("Reporte de folios y estados (funciones recursivas)", _opcion_reporte_recursivo),
    "8": ("Comparar algoritmos (iterativo vs. recursivo, Burbuja vs. Selección)", _opcion_comparar_algoritmos),
    "9": ("Ejecutar simulación automática con datos de Cajamarca", ejecutar_simulacion_cajamarca),
    "10": ("Exportar el padrón a CSV para Excel", _opcion_exportar_csv),
}
OPCION_SALIR = "0"


def menu_interactivo() -> None:
    """
    Menú interactivo por consola que permite al usuario o evaluador introducir
    datos en vivo por teclado para registrar, buscar, ordenar y persistir trámites.
    """
    cargar_padron()
    while True:
        print("\n" + "=" * 70)
        print("  MESA DE PARTES DIGITAL — MUNICIPALIDAD DE LOS BAÑOS DEL INCA (CAJAMARCA)")
        print("=" * 70)
        for numero, (texto, _) in OPCIONES_MENU.items():
            print(f"  [{numero}] {texto}")
        print(f"  [{OPCION_SALIR}] Salir del sistema")
        print("-" * 70)

        opcion = input("Seleccione una opción: ").strip()
        if opcion == OPCION_SALIR:
            guardar_padron()
            print("\n¡Gracias! Datos persistidos en disco. Cerrando sistema...")
            break
        if opcion in OPCIONES_MENU:
            try:
                OPCIONES_MENU[opcion][1]()
            except Exception as error:   # ninguna entrada puede cerrar el programa con un error de Python
                registrar_auditoria("ERROR", f"Opción {opcion}: {type(error).__name__}: {error}")
                print("[ERROR] La operación se canceló por un dato inesperado. Los datos guardados no cambiaron.")
        else:
            print("[ERROR] Opción no válida. Elija una de las opciones del menú.")
