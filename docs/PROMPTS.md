# Prompts por fase

Prompts listos para copiar en un asistente de código (Claude Code u otro) abierto en la raíz del repositorio. Úselos en orden: cada uno supone que la fase anterior está cerrada.

Recomendaciones:
- Abra una sesión nueva por fase para mantener el contexto limpio.
- Revise el código generado antes de hacer commit. El objetivo es que usted lo entienda y pueda explicarlo en clase.
- Si algo falla, pegue el error completo y pida la corrección antes de seguir.

---

## Prompt de arranque (una vez por sesión)

```
Lee CLAUDE.md, ENUNCIADO.md y docs/ROADMAP.md antes de hacer cualquier cambio.
Resume en 5 líneas qué es el proyecto, en qué fase está el repositorio
(revisa git tag y los archivos de src/placas) y cuál es la siguiente fase.
No escribas código todavía.
```

---

## Fase 00. Entorno y repositorio

```
Fase 00 del ROADMAP.

Crea src/placas/__init__.py y src/placas/configuracion.py con:
- una función cargar_reglas(ruta) que lea config/reglas.yaml y devuelva
  un dataclass Reglas con subestructuras para pico_y_placa, ocr,
  formato_placa, correcciones y plc;
- funciones cargar_autorizados(ruta) y cargar_reportados(ruta) que
  devuelvan diccionarios indexados por placa;
- validación: días válidos, dígitos entre 0 y 9, horas en formato HH:MM,
  confianza entre 0 y 1. Errores con mensajes claros en español.
Agrega un pyproject.toml mínimo para que "pip install -e ." haga
importable el paquete placas desde src/.
Crea tests/test_configuracion.py con pruebas de carga correcta y de
errores de validación.
El bloque __main__ debe imprimir un resumen legible de las reglas.
Criterio: pytest pasa y "python -m placas.configuracion" funciona.
```

---

## Fase 01. Generador de placas sintéticas

```
Fase 01 del ROADMAP.

Crea src/placas/generador.py que genere imágenes de placas colombianas
de automóvil particular:
- fondo amarillo, borde negro, texto negro "ABC 123" con tipografía
  sans condensada (usa una fuente del sistema y deja la ruta configurable),
  y una franja inferior con un nombre de ciudad ficticio;
- proporción real aproximada 33 x 16,5 cm;
- la placa se pega sobre un fondo que simule la parte frontal de un
  vehículo (rectángulo gris con degradado y ruido) para que haya que
  buscarla en la imagen;
- degradaciones aleatorias configurables: rotación ±15°, perspectiva,
  desenfoque, ruido gaussiano, cambios de brillo y contraste;
- semilla configurable para reproducibilidad.
Guarda las imágenes en data/sinteticas/ y un etiquetas.csv con
archivo, placa, y los parámetros de degradación usados.
Incluye placas de config/autorizados.csv, de reportados.csv y placas
aleatorias, para que después existan todos los casos de decisión.
CLI: python -m placas.generador --n 200 --semilla 42
Agrega una prueba que verifique que se generan n archivos y que las
placas del CSV cumplen el formato.
```

---

## Fase 02. Adquisición de imágenes

```
Fase 02 del ROADMAP.

Crea src/placas/adquisicion.py con una clase FuenteImagenes que ofrezca
la misma interfaz (iterador de fotogramas con nombre y marca de tiempo)
para tres fuentes: carpeta de imágenes, cámara web (índice) y archivo
de video. Debe liberar recursos correctamente (context manager).
CLI: python -m placas.adquisicion --fuente data/sinteticas
     python -m placas.adquisicion --fuente 0          (cámara)
Muestra cada imagen en una ventana de OpenCV con su tamaño, canales y
FPS; teclas: espacio para pausar, s para guardar en salidas/, q para salir.
Explica en docstrings qué es una imagen BGR como matriz numpy.
Prueba con pytest usando la carpeta sintética.
```

---

## Fase 03. Preprocesamiento

```
Fase 03 del ROADMAP.

Crea src/placas/preproceso.py con funciones separadas y documentadas:
a_grises, ecualizar_clahe, filtrar_bilateral, detectar_bordes_canny,
cerrar_morfologico, y una función preprocesar(imagen, parametros,
depurar=False) que las encadene.
Los parámetros (tamaño de kernel, umbrales de Canny, clipLimit de CLAHE)
vienen de una sección nueva "preproceso" en config/reglas.yaml.
Con depurar=True guarda cada paso en salidas/ como 01_grises.png,
02_clahe.png, etc., y además un mosaico con todos los pasos juntos.
En cada docstring explica en dos o tres líneas qué hace el filtro y por
qué ayuda a encontrar la placa, en lenguaje para estudiantes de
ingeniería eléctrica.
CLI que procese una imagen y abra el mosaico.
```

