# Modbus TCP: direcciones, códigos de función y cómo verlos en Wireshark

El sistema de visión es el **cliente** Modbus TCP; el PLC (o, para pruebas, `hmi/servidor_prueba.py`) es el **servidor**. Ver `ENUNCIADO.md` para el detalle de cada señal.

## Direcciones

| Tipo | Dirección | Nombre | Notas |
|---|---|---|---|
| Coil | 0 | `vehiculo_presente` | |
| Coil | 1 | `acceso_permitido` | |
| Coil | 2 | `acceso_denegado` | |
| Coil | 3 | `lectura_dudosa` | |
| Coil | 4 | `nueva_lectura` | Pulso; el PLC lo pone en 0 como acuse |
| Holding | 0 | `codigo_decision` | Entero 0-5 |
| Holding | 1 | `confianza` | Entero 0-1000 (confianza OCR x 1000) |
| Holding | 2 | `ultimo_digito` | Entero 0-9 |
| Holding | 3 | `watchdog` | El sistema de vision lo incrementa cada segundo |

Estas direcciones son "de protocolo" (empiezan en 0). `src/placas/comunicacion.py` las usa directamente; `hmi/servidor_prueba.py` configura su `ModbusSlaveContext` con `zero_mode=True` para que la dirección 0 del protocolo sea la dirección 0 del bloque de datos, sin el desplazamiento +1 histórico de Modbus.

## Códigos de función usados

`src/placas/comunicacion.py` siempre agrupa sus escrituras (coils juntos, registros juntos), así que genera FC15 y FC16, nunca FC05/06 por sí solo:

| Código | Nombre | Quién lo usa | Para qué |
|---|---|---|---|
| 15 (0x0F) | Write Multiple Coils | `ClienteModbusAcceso.enviar()` | Escribe los 5 coils de una vez |
| 16 (0x10) | Write Multiple Registers | `ClienteModbusAcceso.enviar()` (incluye el watchdog, que se escribe como una lista de un solo registro) | Escribe los holding registers |
| 01 | Read Coils | `ClienteModbusAcceso.leer_acuse()` | Lee el coil 4 para saber si el PLC ya proceso la lectura |
| 03 | Read Holding Registers | Un cliente externo (HMI de la Fase 12) | Lee los registros para supervisión |

Los códigos **05** (Write Single Coil) y **06** (Write Single Register) no los genera este cliente Python (siempre escribe en grupo). Suelen aparecer cuando otra herramienta Modbus escribe un solo punto a la vez: por ejemplo, el panel de forzado de E/S del web server de OpenPLC (Fase 11), o una utilidad de prueba como `mbpoll` escribiendo un coil individual. Parte del reto de Wireshark de esta fase es, precisamente, identificar de dónde sale cada código de función que aparezca en la captura — no asuma que todo el tráfico viene del mismo programa.

## Cómo probarlo sin un PLC real

```bash
# Terminal 1: servidor de prueba (imprime cada escritura que recibe)
python -m hmi.servidor_prueba --puerto 5020   # puertos <1024 (como el 502 real) requieren sudo en Linux

# Terminal 2: la interfaz, apuntando config/reglas.yaml -> plc.puerto a 5020 para esta prueba
streamlit run app/interfaz.py
# en la barra lateral, elegir destino "Modbus TCP"
```

## Cómo verlo en Wireshark

1. Inicie una captura en la interfaz de red por la que viaja el tráfico (`lo` si cliente y servidor están en la misma máquina).
2. Filtro de captura o de visualización: `modbus` (si Wireshark reconoce el protocolo) o, como alternativa más genérica, `tcp.port == 502` (o el puerto que se esté usando, por ejemplo `tcp.port == 5020` en las pruebas locales).
3. Con el destino "Modbus TCP" activo en la interfaz, cada imagen procesada genera al menos dos paquetes de escritura: uno con código de función 15 (coils) y otro con 16 (registros). Puede confirmarlo mirando el campo `Function Code` que Wireshark decodifica dentro de cada paquete Modbus/TCP.
4. El watchdog, si está activo (`ClienteModbusAcceso.iniciar_watchdog`), genera un paquete adicional con función 16 cada `periodo_watchdog_s` segundos, incluso sin procesar ninguna imagen nueva.

## Nota de versión de `pymodbus`

`requirements.txt` fija `pymodbus>=3.6,<3.8`. Versiones más nuevas (probadas hasta la 3.15) reescribieron el `datastore` (`ModbusSequentialDataBlock`/`ModbusSlaveContext` cambiaron de forma incompatible: direcciones 1-based internamente, nuevos nombres como `ModbusDeviceContext`, parámetro `device_id` en vez de `slave`). Si necesita usar una versión más nueva, revise la documentación de esa versión antes de adaptar `src/placas/comunicacion.py` y `hmi/servidor_prueba.py`.
