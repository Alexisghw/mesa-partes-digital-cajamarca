#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 2: FUNCIONES DE VALIDACIÓN Y MANIPULACIÓN DE CADENAS DE CARACTERES
"""

import unicodedata
from datetime import datetime
from typing import List, Optional, Tuple

from datos import AREAS_MUNICIPALES, ESTADOS_VALIDOS

FOLIOS_MINIMO = 1
FOLIOS_MAXIMO = 500


def normalizar_texto(texto: str) -> str:
    """Limpia espacios extremos, dobles espacios y convierte a mayúsculas."""
    palabras = texto.strip().upper().split()
    return " ".join(palabras)


def clave_orden_alfabetico(texto: str) -> str:
    """
    Devuelve la clave con la que se comparan dos nombres al ordenarlos A-Z en español.
    Python compara cadenas por su código Unicode, por eso 'Á' (193) quedaba después
    de 'Z' (90). Aquí se quitan las tildes (Á→A, É→E, Ü→U) y la Ñ se reemplaza por
    'N{' para que quede después de toda palabra con N y antes de la O
    (el carácter '{' tiene un código mayor que 'Z').
    """
    texto = unicodedata.normalize("NFC", normalizar_texto(texto)).replace("Ñ", "N{")
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


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
    if FOLIOS_MINIMO <= num <= FOLIOS_MAXIMO:
        return True, num
    return False, 0


def validar_opcion_area(opcion_texto: str) -> Tuple[bool, int]:
    """
    El usuario elige el área con un número del 1 al 6 (como en el informe).
    Retorna (True, índice del arreglo AREAS_MUNICIPALES) = opción - 1, o (False, -1).
    """
    limpio = str(opcion_texto).strip()
    if not limpio.isdigit():
        return False, -1
    opcion = int(limpio)
    if 1 <= opcion <= len(AREAS_MUNICIPALES):
        return True, opcion - 1
    return False, -1


def validar_indice_area(indice: int) -> bool:
    """Comprueba que un índice interno (0 a 5) exista en AREAS_MUNICIPALES."""
    return 0 <= indice < len(AREAS_MUNICIPALES)


def validar_estado(estado_texto: str) -> Tuple[bool, str]:
    """
    Valida que el estado sea uno de ESTADOS_VALIDOS. Acepta minúsculas y la palabra
    sin tilde ('en evaluacion') y retorna el nombre oficial ('EN EVALUACIÓN').
    """
    buscado = clave_orden_alfabetico(estado_texto)
    for estado in ESTADOS_VALIDOS:
        if clave_orden_alfabetico(estado) == buscado:
            return True, estado
    return False, "Error: Estado no válido. Use: " + ", ".join(ESTADOS_VALIDOS) + "."


def validar_codigo_expediente(codigo: str) -> bool:
    """Comprueba el formato EXP-AAAA-XXXX (solo dígitos 0-9 en el año y el correlativo)."""
    partes = codigo.strip().split("-")
    return (len(partes) == 3 and partes[0] == "EXP"
            and len(partes[1]) == 4 and len(partes[2]) == 4
            and all(c in "0123456789" for c in partes[1] + partes[2]))


def neutralizar_formula_csv(texto: str) -> str:
    """
    Evita la inyección CSV: si un texto empieza con = + - @ (o tabulación), Excel lo
    interpretaría como fórmula al abrir el archivo. Se antepone un apóstrofo para que
    se muestre como texto común.
    """
    if texto and texto[0] in "=+-@\t\r":
        return "'" + texto
    return texto


def generar_codigo_expediente(lista_codigos: List[str], anio: Optional[int] = None) -> str:
    """
    Genera automáticamente un código único con formato EXP-AAAA-XXXX
    extrayendo el correlativo máximo mediante descomposición de cadenas (.split('-')).
    El año se toma de la fecha del sistema si no se indica.
    """
    if anio is None:
        anio = datetime.now().year
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