---

## Fase 04. Localización de la placa

```
Fase 04 del ROADMAP.

Crea src/placas/localizacion.py que encuentre la placa y devuelva el
recorte rectificado. Implementa dos métodos y compáralos:
1. Por color: convertir a HSV, segmentar el amarillo de la placa con
   rango configurable, limpiar con morfología y tomar contornos.
2. Por bordes: usar la salida de preproceso.py y buscar contornos
   cuadriláteros.
Filtra candidatos por área mínima, relación de aspecto (cercana a 2:1)
y rectangularidad. Corrige perspectiva con getPerspectiveTransform a un
tamaño fijo (por ejemplo 400 x 200).
Devuelve un dataclass Deteccion con: encontrada, metodo, caja, recorte,
puntaje.
Con depurar=True dibuja todos los candidatos en una imagen y marca el
elegido.
Agrega un script que recorra data/sinteticas/ y reporte el porcentaje
de placas encontradas por cada método.
Criterio: al menos 90 % en las sintéticas con el mejor método.
```

---

## Fase 05. Lectura (OCR) y validación

```
Fase 05 del ROADMAP.

Crea src/placas/ocr.py:
- inicializa EasyOCR una sola vez (carga perezosa) con allowlist de
  config;
- leer_placa(recorte) devuelve un dataclass Lectura con: texto_crudo,
  placa_normalizada, confianza (0 a 1), formato_valido, tipo
  ("carro" o "moto" o None);
- normalización: mayúsculas, quitar espacios y guiones, aplicar las
  correcciones por posición de config (posiciones 1 a 3 deben ser
  letras, 4 a 6 números);
- ignorar la franja inferior con el nombre de la ciudad (recortar la
  parte superior del recorte antes del OCR);
- validar con las expresiones regulares de config.
Pruebas unitarias de la normalización con casos como "A8C 12O" -> "ABC120"
y "UTP-123" -> "UTP123", sin depender de EasyOCR.
Crea src/placas/pipeline.py con procesar_imagen(imagen) que encadene
preproceso, localización y OCR, y mida el tiempo de cada etapa.
```

---

## Fase 06. Evaluación

```
Fase 06 del ROADMAP.

Crea src/placas/evaluacion.py que ejecute el pipeline sobre
data/sinteticas/ y compare con etiquetas.csv. Reporta:
- porcentaje de placas localizadas;
- exactitud por placa completa y por carácter;
- matriz de confusión de caracteres (qué se leyó en vez de qué);
- tiempo medio por etapa;
- exactitud agrupada por tipo de degradación del generador.
Guarda salidas/evaluacion.csv y salidas/confusiones.png.
Crea notebooks/06_evaluacion.ipynb que cargue el CSV y grafique
los resultados, con celdas de texto que guíen el análisis del
estudiante (preguntas, no respuestas).
```

---

## Fase 07. Reglas de acceso

```
Fase 07 del ROADMAP.

Crea src/placas/reglas.py con:
- enum CodigoDecision con los valores 0 a 5 del ENUNCIADO;
- función decidir(lectura, fecha_hora, reglas, autorizados, reportados)
  que aplique las reglas en el orden de prioridad del ENUNCIADO y
  devuelva un dataclass Decision con código, nombre, motivo en texto
  y ultimo_digito;
- pico y placa según día de la semana, horarios y festivos (librería
  holidays con el país de config); "fin" del horario es exclusivo;
- la fecha y hora siempre entran como parámetro (nunca datetime.now()
  dentro de la lógica) para poder probar cualquier día.
tests/test_reglas.py con pruebas parametrizadas que cubran los seis
códigos, placas con excepción, un festivo, sábado, y los bordes
05:59, 06:00, 08:59, 09:00.
Agrega al final del archivo de pruebas una tabla en comentario con los
casos, para usarla en clase.
```

---

## Fase 08. Señales y PLC simulado

```
Fase 08 del ROADMAP.

Crea src/placas/senales.py:
- dataclass Senales con los coils y holding registers de la tabla del
  ENUNCIADO;
- función a_senales(decision, lectura) que haga la traducción, con la
  confianza escalada a entero 0 a 1000;
- función a_modbus(senales) que devuelva dos listas: coils[0..4] y
  registros[0..3], en el orden de direcciones del ENUNCIADO.
Crea src/placas/plc_simulado.py: una clase que reciba Senales, ejecute
cíclicamente (cada 50 ms) la lógica del ENUNCIADO con temporizadores
TON, contadores, flanco de nueva_lectura, acuse de recibo y watchdog,
e imprima en consola el estado de Q0 a Q3 y los contadores.
Escribe la lógica del PLC simulado imitando la estructura de un
programa ladder (una función por renglón, con comentario del renglón
equivalente) para que después se traduzca fácil a OpenPLC.
Pruebas de a_senales para cada código y del watchdog.
```

