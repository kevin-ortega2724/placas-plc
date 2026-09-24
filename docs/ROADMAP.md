# Ruta de trabajo

El proyecto se construye por fases. Cada fase deja el repositorio funcionando, con pruebas que pasan y una etiqueta `fase-NN`. Los estudiantes pueden arrancar desde cualquier etiqueta.

Cada fase indica:
- **Objetivo**: qué funciona al terminar.
- **Conceptos**: qué se enseña.
- **Archivos**: qué se crea o modifica.
- **Reto para estudiantes**: qué deben cambiar ellos.
- **Cierre**: condición verificable para dar la fase por terminada.

El prompt de cada fase para el asistente de código está en [`PROMPTS.md`](PROMPTS.md).

---

## Bloque A. Procesamiento de imágenes

### Fase 00. Entorno y repositorio
- **Objetivo**: repositorio con estructura, entorno virtual y configuración cargable.
- **Conceptos**: entornos virtuales, dependencias, control de versiones, configuración externa.
- **Archivos**: `src/placas/configuracion.py`, `tests/test_configuracion.py`.
- **Reto**: agregar una regla nueva en `reglas.yaml` (por ejemplo, restringir el sábado el dígito 5) y verificar que se carga.
- **Cierre**: `pytest` pasa y `python -m placas.configuracion` imprime las reglas.

### Fase 01. Generador de placas sintéticas
- **Objetivo**: producir imágenes de placas colombianas de prueba con su etiqueta, sin usar datos personales.
- **Conceptos**: datos sintéticos, verdad de terreno (*ground truth*), aumento de datos (rotación, ruido, desenfoque, iluminación).
- **Archivos**: `src/placas/generador.py`, `data/sinteticas/etiquetas.csv`.
- **Reto**: agregar un nuevo tipo de degradación (lluvia, sombra, placa sucia) y medir después cómo afecta la lectura.
- **Cierre**: se generan 200 imágenes con placas del formato `ABC123` y un CSV con nombre de archivo y placa.

### Fase 02. Adquisición de imágenes
- **Objetivo**: leer imágenes desde carpeta, cámara web o video con una misma interfaz.
- **Conceptos**: imagen como matriz, canales BGR, resolución, fotogramas por segundo.
- **Archivos**: `src/placas/adquisicion.py`.
- **Reto**: mostrar el histograma de cada canal de color de una imagen.
- **Cierre**: `python -m placas.adquisicion --fuente data/sinteticas` recorre las imágenes y muestra dimensiones.

### Fase 03. Preprocesamiento
- **Objetivo**: mejorar la imagen antes de buscar la placa.
- **Conceptos**: escala de grises, ecualización (CLAHE), filtro bilateral, umbralización, detección de bordes (Canny), morfología.
- **Archivos**: `src/placas/preproceso.py`.
- **Reto**: comparar Canny con distintos umbrales y justificar la elección con imágenes.
- **Cierre**: con `depurar=True` se guardan en `salidas/` las imágenes de cada paso.

### Fase 04. Localización de la placa
- **Objetivo**: encontrar el rectángulo de la placa y recortarlo.
- **Conceptos**: espacio de color HSV, segmentación del amarillo de la placa colombiana, contornos, relación de aspecto, corrección de perspectiva.
- **Archivos**: `src/placas/localizacion.py`.
- **Reto**: ajustar el rango HSV para fotos tomadas de noche o a contraluz.
- **Cierre**: en las imágenes sintéticas se recorta la placa en al menos el 90 % de los casos.

### Fase 05. Lectura (OCR) y validación
- **Objetivo**: convertir el recorte en texto válido.
- **Conceptos**: OCR, confianza, expresiones regulares, correcciones por posición (O↔0, B↔8, I↔1).
- **Archivos**: `src/placas/ocr.py`.
- **Reto**: agregar soporte para placas de moto (`ABC12D`).
- **Cierre**: la función devuelve placa, confianza y si el formato es válido.

