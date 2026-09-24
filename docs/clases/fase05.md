# Clase Fase 05 — Lectura (OCR) y validación

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante entiende qué hace un motor de OCR y por qué se carga una sola vez, sabe normalizar y validar texto ruidoso con expresiones regulares y correcciones por posición, y puede explicar por qué se mide el tiempo de cada etapa del pipeline por separado.

## Conceptos

- **OCR (reconocimiento óptico de caracteres)**: un modelo que recibe una imagen y devuelve texto, con una confianza asociada a cada detección.
- **Carga perezosa (lazy loading)**: EasyOCR tarda varios segundos en inicializarse (carga una red neuronal); se crea una sola vez con un singleton a nivel de módulo, no una vez por imagen.
- **Normalización de texto**: pasar a mayúsculas, quitar separadores y aplicar correcciones específicas por posición (O↔0, B↔8, ...) porque el OCR confunde caracteres visualmente parecidos de forma sistemática.
- **Expresiones regulares para validación**: `^[A-Z]{3}[0-9]{3}$` no solo valida el formato, sino que también sirve para *clasificar* el resultado (carro, moto o ninguno).
- **Medición de tiempos por etapa**: separar el tiempo de preprocesamiento, localización y OCR permite encontrar el cuello de botella real del sistema (Fase 06), en vez de adivinar.

## Demostración paso a paso

```bash
pytest tests/test_ocr.py tests/test_pipeline.py -v   # no requieren EasyOCR instalado

pip install easyocr   # descarga PyTorch, puede tardar varios minutos

python -m placas.generador --n 5 --semilla 42
python -m placas.pipeline --imagen data/sinteticas/placa_0000.png
```

Mostrar en vivo la diferencia entre `texto_crudo` (lo que devolvió EasyOCR, con posibles errores) y `placa_normalizada` (después de aplicar mayúsculas, quitar separadores y las correcciones de `config/reglas.yaml`).

## Preguntas de verificación

1. **¿Por qué el lector de EasyOCR se guarda en una variable global (`_lector_ocr`) en vez de crearse dentro de `leer_placa`?**
   Respuesta: crear el lector implica cargar un modelo de red neuronal, lo cual toma varios segundos. Si se hiciera en cada llamada, procesar 200 imágenes tomaría 200 veces ese costo de inicialización en vez de solo una.

2. **¿Por qué las correcciones de OCR se aplican por posición (letras en 1-3, números en 4-6) y no de forma global sobre todo el texto?**
   Respuesta: porque el mismo carácter confundido significa cosas distintas según dónde aparece: una "O" leída donde debería haber un número se corrige a "0", pero una "O" en las primeras tres posiciones (donde se esperan letras) está probablemente bien y no debe tocarse. Aplicar la corrección sin importar la posición introduciría errores nuevos.

3. **Si el pipeline mide 0.02 s en preprocesamiento, 0.01 s en localización y 0.3 s en OCR, ¿qué le dice eso sobre dónde optimizar primero?**
   Respuesta: que el OCR es, por mucho, la etapa más costosa; cualquier esfuerzo de optimización (una GPU, un modelo más liviano, procesar menos resolución) debería concentrarse ahí primero, porque mejorar preprocesamiento o localización apenas movería el tiempo total.

## Reto para estudiantes

Agregar soporte para placas de moto (`ABC12D`: tres letras, dos números y una letra final).

**Criterios de evaluación:**
- `normalizar_texto` sigue funcionando igual para placas de carro (no rompe las pruebas existentes).
- Se agrega una prueba que verifique la normalización de una placa de moto con al menos un carácter mal leído.
- `_determinar_tipo` devuelve `"moto"` para placas que cumplan `formato_placa.moto` de config, sin necesitar cambios en `config/reglas.yaml`.

---

[Fase anterior](fase04.md) · [Índice de guías](../README.md) · [Fase siguiente](fase06.md)
