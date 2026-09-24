# Clase Fase 10 — Comunicación Modbus TCP

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante entiende la relación cliente/servidor en Modbus TCP, sabe qué código de función corresponde a cada operación (leer/escribir, uno/varios), y puede capturar y leer tráfico Modbus real con Wireshark.

## Conceptos

- **Cliente y servidor en Modbus**: el sistema de visión es el cliente (inicia la conexión y las peticiones); el PLC es el servidor (responde, nunca inicia). Esto es al revés de lo que muchos esperan intuitivamente ("el PLC manda"), y vale la pena remarcarlo.
- **Coils y holding registers**: los coils son bits de lectura/escritura; los holding registers son palabras de 16 bits de lectura/escritura. Ambos existen en un espacio de direcciones separado (coil 0 y holding register 0 son direcciones distintas, no la misma).
- **Códigos de función**: cada operación Modbus tiene un número que la identifica en el paquete (01 leer coils, 03 leer registros, 05/06 escribir un solo coil/registro, 15/16 escribir varios); ver `docs/modbus.md`.
- **Reconexión y manejo de errores**: una interfaz de operador no debe congelarse ni caerse si el PLC se desconecta; debe reintentar con un límite razonable y mostrar el problema, no ocultarlo ni bloquear la aplicación.
- **Watchdog en un hilo aparte**: incrementar el watchdog en un hilo independiente (`threading.Thread`) permite seguir "avisando que estamos vivos" aunque el hilo principal esté ocupado procesando una imagen.

## Demostración paso a paso

```bash
pytest tests/test_comunicacion.py -v

# Terminal 1
python -m hmi.servidor_prueba --puerto 5020

# Terminal 2
streamlit run app/interfaz.py
# barra lateral -> destino "Modbus TCP" (edite config/reglas.yaml -> plc.puerto a 5020 para esta prueba local)
```

Capturar con Wireshark (filtro `tcp.port == 5020`) mientras se procesa una imagen desde la interfaz, y mostrar en vivo los paquetes con función 15 (coils) y 16 (registros).

## Preguntas de verificación

1. **¿Por qué el sistema de visión es el cliente Modbus y el PLC el servidor, y no al revés?**
   Respuesta: porque el PLC debe estar siempre disponible para recibir señales de quien sea que este vigilando el acceso, sin depender de iniciar conexiones el mismo; el cliente (sistema de visión) es quien decide cuándo hay algo nuevo que enviar, y por eso inicia la comunicación.

2. **¿Qué pasa si `ClienteModbusAcceso.enviar()` no pudiera fallar de forma controlada (por ejemplo, si dejara propagar la excepción de conexión)?**
   Respuesta: la interfaz completa se caería cada vez que el PLC estuviera apagado o inaccesible, en vez de simplemente mostrar un aviso y seguir funcionando (por ejemplo, para seguir revisando imágenes o cambiar de destino).

3. **¿Por qué el watchdog corre en un hilo aparte en vez de incrementarse solo cuando se procesa una imagen?**
   Respuesta: porque si el sistema de visión tarda en procesar una imagen (por ejemplo, el OCR), el PLC necesita seguir viendo que el watchdog cambia para no declarar una falla de comunicación falsa; un hilo aparte garantiza que el watchdog se actualice a un ritmo constante, independiente de cuánto tarde el resto del pipeline.

## Reto para estudiantes

Capturar el tráfico con Wireshark e identificar los códigos de función 05, 06, 15 y 16 en una sesión completa (sistema de visión + PLC + alguna herramienta que escriba puntos individuales, como el forzado de E/S de OpenPLC en la Fase 11).

**Criterios de evaluación:**
- Se entrega una captura (o al menos capturas de pantalla de Wireshark) mostrando al menos un paquete de cada uno de los cuatro códigos de función.
- Para cada código encontrado, se identifica correctamente qué programa lo generó y por qué (no basta con decir "Modbus lo hizo").
- Se explica la diferencia entre "escribir un solo punto" (05/06) y "escribir varios de una vez" (15/16) con un ejemplo concreto de la captura.

---

[Fase anterior](fase09.md) · [Índice de guías](../README.md) · [Fase siguiente](fase11.md)