### Fase 06. Evaluación del sistema de visión
- **Objetivo**: medir qué tan bien lee el sistema.
- **Conceptos**: exactitud por placa y por carácter, matriz de confusión de caracteres, tiempo de procesamiento.
- **Archivos**: `src/placas/evaluacion.py`, `notebooks/06_evaluacion.ipynb`.
- **Reto**: identificar las tres confusiones más frecuentes y proponer una corrección.
- **Cierre**: reporte en `salidas/evaluacion.csv` con exactitud y tiempo medio por imagen.

---

## Bloque B. Reglas y señales

### Fase 07. Reglas de acceso (pico y placa)
- **Objetivo**: decidir el acceso a partir de la placa, la fecha y la hora.
- **Conceptos**: lógica de decisión con prioridades, tablas de verdad, festivos, pruebas con fecha simulada.
- **Archivos**: `src/placas/reglas.py`, `tests/test_reglas.py`.
- **Reto**: agregar la regla "vehículos con excepción pueden entrar en pico y placa solo si están en la lista de autorizados" y su prueba.
- **Cierre**: pruebas que cubren los seis códigos de decisión, incluidos casos frontera de horario (08:59, 09:00, 09:01).

### Fase 08. De la decisión a las señales
- **Objetivo**: traducir la decisión en coils y registros según la tabla del enunciado.
- **Conceptos**: variables digitales y analógicas, codificación de estados, escalado (confianza 0 a 1000), *handshake*, *watchdog*.
- **Archivos**: `src/placas/senales.py`, `src/placas/plc_simulado.py`.
- **Reto**: agregar un registro con el número de lecturas consecutivas de la misma placa (antirrebote).
- **Cierre**: un PLC simulado en Python recibe las señales y aplica la lógica del enunciado en consola.

### Fase 09. Interfaz gráfica
- **Objetivo**: interfaz que muestre imagen, pasos intermedios, placa leída, decisión y señales.
- **Conceptos**: interfaz de operador, visualización de estados, lámparas virtuales.
- **Archivos**: `app/interfaz.py` (Streamlit).
- **Reto**: agregar un selector de fecha y hora simuladas para probar el pico y placa.
- **Cierre**: `streamlit run app/interfaz.py` procesa imágenes de la carpeta o de la cámara.

---

## Bloque C. Comunicaciones y PLC

### Fase 10. Comunicación Modbus TCP
- **Objetivo**: enviar las señales a un servidor Modbus.
- **Conceptos**: cliente y servidor, coils y holding registers, direcciones, códigos de función, reconexión, *watchdog*.
- **Archivos**: `src/placas/comunicacion.py`, `hmi/servidor_prueba.py`.
- **Reto**: capturar el tráfico con Wireshark e identificar los códigos de función 05, 06, 15 y 16.
- **Cierre**: la interfaz escribe en un servidor Modbus de prueba y un cliente externo lee los valores.

### Fase 11. PLC en ladder
- **Objetivo**: programar en OpenPLC (o CODESYS) la lógica del enunciado.
- **Conceptos**: ladder, temporizadores TON, contadores CTU, flancos, SET/RESET, comparadores, mapeo Modbus del PLC.
- **Archivos**: `plc/openplc/control_acceso.st` o proyecto del editor, `plc/openplc/mapa_modbus.md`.
- **Reto**: agregar un segundo carril de entrada con su propia talanquera.
- **Cierre**: con la interfaz enviando lecturas, el PLC abre la talanquera, cuenta ingresos y detecta pérdida de comunicación.

### Fase 12. HMI de solo lectura
- **Objetivo**: un programa independiente que solo lee salidas y contadores del PLC.
- **Conceptos**: separación de responsabilidades, supervisión, registro histórico.
- **Archivos**: `hmi/monitor.py`.
- **Reto**: guardar un histórico en CSV y graficar ingresos por hora.
- **Cierre**: el monitor muestra estado de la talanquera, lámparas y contadores en tiempo real.

### Fase 13. Integración y proyecto final
- **Objetivo**: sistema completo funcionando con cámara real o video.
- **Entregable del estudiante**: video de demostración, informe con mapa de señales, resultados de evaluación y análisis de fallas.
