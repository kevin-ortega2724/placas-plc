# 05 · Control PLC y supervisión independiente

**Objetivo:** comprobar salidas decididas por el PLC y leerlas desde el HMI. Necesitas OpenPLC preparado o un servidor equivalente que ejecute la lógica y exponga el mismo mapa. El servidor de prueba del tutorial 04 solo permite comprobar comunicación.

## 1. Prepara el programa de control

1. Sigue la [guía ladder](../../plc/openplc/ladder_paso_a_paso.md) y revisa [control_acceso.st](../../plc/openplc/control_acceso.st).
2. Compila y carga el programa en tu Runtime.
3. Verifica el [mapa Modbus del PLC](../../plc/openplc/mapa_modbus.md) contra la versión instalada. Confirma las direcciones antes de interpretar estados.
4. Apaga el servidor de prueba si ocupa el mismo puerto. Ajusta el host/puerto de la interfaz al Runtime.

## 2. Mantén el watchdog durante la prueba

La interfaz actual abre y cierra una conexión por envío. Para probar la lógica PLC con una conexión persistente, abre una sesión `python` y ejecuta:

```python
from datetime import datetime
from placas.comunicacion import ClienteModbusAcceso
from placas.configuracion import cargar_reglas, cargar_autorizados, cargar_reportados
from placas.ocr import Lectura
from placas.reglas import decidir
from placas.senales import a_senales

reglas = cargar_reglas("config/reglas.yaml")
cliente = ClienteModbusAcceso(reglas.plc.host, reglas.plc.puerto, reglas.plc.unidad)
assert cliente.conectar(), "Verifica host, puerto y Runtime"
cliente.iniciar_watchdog(reglas.plc.periodo_watchdog_s)
lectura = Lectura("ABC231", "ABC231", 0.99, True, "carro")
decision = decidir(lectura, datetime(2024, 1, 15, 10, 0), reglas,
                   cargar_autorizados("config/autorizados.csv"),
                   cargar_reportados("config/reportados.csv"))
print(cliente.enviar(a_senales(decision, lectura)))
```

Mantén esta sesión abierta mientras observas el PLC. No envíes simultáneamente desde la interfaz: usa un solo emisor durante el ensayo. Al terminar ejecuta `cliente.detener()` y observa la detección de pérdida de comunicación. Consulta `src/placas/comunicacion.py` para la implementación del watchdog y del acuse.

## 3. Abre el monitor (otra terminal)

```bash
python -m streamlit run hmi/monitor.py --server.port 8502
```

Abre `http://localhost:8502`. Introduce el host, puerto y unidad del PLC en la barra lateral del monitor. El HMI usa sus propios controles de conexión. Lee coils 8–11 y registros 10–11 para salidas y contadores; el Runtime debe exponer esas direcciones o debes adaptar el mapa.

**Resultado esperado con un PLC funcional:** las lámparas reflejan sus salidas, el contador cambia después de una nueva lectura válida y se genera `salidas/historico.csv`. Con el servidor de prueba, salidas y contadores pueden permanecer en cero: eso no demuestra una falla del monitor.

## 4. Ejecuta el protocolo

Completa las pruebas de [talanquera, rechazo, validación, watchdog y emergencia](../../plc/openplc/pruebas.md). Registra esperado, obtenido y evidencia por paso. Usa el emisor persistente cuando el escenario requiera watchdog activo.

```bash
python -m pytest tests/test_plc_simulado.py tests/test_comunicacion.py tests/test_monitor.py -q
```

Estas pruebas no certifican el cableado, el mapeo ni el Runtime de tu instalación.

**Reto:** explica qué lecturas permitirían detectar un reinicio del contador antes de calcular ingresos por hora.

**Criterio para avanzar:** comprobaste el mapa, un ingreso, un rechazo y una pérdida de comunicación en el PLC. Si no tienes Runtime, reporta la práctica como pendiente y entrega por separado la simulación local y el ensayo de transporte.

[Anterior](04-modbus.md) · [Siguiente: entrega](06-proyecto-final.md)
