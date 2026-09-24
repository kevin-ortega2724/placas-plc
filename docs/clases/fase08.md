# Clase Fase 08 — De la decisión a las señales

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede traducir una decisión lógica a variables digitales y analógicas concretas, entiende los conceptos de *handshake* y *watchdog* en comunicación PLC-supervisor, y puede leer/escribir lógica de PLC simulada estructurada como renglones de ladder.

## Conceptos

- **Variables digitales (coils) y analógicas (holding registers)**: los coils son bits (sí/no); los registros guardan números (código de decisión, confianza, dígito, contador).
- **Escalado**: la confianza del OCR (0.0 a 1.0) se guarda como entero de 0 a 1000 porque los registros Modbus son enteros; escalar evita perder precisión al truncar decimales.
- **Handshake (protocolo de apretón de manos)**: `nueva_lectura` se pone en 1 cuando hay un resultado nuevo, y el receptor (el PLC) lo pone en 0 como acuse de recibo — así el emisor sabe que el dato ya fue procesado y no lo reenvía indefinidamente.
- **Watchdog**: un contador que una parte incrementa periódicamente para probar que sigue viva; si la otra parte deja de ver cambios durante un tiempo (aquí, 3 s), asume que se perdió la comunicación y actúa en consecuencia (alarma, talanquera cerrada).
- **Ladder como una función por renglón**: cada "renglón" de la lógica del ENUNCIADO se implementa como un método independiente (`_renglon_1_abrir_talanquera`, etc.), para que la correspondencia con el diagrama ladder de la Fase 11 sea directa.

## Demostración paso a paso

```bash
pytest tests/test_senales.py tests/test_plc_simulado.py -v

python -m placas.plc_simulado
```

Mostrar en vivo, con una sesión de Python, cómo cambian las señales según el código de decisión:

```python
from placas.reglas import CodigoDecision, Decision
from placas.senales import a_senales, a_modbus

decision = Decision(CodigoDecision.PICO_Y_PLACA, "PICO_Y_PLACA", "digito restringido", 1)
senales = a_senales(decision, None)  # lectura ya se uso para decidir, aqui solo importan las senales
coils, registros = a_modbus(senales)
print(coils, registros)
```

## Preguntas de verificación

1. **¿Por qué la confianza se escala a un entero de 0 a 1000 en vez de enviarse como decimal?**
   Respuesta: porque los holding registers de Modbus son enteros de 16 bits; no existe un tipo "decimal" nativo en el protocolo. Escalar por 1000 conserva tres cifras decimales de precision sin necesitar un tipo de dato adicional.

2. **¿Qué pasaría si el PLC nunca pusiera `nueva_lectura` en 0 después de procesarla?**
   Respuesta: el sistema de vision no tendría forma de saber si el PLC ya proceso la lectura o no; si se implementara un reenvío basado en ese acuse, se reenviaría la misma lectura indefinidamente, o el sistema de vision no sabría cuándo es seguro enviar la siguiente lectura.

3. **¿Por qué el watchdog lo incrementa el sistema de vision y lo vigila el PLC, y no al revés?**
   Respuesta: porque quien decide si abrir o no la talanquera (el PLC) es quien necesita saber si todavía hay un sistema de vision funcionando del otro lado antes de confiar en sus señales. Si el sistema de vision se cae, el PLC debe notarlo y bloquear la talanquera por seguridad, no al revés.

## Reto para estudiantes

Agregar un registro con el número de lecturas consecutivas de la misma placa (antirrebote): si la misma placa se lee varias veces seguidas (por ejemplo, porque el vehículo tarda en pasar), no debería contar como varios ingresos distintos.

**Criterios de evaluación:**
- Se agrega un campo a `Senales` (por ejemplo `lecturas_consecutivas`) y su holding register correspondiente en `a_modbus`.
- `plc_simulado.py` solo incrementa `contador_ingresos` en la primera lectura de una racha, no en las repeticiones de la misma placa.
- Se agrega una prueba que verifique que 3 lecturas seguidas de la misma placa cuentan como 1 solo ingreso.
