# Clase Fase 06 — Evaluación del sistema de visión

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede distinguir exactitud por carácter de exactitud por placa completa, leer una matriz de confusión de caracteres, y usar mediciones reales de tiempo por etapa para argumentar dónde optimizar un pipeline de visión.

## Conceptos

- **Verdad de terreno (ground truth)**: `etiquetas.csv` (Fase 01) es la referencia contra la que se compara todo lo que lee el sistema; sin ella no hay forma objetiva de medir exactitud.
- **Exactitud por placa completa vs. por carácter**: la primera es estricta (todo o nada); la segunda es más fina y permite ver "qué tan cerca" estuvo una lectura incorrecta.
- **Matriz de confusión de caracteres**: para cada posición, cuenta qué carácter se leyó en vez de cuál. La diagonal son aciertos; fuera de la diagonal quedan los errores sistemáticos (por ejemplo, muchas "O" leídas como "0").
- **Tiempo medio por etapa**: agregar los tiempos de `pipeline.py` sobre muchas imágenes da una medición confiable (no anecdótica) de dónde se concentra el costo de procesamiento.
- **Agrupar por tipo de degradación**: comparar la exactitud entre subconjuntos del dataset (por ejemplo, según el kernel de desenfoque) permite formular hipótesis del tipo "el sistema falla más con desenfoque fuerte" y comprobarlas con datos.

## Demostración paso a paso

```bash
python -m placas.generador --n 200 --semilla 42
python -m placas.evaluacion
# revisar salidas/evaluacion.csv y salidas/confusiones.png

jupyter notebook notebooks/06_evaluacion.ipynb
```

El cuaderno carga `salidas/evaluacion.csv` y guía el análisis con preguntas (no respuestas): localización, exactitud por placa/carácter, tiempo por etapa, exactitud agrupada por desenfoque, y la matriz de confusión.

## Preguntas de verificación

1. **Si la exactitud por carácter es alta (por ejemplo, 95 %) pero la exactitud por placa completa es baja (por ejemplo, 60 %), ¿qué le dice eso sobre el patrón de los errores?**
   Respuesta: que los errores están distribuidos entre muchas placas distintas (cada una con uno o dos caracteres mal leídos) en vez de concentrarse en unas pocas placas totalmente ilegibles. Cada error, aunque pequeño, basta para que la placa completa no coincida.

2. **¿Por qué agrupar la exactitud por `desenfoque_kernel` es más informativo que reportar solo un promedio general?**
   Respuesta: porque el promedio general esconde diferencias importantes; si la exactitud cae mucho con desenfoque fuerte pero se mantiene alta con desenfoque leve, esa es información accionable (mejorar el preprocesamiento o el enfoque de la cámara), que un solo número no revela.

3. **La matriz de confusión muestra que "O" se lee frecuentemente como "0". ¿Por qué esa confusión en particular ya debería estar resuelta por `config/reglas.yaml`, y qué significa si sigue apareciendo en el reporte?**
   Respuesta: porque `correcciones.a_numero` ya mapea "O" → "0" para las posiciones numéricas. Si la confusión sigue apareciendo, puede ser porque ocurre en una posición donde se esperan letras (donde no se debe corregir) o porque la corrección no se está aplicando correctamente; vale la pena revisar en qué posición ocurre antes de agregar más reglas.

## Reto para estudiantes

Identificar las tres confusiones de caracteres más frecuentes en `salidas/confusiones.png` y proponer una corrección concreta (una regla nueva en `config/reglas.yaml`, un ajuste de preprocesamiento o de localización).

**Criterios de evaluación:**
- Se listan las tres confusiones más frecuentes con su conteo exacto (leído de la matriz).
- La propuesta de corrección está justificada con los datos del cuaderno (no solo intuición) y considera el riesgo de introducir falsos positivos.
- Se vuelve a correr `python -m placas.evaluacion` después del cambio y se compara la exactitud antes/después.

---

[Fase anterior](fase05.md) · [Índice de guías](../README.md) · [Fase siguiente](fase07.md)
