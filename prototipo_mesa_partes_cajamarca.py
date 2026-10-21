#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime
from typing import List, Tuple

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

ESTADOS_VALIDOS = ["REGISTRADO", "EN EVALUACIÓN", "OBSERVADO", "ATENDIDO"]

codigos: List[str] = []
dnis: List[str] = []
ciudadanos: List[str] = []
asuntos: List[str] = []
areas: List[str] = []
folios: List[int] = []
fechas: List[str] = []
estados: List[str] = []


def normalizar_texto(texto: str) -> str:
    palabras = texto.strip().upper().split()
    return " ".join(palabras)


def validar_dni_o_ruc(documento: str) -> Tuple[bool, str]:
    doc_limpio = documento.strip()
    if not doc_limpio.isdigit():
        return False, "Error: El documento debe contener únicamente dígitos numéricos (0-9)."
    if len(doc_limpio) == 8:
        return True, doc_limpio
    if len(doc_limpio) == 11 and (doc_limpio.startswith("10") or doc_limpio.startswith("20")):
        return True, doc_limpio
    return False, "Error: Ingrese un DNI válido (8 dígitos) o RUC válido (11 dígitos iniciando en 10 o 20)."


def validar_nombre_ciudadano(nombre: str) -> Tuple[bool, str]:
    nombre_norm = normalizar_texto(nombre)
    if len(nombre_norm) < 5:
        return False, "Error: El nombre del ciudadano debe tener al menos 5 caracteres."
    sin_espacios = nombre_norm.replace(" ", "").replace(",", "").replace(".", "")
    if sin_espacios.isdigit():
        return False, "Error: El nombre del ciudadano no puede estar compuesto solo por números."
    return True, nombre_norm


def validar_asunto(asunto: str) -> Tuple[bool, str]:
    asunto_norm = normalizar_texto(asunto).replace(";", ",")
    if len(asunto_norm) < 8:
        return False, "Error: El asunto debe detallar el trámite (mínimo 8 caracteres)."
    return True, asunto_norm


def validar_folios(valor_texto: str) -> Tuple[bool, int]:
    limpio = valor_texto.strip()
    if not limpio.isdigit():
        return False, 0
    num = int(limpio)
    if 1 <= num <= 500:
        return True, num
    return False, 0


def generar_codigo_expediente(lista_codigos: List[str], anio: int = 2026) -> str:
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


def registrar_auditoria(accion: str, detalle: str) -> None:
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca_tiempo}] [{accion}] {detalle}\n"
    try:
        with open(ARCHIVO_AUDITORIA, mode="a", encoding="utf-8") as f_log:
            f_log.write(linea)
    except OSError as e:
        print(f"[ADVERTENCIA] No se pudo escribir en la bitácora: {e}")


def guardar_en_archivo(ruta_archivo: str = ARCHIVO_DATOS) -> bool:
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
    try:
        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            lector = csv.reader(archivo, delimiter=";")
            next(lector, None)
            for fila in lector:
                if len(fila) == 8:
                    codigos.append(fila[0])
                    dnis.append(fila[1])
                    ciudadanos.append(fila[2])
                    asuntos.append(fila[3])
                    areas.append(fila[4])
                    # Corrección: Uso de .strip() antes de .isdigit() para evitar errores por espacios
                    folios.append(int(fila[5].strip()) if fila[5].strip().isdigit() else 1)
                    fechas.append(fila[6])
                    estados.append(fila[7])
                    contador += 1
        registrar_auditoria("CARGA_INICIAL", f"Se cargaron {contador} expedientes desde {ruta_archivo}.")
    except OSError as error:
        print(f"[ERROR] No se pudo leer el archivo de datos: {error}")
    return contador


def insertar_expediente(dni_doc: str, nombre_ciud: str, asunto_tramite: str, indice_area: int, num_folios: int, fecha_manual: str = "") -> Tuple[bool, str]:
    ok_dni, res_dni = validar_dni_o_ruc(dni_doc)
    if not ok_dni: return False, res_dni

    ok_nom, res_nom = validar_nombre_ciudadano(nombre_ciud)
    if not ok_nom: return False, res_nom

    ok_asu, res_asu = validar_asunto(asunto_tramite)
    if not ok_asu: return False, res_asu

    if not (0 <= indice_area < len(AREAS_MUNICIPALES)):
        return False, "Error: El índice de área municipal seleccionada no es válido."

    if not (1 <= num_folios <= 500):
        return False, "Error: El número de folios debe estar entre 1 y 500."

    nuevo_codigo = generar_codigo_expediente(codigos)
    marca_fecha = fecha_manual if fecha_manual else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    codigos.append(nuevo_codigo)
    dnis.append(res_dni)
    ciudadanos.append(res_nom)
    asuntos.append(res_asu)
    areas.append(AREAS_MUNICIPALES[indice_area])
    folios.append(num_folios)
    fechas.append(marca_fecha)
    estados.append("REGISTRADO")

    guardar_en_archivo()
    registrar_auditoria("REGISTRO", f"Nuevo expediente {nuevo_codigo} - DNI/RUC: {res_dni}")
    return True, nuevo_codigo


