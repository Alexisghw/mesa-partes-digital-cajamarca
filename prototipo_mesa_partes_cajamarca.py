#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
