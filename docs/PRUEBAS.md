# Comprobaciones por etapa

Ejecuta desde la raíz, con el entorno activado. Añade `python -m pytest` delante de las rutas de esta tabla y `-q` al final.

| Etapa | Archivos de prueba | Evidencia manual adicional |
|---|---|---|
| Entorno | `tests/test_configuracion.py` | Configuración impresa |
| Datos | `tests/test_generador.py tests/test_adquisicion.py` | PNG y etiquetas |
| Visión | `tests/test_preproceso.py tests/test_localizacion.py tests/test_ocr.py tests/test_pipeline.py` | Recorte y OCR real comparados con etiqueta |
| Evaluación | `tests/test_evaluacion.py` | CSV y matriz de confusión propios |
| Decisiones | `tests/test_reglas.py tests/test_senales.py` | Seis escenarios esperados/obtenidos |
| Simulación | `tests/test_plc_simulado.py` | Estados y temporización explicados |
| Interfaz | `tests/test_interfaz.py` | Selección, subida y foto de cámara |
| Modbus | `tests/test_comunicacion.py` | Escrituras observadas en receptor |
| HMI | `tests/test_monitor.py` | Lectura de salidas de un PLC funcional |

## Suite completa

```bash
python -m pytest -q
```

Las pruebas generan sus datos temporales y algunas sustituyen componentes externos. El éxito de esas pruebas no mide la exactitud del modelo OCR descargado ni verifica un PLC físico. Para esos resultados usa los tutoriales 01 y 05.

## Registro mínimo de un ensayo

Indica commit, comando, resultado, entrada, esperado, obtenido y ubicación de la evidencia. Si no ejecutaste una parte, escribe **pendiente**, no **aprobada**.

[Plantilla](plantillas/informe.md) · [Índice](README.md)
