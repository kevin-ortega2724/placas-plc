# Clase Fase 03 — Preprocesamiento

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede explicar qué aporta cada filtro clásico de visión por computador antes de buscar un objeto en una imagen, y sabe leer un mosaico de pasos intermedios para diagnosticar por qué falla una detección.

## Conceptos

- **Escala de grises**: reduce 3 canales a 1; simplifica el resto del procesamiento porque solo importa el contraste, no el color exacto.
- **CLAHE** (ecualización adaptativa de contraste): mejora el contraste por regiones (grilla `clahe_tamano_grilla`), útil cuando la iluminación es desigual (sombra de un lado, brillo del otro).
- **Filtro bilateral**: suaviza ruido de fondo pero conserva bordes fuertes, porque solo promedia píxeles vecinos de intensidad parecida — a diferencia de un desenfoque simple, que borra ruido y bordes por igual.
- **Canny**: detector de bordes que produce una imagen binaria (0 o 255) marcando cambios fuertes de intensidad; controlado por dos umbrales (`canny_umbral_bajo`, `canny_umbral_alto`).
- **Cierre morfológico** (dilatar + erosionar): une segmentos de borde separados por unos pocos píxeles, para que el contorno de la placa quede cerrado y sea utilizable como un solo contorno en la Fase 04.

## Demostración paso a paso

```bash
pytest tests/test_preproceso.py -v

python -m placas.generador --n 5 --semilla 42
python -m placas.preproceso --imagen data/sinteticas/placa_0000.png
# abrir salidas/00_mosaico.png
```

Comparar en el mosaico `04_canny.png` (bordes fragmentados por el ruido de fondo) contra `05_cierre_morfologico.png` (el contorno de la placa ya cerrado y sólido) — es la evidencia visual de por qué se necesita el cierre morfológico antes de buscar contornos.

## Preguntas de verificación

1. **¿Por qué se aplica CLAHE en vez de una ecualización de histograma global?**
   Respuesta: porque la ecualización global usa una sola transformación para toda la imagen, y si hay sombra de un lado y brillo del otro, mejora una zona a costa de saturar la otra. CLAHE ecualiza por regiones, adaptándose a la iluminación local.

2. **¿Por qué el filtro bilateral y no un desenfoque gaussiano simple antes de Canny?**
   Respuesta: un desenfoque gaussiano promedia todos los píxeles vecinos por igual, incluidos los que están en un borde real, difuminándolo. El filtro bilateral solo promedia vecinos con intensidad parecida, así que reduce el ruido de fondo sin debilitar el borde de la placa que Canny necesita detectar.

3. **Si subimos mucho `canny_umbral_bajo`, ¿qué pasa con el contorno de la placa?**
   Respuesta: Canny descarta más bordes débiles; el contorno de la placa puede quedar incompleto (fragmentado) incluso después del cierre morfológico, porque el cierre solo une huecos pequeños, no reconstruye bordes que nunca se detectaron.

## Reto para estudiantes

Comparar el resultado de Canny con al menos tres combinaciones distintas de `canny_umbral_bajo`/`canny_umbral_alto` sobre la misma imagen, y justificar con las imágenes guardadas en `salidas/` cuál combinación deja el contorno de la placa más limpio.

**Criterios de evaluación:**
- Se prueban al menos 3 combinaciones de umbrales (editando `config/reglas.yaml`, sin tocar `preproceso.py`).
- Se guardan las 3 imágenes de bordes resultantes con nombres distintos en `salidas/`.
- La justificación compara explícitamente cuántos bordes de fondo (ruido) aparecen frente a qué tan completo queda el contorno de la placa.
