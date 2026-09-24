# Arquitectura y responsabilidades

| Componente | Entrada | Salida | Archivo |
|---|---|---|---|
| Adquisición | Carpeta, cámara o video según API | Imagen BGR | `src/placas/adquisicion.py` |
| Preprocesamiento | Imagen | Grises, filtrado, bordes | `src/placas/preproceso.py` |
| Localización | Imagen y configuración | Candidatos y recorte | `src/placas/localizacion.py` |
| OCR | Recorte | Texto, confianza y validez | `src/placas/ocr.py` |
| Pipeline | Imagen | Detección y lectura | `src/placas/pipeline.py` |
| Reglas | Lectura, fecha y listas | Decisión con motivo | `src/placas/reglas.py` |
| Señales | Decisión y lectura | Coils y registros | `src/placas/senales.py` |
| Comunicación | Señales | Escrituras Modbus | `src/placas/comunicacion.py` |
| PLC | Señales y entradas de control | Salidas y contadores | `plc/openplc/control_acceso.st` |
| HMI | Lecturas Modbus del PLC | Estado e histórico | `hmi/monitor.py` |

## Tres modos que debes distinguir

1. **Simulación local:** la interfaz usa `PlcSimulado` en su proceso. No hay un servidor Modbus asociado al simulador.
2. **Prueba de transporte:** `hmi/servidor_prueba.py` recibe y almacena valores, sin ejecutar control.
3. **Integración:** un Runtime PLC ejecuta el programa y publica las salidas que observa el HMI.

La interfaz llama al pipeline y a las reglas; los cambios de negocio deben hacerse en sus módulos, no duplicarse en la pantalla. El HMI solo lee. Configuración y rutas relativas se resuelven ejecutando desde la raíz del repositorio.

## Límites actuales

El envío de la interfaz no mantiene una sesión con watchdog continuo. El simulador de pantalla avanza por ejecución de Streamlit. El mapa de OpenPLC debe comprobarse en el Runtime concreto. El soporte completo de motos y la adquisición continua desde la interfaz son extensiones, no capacidades terminadas.

[Volver al índice](README.md)
