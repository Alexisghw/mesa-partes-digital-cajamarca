#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 6: MENÚ INTERACTIVO POR TECLADO (INTERFAZ DE USUARIO EN CONSOLA)
"""

from datos import (ARCHIVO_DATOS, AREAS_MUNICIPALES,
                   codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados)
from validacion import (normalizar_texto, validar_dni_o_ruc, validar_nombre_ciudadano,
                        validar_asunto, validar_folios)
from persistencia import guardar_en_archivo, cargar_desde_archivo
from algoritmos import (insertar_expediente, ordenar_expedientes_por_codigo,
                        ordenar_expedientes_por_ciudadano, buscar_por_codigo_binaria,
                        buscar_por_dni_secuencial, mostrar_tabla_expedientes)
from pruebas import ejecutar_simulacion_cajamarca


def menu_interactivo() -> None:
    """
    Menú interactivo por consola que permite al usuario o evaluador introducir
    datos en vivo por teclado para registrar, buscar, ordenar y persistir trámites.
    """
    cargar_desde_archivo()
    while True:
        print("\n" + "=" * 70)
        print("  MESA DE PARTES DIGITAL — MUNICIPALIDAD DE LOS BAÑOS DEL INCA (CAJAMARCA)")
        print("=" * 70)
        print("  [1] Registrar nuevo expediente por teclado")
        print("  [2] Buscar expediente por código (Búsqueda Binaria O(log2 n))")
        print("  [3] Buscar expedientes por DNI/RUC del ciudadano")
        print("  [4] Listar expedientes ordenados por código")
        print("  [5] Listar expedientes ordenados alfabéticamente por ciudadano")
        print("  [6] Ejecutar simulación automática con datos de Cajamarca")
        print("  [7] Salir del sistema")
        print("-" * 70)

        opcion = input("Seleccione una opción (1-7): ").strip()

        if opcion == "1":
            print("\n--- INGRESO DE DATOS DEL EXPEDIENTE ---")
            dni_in = input("Ingrese DNI (8 dígitos) o RUC (11 dígitos): ").strip()
            ok_dni, msg_dni = validar_dni_o_ruc(dni_in)
            if not ok_dni:
                print(f"[ERROR] {msg_dni}")
                continue

            nombre_in = input("Ingrese Apellidos y Nombres (o Razón Social): ").strip()
            ok_nom, msg_nom = validar_nombre_ciudadano(nombre_in)
            if not ok_nom:
                print(f"[ERROR] {msg_nom}")
                continue

            asunto_in = input("Ingrese Asunto del trámite: ").strip()
            ok_asu, msg_asu = validar_asunto(asunto_in)
            if not ok_asu:
                print(f"[ERROR] {msg_asu}")
                continue

            print("\nÁreas de destino municipal disponibles:")
            for i, area in enumerate(AREAS_MUNICIPALES):
                print(f"  [{i}] {area}")
            area_str = input("Seleccione el número de área (0-5): ").strip()
            if not area_str.isdigit() or not (0 <= int(area_str) < len(AREAS_MUNICIPALES)):
                print("[ERROR] Selección de área inválida.")
                continue
            area_idx = int(area_str)

            folios_str = input("Ingrese número de folios (1-500): ").strip()
            ok_fol, num_fol = validar_folios(folios_str)
            if not ok_fol:
                print("[ERROR] El número de folios debe ser un entero entre 1 y 500.")
                continue

            exito, cod_generado = insertar_expediente(dni_in, nombre_in, asunto_in, area_idx, num_fol)
            if exito:
                print("\n" + "*" * 60)
                print(f"  ¡TRÁMITE REGISTRADO CON ÉXITO!")
                print(f"  Código Asignado: {cod_generado}")
                print(f"  Administrado:    {normalizar_texto(nombre_in)}")
                print(f"  Destino:         {AREAS_MUNICIPALES[area_idx]}")
                print(f"  Persistido en:   {ARCHIVO_DATOS}")
                print("*" * 60)
            else:
                print(f"[ERROR] No se pudo registrar: {cod_generado}")

        elif opcion == "2":
            cod_in = input("\nIngrese código a buscar (ej. EXP-2026-0001): ").strip()
            pos = buscar_por_codigo_binaria(cod_in)
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

        elif opcion == "3":
            dni_in = input("\nIngrese DNI o RUC a consultar: ").strip()
            hallados = buscar_por_dni_secuencial(dni_in)
            if hallados:
                print(f"\nExpedientes encontrados para el documento {dni_in}:")
                print(mostrar_tabla_expedientes(hallados))
            else:
                print(f"\n[AVISO] No hay expedientes registrados para el DNI/RUC '{dni_in}'.")

        elif opcion == "4":
            ordenar_expedientes_por_codigo(ascendente=True)
            print("\nPADRÓN ORDENADO POR CÓDIGO:")
            print(mostrar_tabla_expedientes())

        elif opcion == "5":
            ordenar_expedientes_por_ciudadano()
            print("\nPADRÓN ORDENADO ALFABÉTICAMENTE POR CIUDADANO:")
            print(mostrar_tabla_expedientes())

        elif opcion == "6":
            ejecutar_simulacion_cajamarca()

        elif opcion == "7":
            guardar_en_archivo()
            print("\n¡Gracias! Datos persistidos en disco. Cerrando sistema...")
            break
        else:
            print("[ERROR] Opción no válida. Ingrese un número del 1 al 7.")
