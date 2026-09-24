# 02 · Reglas y señales sin depender del OCR

**Objetivo:** probar decisiones reproducibles con lecturas construidas. Las prioridades están en `src/placas/reglas.py`; los datos están en `config/`.

## 1. Comprueba los módulos

```bash
python -m pytest tests/test_reglas.py tests/test_senales.py tests/test_plc_simulado.py -v
python -m placas.plc_simulado
```

La segunda orden es una demostración local de consola, no un servidor al que pueda conectarse el HMI.

## 2. Reproduce un escenario controlado

Abre `python` en la terminal y pega:

```python
from datetime import datetime
from placas.configuracion import cargar_reglas, cargar_autorizados, cargar_reportados
from placas.ocr import Lectura
from placas.reglas import decidir
from placas.senales import a_senales, a_modbus

reglas = cargar_reglas("config/reglas.yaml")
autorizados = cargar_autorizados("config/autorizados.csv")
reportados = cargar_reportados("config/reportados.csv")
lectura = Lectura("ABC231", "ABC231", 0.99, True, "carro")
decision = decidir(lectura, datetime(2024, 1, 15, 7, 0), reglas, autorizados, reportados)
print(decision)
print(a_modbus(a_senales(decision, lectura)))
```

Con la configuración incluida, debe resultar `PICO_Y_PLACA`: lunes, dígito 1, placa autorizada sin excepción. Cambia la hora a las 10:00 y repite las dos últimas asignaciones/impresiones: debe resultar `PERMITIDO`.

## 3. Construye la tabla de decisiones

Cambia la lectura y llama de nuevo a `decidir`. Mantén los CSV originales para estos casos.

| Entrada | Fecha/hora | Resultado esperado |
|---|---|---|
| `None` en lugar de lectura | Cualquiera | `SIN_VEHICULO` |
| ABC231, confianza 0.10 | 2024-01-15 07:00 | `LECTURA_DUDOSA` |
| XYZ999, confianza 0.99 | 2024-01-15 07:00 | `REPORTADO` |
| ZZZ888, confianza 0.99 | 2024-01-15 07:00 | `NO_AUTORIZADO` |
| ABC231, confianza 0.99 | 2024-01-15 07:00 | `PICO_Y_PLACA` |
| ABC231, confianza 0.99 | 2024-01-15 10:00 | `PERMITIDO` |

Para cada placa usa el mismo texto en los dos primeros campos de `Lectura` y formato válido. El caso sin vehículo se prueba pasando `None` directamente.

## 4. Relaciona decisión y señal

Consulta el [mapa Modbus](../modbus.md). Identifica el coil de acceso permitido, el código de decisión y la confianza escalada. Una confianza de 0.99 se representa como 990.

**Reto:** prueba ABC231 a las 08:59 y 09:00 del mismo lunes. El inicio del horario se incluye y el final se excluye. Agrega una prueba para una nueva regla antes de cambiarla.

**Criterio para avanzar:** registra los seis resultados, sus coils y explica por qué la prioridad de reportados va antes de autorizados.

[Anterior](01-vision.md) · [Siguiente: interfaz](03-interfaz.md)
