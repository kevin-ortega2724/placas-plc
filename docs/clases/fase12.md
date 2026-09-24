# Clase Fase 12 — HMI de solo lectura

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante entiende por qué separar la supervisión (HMI) del control (PLC/interfaz) es una práctica de seguridad, no solo de organización de código, y puede construir un panel de monitoreo que se actualiza periódicamente y deja un histórico.

## Conceptos

- **Separación de responsabilidades**: el HMI de esta fase (`hmi/monitor.py`) solo *lee* del PLC; nunca escribe. Esto significa que, aunque el HMI tenga un error o se cuelgue, no puede corromper el estado del PLC ni abrir la talanquera por accidente.
- **Supervisión vs. control**: el control (decidir y actuar) vive en la interfaz y el PLC; la supervisión (mostrar qué está pasando) vive en el HMI. Son procesos independientes que pueden correr en máquinas distintas.
- **Registro histórico**: guardar cada lectura en un CSV permite reconstruir qué pasó después del hecho (auditoría), no solo ver el estado actual.
- **Actualización periódica en Streamlit**: `st.fragment(run_every="0.5s")` vuelve a ejecutar solo esa porción de la página cada 500 ms, sin recargar toda la interfaz ni perder el estado de otros controles.

## Demostración paso a paso

```bash
pytest tests/test_monitor.py -v

# Terminal 1
python -m hmi.servidor_prueba --puerto 5020

# Terminal 2 (simula al PLC escribiendo sus salidas, para la demo)
python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('127.0.0.1', port=5020); c.connect()
c.write_coils(8, [True, False, False, False], slave=1)
c.write_registers(0, [5, 950], slave=1)
c.write_registers(10, [1, 0], slave=1)
"

# Terminal 3
streamlit run hmi/monitor.py
# barra lateral: puerto 5020
```

Mostrar en vivo cómo, si se detiene `hmi/servidor_prueba.py`, el monitor muestra de inmediato "Sin conexión con el PLC" en vez de congelarse o mostrar datos viejos sin avisar.

## Preguntas de verificación

1. **¿Por qué el HMI de esta fase nunca debe escribir en el PLC, ni siquiera para una función aparentemente inofensiva como "silenciar una alarma"?**
   Respuesta: porque en el momento en que el HMI puede escribir, deja de ser puramente un panel de supervisión y se convierte en otro punto desde el que se puede afectar el comportamiento del sistema de control; cualquier error en el HMI (un bug, una mala conexión) ahora podría alterar la talanquera o los contadores, no solo mostrar información incorrecta.

2. **¿Qué garantiza `st.fragment(run_every="0.5s")` que no garantizaría simplemente poner un `time.sleep(0.5)` dentro del script principal?**
   Respuesta: el fragmento vuelve a ejecutar solo esa parte de la página cada 500 ms sin bloquear ni recargar el resto de la interfaz (por ejemplo, los controles de la barra lateral); un `time.sleep` en el script principal congelaría toda la aplicación durante esa espera.

3. **Si el histórico solo guarda el valor acumulado de `contador_ingresos` (no un evento por cada ingreso), ¿cómo se calculan los ingresos de una hora específica?**
   Respuesta: restando el valor máximo del contador al final de esa hora menos el valor máximo al final de la hora anterior; como el contador nunca decrece, esa diferencia es exactamente el número de ingresos ocurridos durante esa hora.

## Reto para estudiantes

Guardar un histórico en CSV y graficar ingresos por hora (si aún no lo ha probado con datos reales) usando datos de varias horas distintas, y agregar una segunda gráfica de rechazos por hora para comparar patrones.

**Criterios de evaluación:**
- La gráfica de ingresos por hora coincide con un conteo manual verificado sobre el CSV crudo (no solo "se ve razonable").
- Se agrega una gráfica equivalente para `contador_rechazos`.
- El HMI sigue sin escribir ningún coil ni registro (verificable revisando que no se usen `write_coils`/`write_registers` en `hmi/monitor.py`).
