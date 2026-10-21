#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 1: CONFIGURACIÓN Y ARREGLOS PARALELOS (ESTRUCTURAS LINEALES DE DATOS)
Prototipo de Mesa de Partes Digital - Municipalidad Distrital de Los Baños del Inca (Cajamarca)
Los ocho arreglos se comparten entre módulos: se modifican con sus métodos
(append, clear, intercambio por índice) y nunca se reasignan.
"""

from typing import List

ARCHIVO_DATOS = "expedientes_cajamarca.csv"
ARCHIVO_AUDITORIA = "auditoria_mesa_partes.log"
ARCHIVO_PRUEBAS = "expedientes_prueba.csv"   # Resultado de la simulación de pruebas

AREAS_MUNICIPALES = [
    "Subgerencia de Desarrollo Urbano y Rural",
    "Subgerencia de Administración Tributaria (SAT)",
    "Subgerencia de Licencias y Comercialización",
    "Oficina de Registro Civil",
    "Subgerencia de Medio Ambiente y Servicios Públicos",
    "Gerencia Municipal"
]

ESTADOS_VALIDOS = ["REGISTRADO", "EN EVALUACIÓN", "OBSERVADO", "ATENDIDO"]

# 8 Arreglos paralelos (listas unidimensionales sincronizadas por el índice i)
codigos: List[str] = []       # Ej: "EXP-2026-0001"
dnis: List[str] = []          # Ej: "71458923"
ciudadanos: List[str] = []    # Ej: "CHILON CHUQUIMANGO, JORGE LUIS"
asuntos: List[str] = []       # Ej: "SOLICITUD DE LICENCIA DE EDIFICACION EN C.P. OTUZCO"
areas: List[str] = []         # Ej: "Subgerencia de Desarrollo Urbano y Rural"
folios: List[int] = []        # Ej: 18
fechas: List[str] = []        # Ej: "2026-10-19 09:15:00"
estados: List[str] = []       # Ej: "REGISTRADO"

# Los 8 arreglos juntos, para respaldarlos o vaciarlos con un solo recorrido
ARREGLOS = [codigos, dnis, ciudadanos, asuntos, areas, folios, fechas, estados]
