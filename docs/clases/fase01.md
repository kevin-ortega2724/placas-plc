# Clase Fase 01 — Generador de placas sintéticas

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante entiende qué son los datos sintéticos y la verdad de terreno (*ground truth*), por qué se usan cuando hay restricciones de privacidad, y qué es el aumento de datos (*data augmentation*) y para qué sirve en visión por computador.

## Conceptos

- **Datos sintéticos**: imágenes generadas por software en vez de capturadas de la realidad. Permiten controlar exactamente qué contienen y evitan exponer datos personales.
- **Verdad de terreno (ground truth)**: la etiqueta correcta conocida de antemano (aquí, la placa real de cada imagen, guardada en `etiquetas.csv`). Sin verdad de terreno no se puede medir qué tan bien lee el sistema.
- **Aumento de datos**: transformaciones aleatorias que simulan condiciones reales de captura, para que el sistema se entrene o se pruebe contra casos difíciles:
  - Ruido gaussiano: `I'(x, y) = I(x, y) + N(0, σ²)` — simula ruido del sensor de la cámara.
  - Brillo y contraste: `I' = α·I + β` — simula distintas condiciones de luz.
  - Rotación y perspectiva: simulan que la cámara y la placa no están perfectamente alineadas.
- **Reproducibilidad con semillas**: fijar la semilla de un generador de números aleatorios (`numpy.random.default_rng(semilla)`) hace que la misma orden produzca siempre el mismo resultado.

## Demostración paso a paso

```bash
# Muestra rapida (20 imagenes) para revisar visualmente
python -m placas.generador --n 20 --semilla 42
# abrir un par de archivos de data/sinteticas/ para revisarlos

# Dataset completo para las siguientes fases
python -m placas.generador --n 200 --semilla 42
cat data/sinteticas/etiquetas.csv | head
```

Mostrar en vivo que correr el mismo comando dos veces (con la misma semilla) genera exactamente las mismas placas y los mismos parámetros de degradación — y que cambiar la semilla cambia el dataset.

## Preguntas de verificación

1. **¿Por qué generar placas sintéticas en vez de usar placas reales de vehículos de los estudiantes?**
   Respuesta: la placa es un dato personal asociado a un vehículo; usar placas sintéticas evita exponer esa información y además da una verdad de terreno exacta y controlada para medir la exactitud del sistema desde el principio.

2. **¿Qué papel cumple `--semilla 42` en el generador?**
   Respuesta: fija el estado interno del generador de números aleatorios para que el mismo comando produzca siempre el mismo dataset. Esto permite comparar resultados entre estudiantes o entre corridas distintas del mismo experimento.

3. **Si se aumenta mucho la intensidad del ruido gaussiano (`ruido_sigma`), ¿qué se espera que pase con la exactitud del OCR en la Fase 05?**
   Respuesta: se espera que baje, porque el ruido degrada los bordes y el contraste que el OCR usa para reconocer caracteres. Esto es una hipótesis que se puede confirmar con el reporte de la Fase 06 (evaluación agrupada por tipo de degradación).

## Reto para estudiantes

Agregar un nuevo tipo de degradación (por ejemplo: lluvia, sombra proyectada, o placa sucia) y, más adelante en la Fase 06, medir cómo afecta la exactitud de lectura.

**Criterios de evaluación:**
- La nueva degradación es una función separada (no se mezcla con las existentes).
- Su parámetro queda registrado como columna nueva en `etiquetas.csv`.
- `pytest` sigue pasando y el dataset se sigue generando de forma reproducible con la misma semilla.