def intercambiar_indices(i: int, j: int) -> None:
    codigos[i], codigos[j] = codigos[j], codigos[i]
    dnis[i], dnis[j] = dnis[j], dnis[i]
    ciudadanos[i], ciudadanos[j] = ciudadanos[j], ciudadanos[i]
    asuntos[i], asuntos[j] = asuntos[j], asuntos[i]
    areas[i], areas[j] = areas[j], areas[i]
    folios[i], folios[j] = folios[j], folios[i]
    fechas[i], fechas[j] = fechas[j], fechas[i]
    estados[i], estados[j] = estados[j], estados[i]


def ordenar_expedientes_por_codigo(ascendente: bool = True) -> None:
    n = len(codigos)
    for i in range(n - 1):
        hubo_intercambio = False
        for j in range(0, n - i - 1):
            condicion = (codigos[j] > codigos[j + 1]) if ascendente else (codigos[j] < codigos[j + 1])
            if condicion:
                intercambiar_indices(j, j + 1)
                hubo_intercambio = True
        if not hubo_intercambio:
            break
    guardar_en_archivo()


def buscar_por_codigo_binaria(codigo_buscado: str) -> int:
    ordenar_expedientes_por_codigo(ascendente=True)
    objetivo = normalizar_texto(codigo_buscado)
    izquierda = 0
    derecha = len(codigos) - 1

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        if codigos[medio] == objetivo:
            return medio
        elif codigos[medio] < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1


def buscar_por_dni_secuencial(dni_buscado: str) -> List[int]:
    objetivo = dni_buscado.strip()
    indices_encontrados: List[int] = []
    for i in range(len(dnis)):
        if dnis[i] == objetivo:
            indices_encontrados.append(i)
    return indices_encontrados


def mostrar_tabla_expedientes(indices: List[int] = None) -> str:
    if len(codigos) == 0:
        return "No existen expedientes registrados en el sistema."

    if indices is None:
        indices = list(range(len(codigos)))

    lineas = []
    separador = "-" * 116
    lineas.append(separador)
    lineas.append(f"{'CÓDIGO':<14} | {'DNI/RUC':<11} | {'CIUDADANO / ADMINISTRADO':<28} | {'ASUNTO DEL TRÁMITE':<30} | {'FOLIOS':<6} | {'ESTADO':<13}")
    lineas.append(separador)
    for idx in indices:
        ciud_corto = ciudadanos[idx][:27]
        asunto_corto = asuntos[idx][:29]
        lineas.append(f"{codigos[idx]:<14} | {dnis[idx]:<11} | {ciud_corto:<28} | {asunto_corto:<30} | {folios[idx]:>6} | {estados[idx]:<13}")
    lineas.append(separador)
    lineas.append(f"Total de registros listados: {len(indices)}")
    return "\n".join(lineas)

# ==============================================================================
# NUEVO MÓDULO: MENÚ INTERACTIVO (CLI)
# ==============================================================================
def mostrar_menu():
    print("\n" + "=" * 60)
    print("   SISTEMA DE MESA DE PARTES DIGITAL - BAÑOS DEL INCA")
    print("=" * 60)
    print("[1] Registrar nuevo expediente")
    print("[2] Mostrar todos los expedientes")
    print("[3] Buscar expediente por código (Búsqueda Binaria)")
    print("[4] Buscar expedientes por DNI/RUC (Búsqueda Secuencial)")
    print("[5] Salir del sistema")
    print("=" * 60)

def ejecutar_sistema():
    total_cargados = cargar_desde_archivo()
    print(f"Sistema iniciado. {total_cargados} expedientes recuperados del almacenamiento local.")

    while True:
        mostrar_menu()
opcion = input("Seleccione una opción (1-5): ").strip()