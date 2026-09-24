# Clase Fase 02 — Adquisición de imágenes

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante entiende una imagen digital como una matriz numérica, distingue el orden de canales BGR de OpenCV frente al RGB habitual, y puede explicar por qué una misma interfaz (`FuenteImagenes`) sirve para leer de una carpeta, una cámara o un video.

## Conceptos

- **Imagen como matriz**: una imagen a color es un arreglo numpy de forma `(alto, ancho, 3)`; cada posición `(fila, columna)` guarda tres valores de intensidad (uno por canal), entre 0 y 255.
- **Canales BGR**: OpenCV ordena los canales como azul, verde, rojo (al revés del RGB de Pillow o matplotlib), por una decisión histórica de la librería. Hay que recordarlo al mezclar OpenCV con otras librerías de imagen.
- **Resolución**: el ancho y el alto en píxeles de la imagen; determina cuánto detalle hay disponible para encontrar y leer la placa en fases siguientes.
- **FPS (fotogramas por segundo)**: `FPS = 1 / Δt`, donde `Δt` es el tiempo entre dos fotogramas consecutivos. Con una cámara o video es una propiedad del archivo/dispositivo; leyendo una carpeta de imágenes es, en cambio, una medida de qué tan rápido el código puede procesar cada una.
- **Iterador + gestor de contexto**: `FuenteImagenes` se recorre con `for fotograma in fuente` y se usa con `with ... as ...` para garantizar que la cámara o el archivo de video se liberen aunque ocurra un error a mitad de camino.

## Demostración paso a paso

```bash
pytest tests/test_adquisicion.py -v

# En un equipo con pantalla (ventana interactiva, teclas: espacio pausa, s guarda, q sale)
python -m placas.adquisicion --fuente data/sinteticas

# En un servidor sin entorno grafico (o para verificar rapido)
python -m placas.adquisicion --fuente data/sinteticas --sin-ventana
```

Mostrar la salida en consola (`archivo: 1000x700 px, 3 canales, NN.N FPS`) y explicar que el mismo comando, cambiando `--fuente` a `0`, leería de la cámara web del equipo en vez de la carpeta.

## Preguntas de verificación

1. **¿Por qué OpenCV usa el orden de canales BGR y no RGB?**
   Respuesta: es una decisión histórica heredada de versiones antiguas de la librería; se mantiene hoy por compatibilidad. Es importante recordarlo porque Pillow, matplotlib y la mayoría de formatos de imagen usan RGB, y mezclar ambos sin convertir produce colores invertidos.

2. **¿Por qué `FuenteImagenes` es un gestor de contexto (`with ... as ...`)?**
   Respuesta: para garantizar que la cámara o el archivo de video se liberen (`cap.release()`) incluso si ocurre un error mientras se procesan los fotogramas, evitando dejar el dispositivo bloqueado para otros programas.

3. **Al recorrer una carpeta de 200 imágenes (sin cámara real), ¿qué representa el "FPS" que calcula la clase?**
   Respuesta: no es un framerate físico, sino una medida de la velocidad de procesamiento del código: cuántas imágenes por segundo puede leer y entregar. Sirve para estimar si el pipeline completo podría correr en tiempo real más adelante.

## Reto para estudiantes

Mostrar el histograma de cada canal de color (B, G, R) de una imagen.

**Criterios de evaluación:**
- Se calcula el histograma de los tres canales por separado (por ejemplo con `cv2.calcHist` o `np.histogram`).
- El resultado se muestra en pantalla o se guarda en `salidas/` para al menos una imagen de `data/sinteticas/`.
- El código queda en una función independiente, reutilizable desde otra fase (por ejemplo, la de preprocesamiento).

---

[Fase anterior](fase01.md) · [Índice de guías](../README.md) · [Fase siguiente](fase03.md)
