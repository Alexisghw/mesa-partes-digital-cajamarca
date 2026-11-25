# Sistema de Mesa de Partes Digital — Municipalidad Distrital de Los Baños del Inca (Cajamarca)

**Curso:** Fundamentos de Programación (CIIN1205P) — Universidad Privada del Norte (UPN) - Sede Cajamarca  
**Docente:** Ing. Edwuard Jhonatan Pereda Cabanillas  
**Normativa:** Ley N.° 31170 y Decreto Legislativo N.° 1412 (Ley de Gobierno Digital)

## Descripción del Proyecto
Prototipo funcional en **Python 3** que registra, valida, busca (binaria iterativa y recursiva por código, secuencial por DNI/RUC), actualiza el estado, ordena (Burbuja Mejorado y Selección sobre 8 arreglos paralelos) y guarda de forma permanente en una base de datos SQLite los trámites que ingresan a la Mesa de Partes de la Municipalidad Distrital de Los Baños del Inca, Cajamarca.

## Estructura Modular
| Archivo | Módulo | Contenido |
|---|---|---|
| `datos.py` | 1 | Constantes (archivos, áreas, estados) y los 8 arreglos paralelos |
| `validacion.py` | 2 | Validación de DNI/RUC, nombre, asunto, folios, área (1–6) y estado; clave de orden sin tildes; código `EXP-AAAA-XXXX` |
| `persistencia.py` | 3 | Base de datos SQLite (consultas parametrizadas, restricciones CHECK), migración desde CSV, exportación a Excel y bitácora `.log` |
| `algoritmos.py` | 4 | Inserción, actualización de estado, Burbuja Mejorado, Selección, búsqueda binaria y secuencial |
| `pruebas.py` | 5 | Simulación automática con los trámites de la práctica de campo (no modifica el padrón real) |
| `interfaz.py` | 6 | Menú interactivo por teclado (una función por opción) |
| `recursividad.py` | 7 | Búsqueda binaria recursiva, suma y conteo recursivos, tabla iterativa vs. recursiva |
| `analisis.py` | 8 | Conteo de comparaciones e intercambios: Burbuja Mejorado vs. Selección |
| `tests/test_mesa_partes.py` | — | 24 pruebas automáticas (CP-01 a CP-24) con `unittest` |
| `main.py` | — | Punto de entrada del programa |

## Cómo ejecutar
Requiere Python 3.10 o superior (sin librerías externas).

```bash
python main.py          # menú interactivo (uso normal)
python main.py --auto   # simulación automática de pruebas
python -m unittest discover -s tests -v   # pruebas automáticas CP-01 a CP-24
```

### Menú
| Opción | Acción |
|---|---|
| 1 | Registrar expediente (área de destino del 1 al 6) |
| 2 | Buscar por código (binaria iterativa; muestra también la recursiva) |
| 3 | Buscar por DNI/RUC (secuencial) |
| 4 | Actualizar estado: REGISTRADO, EN EVALUACIÓN, OBSERVADO, ATENDIDO (ATENDIDO es final) |
| 5 | Listar ordenado por código |
| 6 | Listar ordenado por ciudadano (respeta tildes y Ñ) |
| 7 | Reporte de folios y estados con funciones recursivas |
| 8 | Comparar algoritmos: iterativo vs. recursivo y Burbuja vs. Selección |
| 9 | Simulación automática (7 fases, incluye intentos de inyección SQL) |
| 10 | Exportar el padrón a CSV para Excel |
| 0 | Salir |

- Los expedientes se guardan en la base SQLite `mesa_partes.db` en cada registro y cambio de estado, y se cargan al iniciar.
- La primera ejecución migra a SQLite el padrón del EP (`expedientes_cajamarca.csv`), validando cada fila.
- La simulación corre en una base aparte (`mesa_partes_prueba.db`): la base real nunca se abre.
- La opción 10 exporta el padrón a `expedientes_exportados.csv` para Excel, neutralizando fórmulas (=, +, -, @).

### Seguridad
- **Inyección SQL:** todas las consultas usan parámetros `?`; un nombre como `Robert'); DROP TABLE expedientes; --` se guarda como texto (pruebas CP-21 y CP-22).
- **Restricciones de la base:** `CHECK` sobre DNI/RUC, folios (1–500), estado, área y formato del código (CP-23).
- **Inyección CSV:** la exportación antepone un apóstrofo a los textos que Excel tomaría como fórmula (CP-24).
