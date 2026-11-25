#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRUEBAS AUTOMÁTICAS (matriz de casos de prueba CP-xx, sesión 6.3)
Cada prueba usa los valores normales, el límite, el adyacente al límite y entradas inválidas.
Ejecutar desde la carpeta del proyecto:
    python -m unittest discover -s tests -v
Cada prueba trabaja en una carpeta temporal: nunca toca expedientes_cajamarca.csv real.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datos                                                    # noqa: E402
from datos import ARREGLOS, codigos, ciudadanos, estados, folios  # noqa: E402
from validacion import (validar_dni_o_ruc, validar_nombre_ciudadano, validar_asunto,  # noqa: E402
                        validar_folios, validar_opcion_area, validar_estado,
                        generar_codigo_expediente, clave_orden_alfabetico)
from persistencia import guardar_en_archivo, cargar_desde_archivo      # noqa: E402
from algoritmos import (insertar_expediente, ordenar_expedientes_por_codigo,  # noqa: E402
                        ordenar_expedientes_por_codigo_seleccion, ordenar_expedientes_por_ciudadano,
                        buscar_por_codigo_binaria, busqueda_binaria_iterativa,
                        buscar_por_dni_secuencial, actualizar_estado_expediente)
from recursividad import (busqueda_binaria_recursiva, sumar_folios_recursivo,  # noqa: E402
                          contar_por_estado_recursivo)
from pruebas import ejecutar_simulacion_cajamarca                      # noqa: E402

CAMPO = [
    ("71458923", "Chilón Chuquimango, Jorge Luis", "Solicitud de Licencia de Edificación", 0, 18),
    ("42891034", "Vásquez Rabanal, María Elena", "Reclamo por Arbitrios Municipales 2026", 1, 6),
    ("20453891201", "Lácteos Huacariz Cajamarca S.A.C.", "Renovación de Licencia de Funcionamiento", 2, 24),
]


class BaseConCarpetaTemporal(unittest.TestCase):
    """Cambia a una carpeta temporal vacía y vacía los 8 arreglos antes de cada prueba."""

    def setUp(self):
        self._carpeta_original = os.getcwd()
        self._temporal = tempfile.TemporaryDirectory()
        os.chdir(self._temporal.name)
        for lista in ARREGLOS:
            lista.clear()

    def tearDown(self):
        os.chdir(self._carpeta_original)
        self._temporal.cleanup()

    def registrar_campo(self):
        for dni, nom, asu, area, fol in CAMPO:
            ok, msg = insertar_expediente(dni, nom, asu, area, fol, "2026-10-14 08:00:00")
            self.assertTrue(ok, msg)


class TestValidaciones(unittest.TestCase):
    """CP-01 a CP-08: reglas de negocio con valores límite."""

    def test_cp01_dni_longitud(self):
        self.assertTrue(validar_dni_o_ruc("71458923")[0])        # 8 dígitos: normal
        self.assertFalse(validar_dni_o_ruc("7145892")[0])        # 7: adyacente inferior
        self.assertFalse(validar_dni_o_ruc("714589231")[0])      # 9: adyacente superior

    def test_cp02_ruc_prefijo(self):
        self.assertTrue(validar_dni_o_ruc("10458912345")[0])
        self.assertTrue(validar_dni_o_ruc("20453891201")[0])
        self.assertFalse(validar_dni_o_ruc("15453891201")[0])    # 11 dígitos, prefijo inválido

    def test_cp03_documento_invalido(self):
        for valor in ["7145AB23", "", "   ", "71458-23"]:
            self.assertFalse(validar_dni_o_ruc(valor)[0], valor)

    def test_cp04_folios_limites(self):
        self.assertEqual(validar_folios("1"), (True, 1))
        self.assertEqual(validar_folios("500"), (True, 500))
        for valor in ["0", "501", "-1", "abc", "", "3.5"]:
            self.assertFalse(validar_folios(valor)[0], valor)

    def test_cp05_nombre(self):
        self.assertFalse(validar_nombre_ciudadano("Luis")[0])     # 4 caracteres
        self.assertTrue(validar_nombre_ciudadano("Luisa")[0])     # 5: límite
        self.assertFalse(validar_nombre_ciudadano("12345678")[0])
        self.assertEqual(validar_nombre_ciudadano("  ana   ruiz ")[1], "ANA RUIZ")

    def test_cp06_asunto(self):
        self.assertFalse(validar_asunto("Trámite")[0])            # 7 caracteres
        self.assertTrue(validar_asunto("Trámites")[0])            # 8: límite
        self.assertNotIn(";", validar_asunto("Licencia; edificación")[1])

    def test_cp07_area_1_a_6(self):
        self.assertEqual(validar_opcion_area("1"), (True, 0))
        self.assertEqual(validar_opcion_area("6"), (True, 5))
        for valor in ["0", "7", "x", ""]:
            self.assertFalse(validar_opcion_area(valor)[0], valor)

    def test_cp08_codigo_correlativo(self):
        self.assertEqual(generar_codigo_expediente([], 2026), "EXP-2026-0001")
        self.assertEqual(generar_codigo_expediente(["EXP-2026-0001", "EXP-2026-0007"], 2026),
                         "EXP-2026-0008")


