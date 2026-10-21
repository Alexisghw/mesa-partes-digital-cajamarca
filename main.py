#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTOTIPO DE MESA DE PARTES DIGITAL - MUNICIPALIDAD DISTRITAL DE LOS BAÑOS DEL INCA (CAJAMARCA)
Curso: Fundamentos de Programación (CIIN1205P) - Universidad Privada del Norte (UPN) - Sede Cajamarca
Título del Desafío: Del archivador al algoritmo, un prototipo para la mesa de partes digital
Normativa vinculada: Ley N.° 31170 y Decreto Legislativo N.° 1412 (Ley de Gobierno Digital)

Descripción técnica:
Este sistema implementa el registro interactivo por teclado, validación con lógica proposicional,
búsqueda binaria O(log2 n), ordenamiento Burbuja Mejorado sobre 8 arreglos paralelos
y persistencia permanente en archivos estructurados CSV (UTF-8).

Organización en módulos:
    datos.py         -> Módulo 1: configuración y arreglos paralelos
    validacion.py    -> Módulo 2: validación y cadenas de caracteres
    persistencia.py  -> Módulo 3: archivos CSV y bitácora de auditoría
    algoritmos.py    -> Módulo 4: inserción, ordenamiento y búsqueda
    pruebas.py       -> Módulo 5: simulación de pruebas con datos de campo
    interfaz.py      -> Módulo 6: menú interactivo por teclado

Ejecución:
    python main.py          -> menú interactivo
    python main.py --auto   -> simulación automática de pruebas
"""

import sys

from interfaz import menu_interactivo
from pruebas import ejecutar_simulacion_cajamarca


if __name__ == "__main__":
    # Por defecto siempre abre el menú interactivo con entrada por teclado
    # Solo ejecuta la simulación si se pasa explícitamente el parámetro --auto
    if len(sys.argv) > 1 and sys.argv[1] in ["--auto", "--simulacion"]:
        ejecutar_simulacion_cajamarca()
    else:
        menu_interactivo()
