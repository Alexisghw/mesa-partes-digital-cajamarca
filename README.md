# Sistema de Mesa de Partes Digital — Municipalidad Distrital de Los Baños del Inca (Cajamarca)

**Curso:** Fundamentos de Programación (CIIN1205P) — Universidad Privada del Norte (UPN) - Sede Cajamarca  
**Docente:** Ing. Edwuard Jhonatan Pereda Cabanillas  
**Normativa:** Ley N.° 31170 y Decreto Legislativo N.° 1412 (Ley de Gobierno Digital)

## Descripción del Proyecto
Prototipo funcional en **Python 3** que registra, valida, busca (binaria por código y secuencial por DNI/RUC), ordena (Burbuja Mejorado sobre 8 arreglos paralelos) y guarda de forma permanente en un archivo CSV los trámites que ingresan a la Mesa de Partes de la Municipalidad Distrital de Los Baños del Inca, Cajamarca.

## Estructura Modular
| Archivo | Módulo | Contenido |
|---|---|---|
| `datos.py` | 1 | Constantes (archivos, áreas, estados) y los 8 arreglos paralelos |
| `validacion.py` | 2 | Validación de DNI/RUC, nombre, asunto y folios; generación del código `EXP-2026-XXXX` |
| `persistencia.py` | 3 | Guardar y cargar el CSV (UTF-8) y bitácora de auditoría `.log` |
| `algoritmos.py` | 4 | Inserción, intercambio sincronizado, Burbuja Mejorado, búsqueda binaria y secuencial |
| `pruebas.py` | 5 | Simulación automática con los trámites de prueba de la práctica de campo |
| `interfaz.py` | 6 | Menú interactivo por teclado |
| `main.py` | — | Punto de entrada del programa |

## Cómo ejecutar
Requiere Python 3.10 o superior (sin librerías externas).

```bash
python main.py          # menú interactivo (uso normal)
python main.py --auto   # simulación automática de pruebas
```

- Los expedientes se guardan en `expedientes_cajamarca.csv` después de cada registro y se cargan al iniciar el programa.
- La simulación de pruebas no modifica el padrón real: su resultado queda en `expedientes_prueba.csv`.