class TestBusquedas(unittest.TestCase):
    """CP-09 a CP-11: búsqueda binaria iterativa y recursiva."""

    LISTA = [f"EXP-2026-{k:04d}" for k in range(1, 101)]

    def test_cp09_binaria_extremos_y_ausentes(self):
        for objetivo, esperado in [("EXP-2026-0001", 0), ("EXP-2026-0100", 99),
                                   ("EXP-2026-0050", 49), ("EXP-2026-0101", -1), ("EXP-2025-0001", -1)]:
            self.assertEqual(busqueda_binaria_iterativa(self.LISTA, objetivo), esperado)

    def test_cp10_recursiva_equivale_a_iterativa(self):
        for objetivo in self.LISTA + ["EXP-0000-0000", "EXP-9999-9999"]:
            c_it, c_rec = [0], [0]
            self.assertEqual(busqueda_binaria_iterativa(self.LISTA, objetivo, c_it),
                             busqueda_binaria_recursiva(self.LISTA, objetivo, 0, 99, c_rec))
            self.assertEqual(c_it[0], c_rec[0])
            self.assertLessEqual(c_rec[0], 7)                      # ⌈log2(101)⌉ = 7

    def test_cp11_lista_vacia_y_un_elemento(self):
        self.assertEqual(busqueda_binaria_recursiva([], "EXP-2026-0001", 0, -1), -1)
        self.assertEqual(busqueda_binaria_recursiva(["EXP-2026-0001"], "EXP-2026-0001", 0, 0), 0)


