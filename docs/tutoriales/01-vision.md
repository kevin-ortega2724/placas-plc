# 01 · De los píxeles a la placa

**Prerrequisito:** tutorial 00 completado. **Objetivo:** distinguir adquisición, preprocesamiento, localización, OCR y evaluación.

## 1. Recorre las imágenes

```bash
python -m placas.adquisicion --fuente data/sinteticas --sin-ventana
python -m pytest tests/test_generador.py tests/test_adquisicion.py -q
```

Observa las dimensiones. Consulta `data/sinteticas/etiquetas.csv`: esa es la referencia para evaluar, no el texto producido por OCR.

## 2. Examina las transformaciones

```bash
python -m placas.preproceso --imagen data/sinteticas/placa_0000.png
python -m pytest tests/test_preproceso.py -q
```

Revisa los archivos generados en `salidas/`. Explica qué cambia al pasar a grises, ecualizar, filtrar y detectar bordes. Cambia un umbral Canny en `config/reglas.yaml`, repite y compara; restaura el valor al terminar.

## 3. Localiza y lee

```bash
python -m placas.localizacion --fuente data/sinteticas
python -m placas.pipeline --imagen data/sinteticas/placa_0000.png
python -m pytest tests/test_localizacion.py tests/test_ocr.py tests/test_pipeline.py -q
```

Compara el recorte y el texto normalizado con el CSV. Una localización correcta no garantiza una lectura correcta. Si quieres ejecutar `placas.ocr` por separado, `--recorte` debe apuntar a una imagen ya recortada de la placa.

## 4. Mide el conjunto

```bash
python -m placas.evaluacion --fuente data/sinteticas --etiquetas data/sinteticas/etiquetas.csv
python -m pytest tests/test_evaluacion.py -q
```

Revisa `salidas/evaluacion.csv` y `salidas/confusiones.png`. Registra exactitud por placa, por carácter y tiempo medio. No uses un porcentaje inventado como resultado esperado: las métricas dependen del conjunto, fuente, modelos y entorno.

| Ensayo | Parámetro cambiado | Placas correctas / total | Tiempo medio | Fallo observado |
|---|---|---|---|---|
| Base | Ninguno | Completar | Completar | Completar |
| Variante | Un único parámetro | Completar | Completar | Completar |

**Criterio para avanzar:** puedes explicar un error de localización y uno de OCR, y tienes un reporte de evaluación propio.

**Reto:** selecciona tres errores, plantea una hipótesis por caso y cambia un solo parámetro para contrastarla. Consulta las [clases 01–06](../README.md).

[Anterior](00-instalacion.md) · [Siguiente: reglas](02-reglas.md)
