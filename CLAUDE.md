# Convenciones del proyecto (léase antes de escribir código)

Proyecto didáctico: los estudiantes leerán y modificarán este código. La claridad es más importante que la brevedad.

## Lenguaje y estilo
- Python 3.11. Tipado con *type hints* en todas las funciones públicas.
- Identificadores en español sin tildes (`detectar_placa`, `ultimo_digito`). Docstrings y comentarios en español.
- Un módulo por etapa en `src/placas/`. Cada módulo incluye un bloque `if __name__ == "__main__":` con una demostración ejecutable desde la terminal.
- Nada de valores mágicos en el código: umbrales, rutas y reglas se leen de `config/`.
- Funciones pequeñas y puras cuando sea posible, para poder probarlas con pytest.

## Visión
- OpenCV para procesamiento, EasyOCR para lectura. No usar servicios en la nube.
- Toda función de procesamiento puede guardar su imagen intermedia en `salidas/` cuando `depurar=True`, con nombre `NN_etapa.png`, para que los estudiantes vean cada paso.

## Datos
- No subir imágenes reales. `data/crudas/`, `data/sinteticas/` y `salidas/` están en `.gitignore` (las sintéticas pesan demasiado para versionarlas y son reproducibles).
- Antes de trabajar, cada quien genera su copia local: `python -m placas.generador --n 200 --semilla 42`. Con la misma semilla el dataset es idéntico para todos.
- Las pruebas automáticas no dependen de este dataset fijo: generan sus propias imágenes de prueba en carpetas temporales.

## Pruebas
- pytest en `tests/`. Cada fase agrega sus pruebas. Todas deben pasar antes de cerrar una fase.

## Git
- Un commit por paso lógico, mensaje en español en imperativo ("Agrega segmentación por color").
- Al cerrar una fase, el docente crea la etiqueta `fase-NN`.