class TestRecursividadSobreArreglos(unittest.TestCase):
    """CP-12: suma y conteo recursivos, incluido un arreglo de 5000 elementos."""

    def test_cp12_suma_y_conteo(self):
        self.assertEqual(sumar_folios_recursivo([], 0, -1), 0)
        self.assertEqual(sumar_folios_recursivo([18, 6, 24], 0, 2), 48)
        grande = list(range(1, 5001))
        self.assertEqual(sumar_folios_recursivo(grande, 0, 4999), 5000 * 5001 // 2)  # sin RecursionError
        self.assertEqual(contar_por_estado_recursivo(["REGISTRADO", "ATENDIDO", "REGISTRADO"],
                                                     "REGISTRADO", 0, 2), 2)


class TestOperacionesSobreElPadron(BaseConCarpetaTemporal):
    """CP-13 a CP-19: registro, ordenamientos, estados, persistencia y regresión de la simulación."""

    def test_cp13_registro_y_rechazo(self):
        self.registrar_campo()
        self.assertEqual(list(codigos), ["EXP-2026-0001", "EXP-2026-0002", "EXP-2026-0003"])
        ok, _ = insertar_expediente("71458923", "Persona Valida", "Asunto valido largo", 6, 3)
        self.assertFalse(ok)                                     # índice 6 = opción 7, inexistente
        ok, _ = insertar_expediente("71458923", "Persona Valida", "Asunto valido largo", 0, 501)
        self.assertFalse(ok)
        self.assertEqual(len(codigos), 3)
        self.assertEqual(buscar_por_dni_secuencial("42891034"), [1])

    def test_cp14_orden_alfabetico_con_tildes_y_enie(self):
        for nombre in ["Zavala Luis", "Ñontol Brayan", "Álvarez Ana", "Novoa Rai", "Ocaña Pedro"]:
            insertar_expediente("71458923", nombre, "Asunto de prueba", 0, 1)
        ordenar_expedientes_por_ciudadano()
        self.assertEqual(list(ciudadanos), ["ÁLVAREZ ANA", "NOVOA RAI", "ÑONTOL BRAYAN",
                                            "OCAÑA PEDRO", "ZAVALA LUIS"])
        self.assertLess(clave_orden_alfabetico("Nuñez"), clave_orden_alfabetico("Nuzco"))

    def test_cp15_burbuja_y_seleccion_mismo_resultado(self):
        self.registrar_campo()
        ordenar_expedientes_por_codigo(ascendente=False, guardar=False)
        self.assertEqual(codigos[0], "EXP-2026-0003")
        contador = {"comparaciones": 0, "intercambios": 0}
        ordenar_expedientes_por_codigo_seleccion(guardar=False, contador=contador)
        self.assertEqual(list(codigos), ["EXP-2026-0001", "EXP-2026-0002", "EXP-2026-0003"])
        self.assertEqual(contador["comparaciones"], 3)           # n(n-1)/2 con n = 3
        self.assertEqual(folios[0], 18)                          # los arreglos siguen sincronizados

    def test_cp16_simulacion_no_altera_el_padron(self):
        # Regresión del defecto del EP: la simulación borraba y duplicaba el padrón real.
        self.registrar_campo()
        with open(datos.ARCHIVO_DATOS, encoding="utf-8") as archivo:
            antes = archivo.read()
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            ejecutar_simulacion_cajamarca()
        with open(datos.ARCHIVO_DATOS, encoding="utf-8") as archivo:
            self.assertEqual(archivo.read(), antes)
        self.assertEqual(len(codigos), 3)
        self.assertTrue(os.path.exists(datos.ARCHIVO_PRUEBAS))

    def test_cp17_actualizar_estado(self):
        self.registrar_campo()
        self.assertTrue(actualizar_estado_expediente("exp-2026-0002", "en evaluacion")[0])
        self.assertEqual(estados[buscar_por_codigo_binaria("EXP-2026-0002")], "EN EVALUACIÓN")
        self.assertFalse(actualizar_estado_expediente("EXP-2026-0002", "EN EVALUACIÓN")[0])
        self.assertTrue(actualizar_estado_expediente("EXP-2026-0002", "ATENDIDO")[0])
        self.assertFalse(actualizar_estado_expediente("EXP-2026-0002", "OBSERVADO")[0])  # final
        self.assertFalse(actualizar_estado_expediente("EXP-2026-0001", "ARCHIVADO")[0])
        self.assertFalse(actualizar_estado_expediente("EXP-2026-0099", "ATENDIDO")[0])

    def test_cp18_persistencia_ida_y_vuelta(self):
        self.registrar_campo()
        actualizar_estado_expediente("EXP-2026-0003", "OBSERVADO")
        for lista in ARREGLOS:
            lista.clear()
        self.assertEqual(cargar_desde_archivo(), 3)
        self.assertEqual(estados[codigos.index("EXP-2026-0003")], "OBSERVADO")
        self.assertEqual(ciudadanos[0], "CHILÓN CHUQUIMANGO, JORGE LUIS")   # UTF-8 conserva tildes

    def test_cp19_linea_danada_se_ignora(self):
        self.registrar_campo()
        with open(datos.ARCHIVO_DATOS, "a", encoding="utf-8") as archivo:
            archivo.write("EXP-2026-0004;DATO;INCOMPLETO\n")
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cargar_desde_archivo(), 3)

    def test_cp20_estado_valido_acepta_minusculas(self):
        self.assertEqual(validar_estado("en evaluación"), (True, "EN EVALUACIÓN"))
        self.assertFalse(validar_estado("pendiente")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
