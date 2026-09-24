# Clase Fase 07 — Reglas de acceso (pico y placa)

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede implementar una cadena de decisión con prioridades explícitas, entiende por qué la fecha y la hora deben ser parámetros de entrada (nunca `datetime.now()`) en lógica que se necesita probar, y sabe manejar límites de horario correctamente (inclusivo/exclusivo).

## Conceptos

- **Lógica de decisión con prioridades**: se evalúan condiciones en un orden fijo y se toma la primera que aplique; el orden importa (por ejemplo, `REPORTADO` se revisa antes que `NO_AUTORIZADO`, así que una placa reportada nunca llega a evaluarse como "no autorizada").
- **Tablas de verdad**: cada combinación de (¿hay lectura?, ¿confianza suficiente?, ¿reportada?, ¿autorizada?, ¿pico y placa?) mapea a exactamente un código de decisión.
- **Festivos**: la librería `holidays` calcula los días festivos de un país (`pais_festivos` en config) sin necesidad de mantener una lista manual que se desactualice cada año.
- **Pruebas con fecha simulada**: pasar `fecha_hora` como parámetro permite probar un lunes festivo, un sábado o las 8:59 a.m. exactas sin esperar a que ocurra de verdad — esencial para poder automatizar las pruebas.
- **Límites inclusivo/exclusivo**: el horario de pico y placa es `[inicio, fin)` — las 09:00 en punto ya NO están restringidas, aunque las 08:59 sí. Estos límites son la fuente más común de errores "por un minuto" en este tipo de reglas.

## Demostración paso a paso

```bash
pytest tests/test_reglas.py -v
```

Mostrar en vivo, con una sesión de Python, cómo cambia la decisión para la misma placa (`ABC231`, autorizada, último dígito 1) según la fecha:

```python
from datetime import datetime
from placas.configuracion import cargar_reglas, cargar_autorizados, cargar_reportados
from placas.ocr import Lectura
from placas.reglas import decidir

reglas = cargar_reglas("config/reglas.yaml")
autorizados = cargar_autorizados("config/autorizados.csv")
reportados = cargar_reportados("config/reportados.csv")
lectura = Lectura("ABC231", "ABC231", 0.95, True, "carro")

decidir(lectura, datetime(2024, 1, 15, 7, 0), reglas, autorizados, reportados)  # lunes normal
decidir(lectura, datetime(2024, 1, 1, 7, 0), reglas, autorizados, reportados)   # lunes festivo
decidir(lectura, datetime(2024, 1, 15, 9, 0), reglas, autorizados, reportados)  # fin del horario
```

## Preguntas de verificación

1. **¿Por qué `REPORTADO` se evalúa antes que `NO_AUTORIZADO` y no al revés?**
   Respuesta: porque una placa reportada por seguridad debe negarse siempre, incluso si además no está en la lista de autorizados; el orden garantiza que el motivo reportado en la decisión sea el correcto (más grave) y no se pierda detrás de un motivo genérico de "no autorizado".

2. **¿Por qué la función `decidir` recibe `fecha_hora` como parámetro en vez de calcularla con `datetime.now()` internamente?**
   Respuesta: para poder probar cualquier día y hora de forma determinista con pytest. Si la función usara `datetime.now()`, las pruebas dependerían del momento en que se ejecutan (y una prueba que hoy pasa podría fallar un sábado, o nunca poder probar un festivo específico).

3. **¿Qué decisión toma el sistema a las 09:00:00 en punto para una placa restringida ese día, y por qué no es `PICO_Y_PLACA`?**
   Respuesta: `PERMITIDO`, porque el horario configurado es `[06:00, 09:00)` con el fin exclusivo: a las 09:00 en punto la hora ya no es menor que el fin, así que la condición de horario deja de cumplirse exactamente en ese instante.

## Reto para estudiantes

Agregar la regla: "los vehículos con excepción solo pueden entrar en pico y placa si además están en la lista de autorizados" (hoy la excepción ya implica estar autorizado, porque el chequeo de excepción ocurre después del de `NO_AUTORIZADO`; el reto es escribir la prueba que deja esto explícito y a prueba de futuros cambios).

**Criterios de evaluación:**
- Se agrega una prueba parametrizada que verifique que una placa con excepción pero que NO está en `autorizados.csv` recibe `NO_AUTORIZADO`, no `PERMITIDO`.
- La prueba falla si alguien reordena las condiciones de `decidir` de forma incorrecta (es decir, protege el orden de prioridades).
- El resto de las pruebas de `test_reglas.py` sigue pasando.

---

[Fase anterior](fase06.md) · [Índice de guías](../README.md) · [Fase siguiente](fase08.md)
