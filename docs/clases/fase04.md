# Clase Fase 04 — Localización de la placa

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede comparar dos estrategias distintas de localización de un objeto en una imagen (por color y por bordes), explicar por qué se usa HSV en vez de BGR/RGB para segmentar color, y aplicar una corrección de perspectiva para obtener un recorte rectangular utilizable por el OCR.

## Conceptos

- **Espacio de color HSV**: separa el matiz (H, el color en sí) de la saturación e intensidad. Es más robusto que BGR/RGB para segmentar "amarillo", porque el matiz cambia poco aunque el brillo de la escena varíe.
- **Segmentación por color**: `cv2.inRange` construye una máscara binaria de los píxeles dentro de un rango HSV configurado (`hsv_amarillo_bajo`/`hsv_amarillo_alto`).
- **Contornos**: `cv2.findContours` agrupa píxeles conectados de la máscara (o de los bordes) en curvas cerradas que se pueden medir y filtrar.
- **Filtros geométricos**: área mínima (descarta ruido pequeño), relación de aspecto cercana a 2:1 (la proporción real de la placa) y rectangularidad (área del contorno contra área de su rectángulo envolvente, descarta blobs irregulares).
- **Corrección de perspectiva**: `cv2.getPerspectiveTransform` + `cv2.warpPerspective` llevan un cuadrilátero inclinado a un rectángulo de tamaño fijo (400×200), para que el recorte sea comparable sin importar el ángulo de la cámara.

## Demostración paso a paso

```bash
pytest tests/test_localizacion.py -v

python -m placas.generador --n 200 --semilla 42
python -m placas.localizacion --fuente data/sinteticas
```

Salida esperada (criterio de cierre: al menos 90 % con el mejor método):
```
Imagenes evaluadas: 200
  Por color: 200/200 (100.0 %)
  Por bordes: 198/200 (99.0 %)
```

Mostrar en vivo `dibujar_candidatos()` sobre una imagen: la caja verde marca el candidato elegido, y comparar el recorte del método color (solo el amarillo, sin la franja de ciudad) contra el de bordes (la placa completa).

## Preguntas de verificación

1. **¿Por qué segmentar en HSV y no directamente en BGR?**
   Respuesta: en BGR, un cambio de brillo mueve los tres canales a la vez de forma poco predecible. En HSV, el matiz (H) del amarillo se mantiene casi igual aunque cambien el brillo o el contraste, así que el rango de segmentación es más estable ante la iluminación.

2. **¿Para qué sirve el filtro de rectangularidad, si ya se filtra por área y relación de aspecto?**
   Respuesta: un contorno puede tener el área y la proporción ancho/alto correctas y aun así no ser un rectángulo (por ejemplo, una forma en "L" o con un borde cóncavo). La rectangularidad (área del contorno / área de su rectángulo envolvente) descarta esas formas irregulares que las otras dos condiciones no detectan.

3. **¿Por qué el recorte final tiene siempre el mismo tamaño (400×200) sin importar el tamaño o ángulo del contorno detectado?**
   Respuesta: porque se aplica una transformación de perspectiva a un tamaño fijo de destino. Esto normaliza la entrada para el OCR de la Fase 05, que trabaja mejor con una escala y proporción consistentes en vez de recortes de tamaño variable.

## Reto para estudiantes

Ajustar el rango HSV de `config/reglas.yaml` para que la detección por color funcione también en fotos tomadas de noche o a contraluz (simuladas bajando mucho el brillo con una degradación adicional, o con fotos reales oscuras).

**Criterios de evaluación:**
- El ajuste se hace solo en `config/reglas.yaml` (rango HSV), sin tocar `localizacion.py`.
- Se documenta en un comentario del propio YAML qué condición de luz motivó el cambio.
- El porcentaje de localización por color no baja respecto al reportado con las imágenes normales (se puede correr `python -m placas.localizacion` antes y después del cambio para comparar).
