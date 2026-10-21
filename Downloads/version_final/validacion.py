#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 2: FUNCIONES DE VALIDACIÓN Y MANIPULACIÓN DE CADENAS DE CARACTERES
"""

from typing import List, Tuple


def normalizar_texto(texto: str) -> str:
    """Limpia espacios extremos, dobles espacios y convierte a mayúsculas."""
    palabras = texto.strip().upper().split()
    return " ".join(palabras)


def validar_dni_o_ruc(documento: str) -> Tuple[bool, str]:
    """
    Valida mediante lógica proposicional que el documento sea un DNI (8 dígitos)
    o un RUC (11 dígitos que inicia en 10 o 20) compuesto exclusivamente por números.
    """
    doc_limpio = documento.strip()
    if not doc_limpio.isdigit():
        return False, "Error: El documento debe contener únicamente dígitos numéricos (0-9)."
    if len(doc_limpio) == 8:
        return True, doc_limpio
    if len(doc_limpio) == 11 and (doc_limpio.startswith("10") or doc_limpio.startswith("20")):
        return True, doc_limpio
    return False, "Error: Ingrese un DNI válido (8 dígitos) o RUC válido (11 dígitos iniciando en 10 o 20)."


def validar_nombre_ciudadano(nombre: str) -> Tuple[bool, str]:
    """Valida que el nombre o razón social tenga longitud mínima y formato válido."""
    nombre_norm = normalizar_texto(nombre)
    if len(nombre_norm) < 5:
        return False, "Error: El nombre del ciudadano debe tener al menos 5 caracteres."
    sin_espacios = nombre_norm.replace(" ", "").replace(",", "").replace(".", "")
    if sin_espacios.isdigit():
        return False, "Error: El nombre del ciudadano no puede estar compuesto solo por números."
    return True, nombre_norm


def validar_asunto(asunto: str) -> Tuple[bool, str]:
    """Valida que el asunto del trámite sea descriptivo y no contenga el delimitador CSV (;)."""
    asunto_norm = normalizar_texto(asunto).replace(";", ",")
    if len(asunto_norm) < 8:
        return False, "Error: El asunto debe detallar el trámite (mínimo 8 caracteres)."
    return True, asunto_norm


def validar_folios(valor_texto: str) -> Tuple[bool, int]:
    """Valida que el número de folios sea un entero positivo entre 1 y 500."""
    limpio = str(valor_texto).strip()
    if not limpio.isdigit():
        return False, 0
    num = int(limpio)
    if 1 <= num <= 500:
        return True, num
    return False, 0


def generar_codigo_expediente(lista_codigos: List[str], anio: int = 2026) -> str:
    """
    Genera automáticamente un código único con formato EXP-2026-XXXX
    extrayendo el correlativo máximo mediante descomposición de cadenas (.split('-')).
    """
    if len(lista_codigos) == 0:
        return f"EXP-{anio}-0001"
    max_correlativo = 0
    for cod in lista_codigos:
        partes = cod.split("-")
        if len(partes) == 3 and partes[2].isdigit():
            corr = int(partes[2])
            if corr > max_correlativo:
                max_correlativo = corr
    nuevo_corr = max_correlativo + 1
    return f"EXP-{anio}-{nuevo_corr:04d}"