---

## Fase 09. Interfaz

```
Fase 09 del ROADMAP.

Crea app/interfaz.py en Streamlit con:
- barra lateral: fuente (carpeta, subir imagen, cámara), fecha y hora
  simuladas o reales, casilla "mostrar pasos intermedios", selector
  de destino (PLC simulado o Modbus, este último deshabilitado por ahora);
- zona principal: imagen original con la caja de la placa, recorte,
  texto leído y confianza, decisión con color (verde, rojo, ámbar,
  gris), y una tabla con los coils y registros que se enviarían;
- lámparas virtuales para Q0 a Q3 alimentadas por el PLC simulado;
- expander con los pasos intermedios del preprocesamiento.
No dupliques lógica: la interfaz solo llama al pipeline, reglas y señales.
```

---

## Fase 10. Comunicación Modbus TCP

```
Fase 10 del ROADMAP.

Crea src/placas/comunicacion.py con una clase ClienteModbusAcceso
(pymodbus 3.x, síncrono):
- conectar con reintentos y tiempo de espera configurables;
- enviar(senales): escribe coils con write_coils (FC15) y registros con
  write_registers (FC16) en las direcciones del ENUNCIADO;
- hilo de watchdog que incremente el registro 3 cada periodo de config;
- leer_acuse(): lee el coil 4 para saber si el PLC ya procesó la lectura;
- manejo claro de errores de conexión, sin detener la interfaz.
Crea hmi/servidor_prueba.py: servidor Modbus TCP en Python que imprima
cada escritura recibida, para probar sin PLC.
Habilita en la interfaz el destino Modbus con host y puerto de config.
Documenta en docs/modbus.md las direcciones, los códigos de función
usados y cómo verlos en Wireshark (filtro "modbus" o "tcp.port == 502").
```

---

## Fase 11. PLC en ladder (OpenPLC)

```
Fase 11 del ROADMAP.

Para OpenPLC Runtime y OpenPLC Editor:
- escribe plc/openplc/mapa_modbus.md con la correspondencia entre las
  direcciones Modbus del ENUNCIADO y las direcciones IEC de OpenPLC
  (%QX, %IX, %QW, %IW, %MW), verificando la tabla de mapeo de la
  versión de OpenPLC y señalando lo que el docente debe confirmar;
- como el editor de ladder es gráfico, entrega la lógica en dos formas:
  plc/openplc/control_acceso.st en texto estructurado equivalente y
  plc/openplc/ladder_paso_a_paso.md con cada renglón descrito
  (contactos, bobinas, TON, CTU, R_TRIG, comparadores) para dibujarlo
  en el editor;
- incluye la lógica completa del ENUNCIADO: talanquera 5 s, luz roja
  3 s, ámbar con validación manual, acuse de nueva_lectura, watchdog
  3 s, emergencia, contadores de ingresos y rechazos en registros
  legibles por Modbus.
Agrega plc/openplc/pruebas.md con un protocolo de prueba paso a paso
usando la interfaz y el monitor.
```

---

## Fase 12. HMI de solo lectura

```
Fase 12 del ROADMAP.

Crea hmi/monitor.py: aplicación Streamlit independiente que solo LEE
del PLC por Modbus (nunca escribe):
- estado de talanquera, luces roja, ámbar y alarma de comunicación;
- contadores de ingresos y rechazos;
- último código de decisión y última confianza;
- actualización cada 500 ms;
- registro histórico en salidas/historico.csv y gráfica de ingresos
  por hora.
Muestra un aviso claro si no hay conexión con el PLC.
```

---

## Prompts de apoyo para el docente

**Guía de clase de una fase**
```
Con base en el código actual de la fase NN, escribe una guía de clase
de 2 horas en docs/clases/faseNN.md: objetivos, conceptos con
ecuaciones o figuras cuando aplique, demostración paso a paso con los
comandos exactos, tres preguntas de verificación con respuesta y el
reto para estudiantes con criterios de evaluación.
```

**Versión para estudiantes con huecos**
```
Crea una rama "estudiante-faseNN" donde las funciones clave de la fase
NN queden con la firma, el docstring y un "raise NotImplementedError",
y las pruebas se mantengan. Así los estudiantes completan el código
hasta que pytest pase.
```

**Revisión de un pull request de estudiante**
```
Revisa los cambios de la rama <rama> respecto a fase-NN: ¿cumple el
reto?, ¿pasan las pruebas?, ¿respeta CLAUDE.md? Da una retroalimentación
breve y concreta para el estudiante y una nota sugerida según la
rúbrica de docs/clases/faseNN.md.
```
