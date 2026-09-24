# Clase Fase 13 — Integración y proyecto final

Duración estimada: 2 horas de clase + trabajo autónomo del estudiante (demo y grabación).

## Objetivos

Que el estudiante integre todo lo construido en las fases 00 a 12 en una sola demostración con cámara o video real, y que documente el sistema completo con evidencia (no solo con la afirmación de que "funciona").

## A diferencia de las fases anteriores

Esta fase no agrega un módulo nuevo: conecta los que ya existen y probaron por separado.

```
Camara/video (Fase 02) -> Preproceso (03) -> Localizacion (04) -> OCR (05)
   -> Reglas de pico y placa (07) -> Senales (08) -> Modbus (10) -> PLC ladder (11)
   -> HMI de solo lectura (12)
```

La interfaz (Fase 09) ya orquesta el lado de visión + reglas + señales; solo falta que el PLC de la Fase 11 esté realmente cargado en OpenPLC (o, como alternativa razonable si no hay hardware/software de PLC disponible, usar `plc_simulado.py` de la Fase 08 como sustituto documentado) y que el HMI de la Fase 12 esté corriendo en paralelo contra ese Runtime. El simulador local no expone Modbus: si se usa como alternativa, se debe declarar la supervisión remota como pendiente.

## Qué debe entregar el estudiante

1. **Video de demostración** (2-5 minutos): mostrando, con cámara real o un video pregrabado de un vehículo con placa visible, al menos un caso de cada categoría de decisión que sea posible reproducir de forma segura: `PERMITIDO`, algún tipo de `RECHAZADO` (`REPORTADO`, `NO_AUTORIZADO` o `PICO_Y_PLACA`, usando la fecha/hora simulada de la interfaz) y `LECTURA_DUDOSA`. El HMI de solo lectura debe verse actualizándose en paralelo.
2. **Informe** con, como mínimo:
   - **Mapa de señales**: la tabla de coils/registros del ENUNCIADO con los valores observados durante la demo (puede ser una captura de las tablas que muestra la interfaz).
   - **Resultados de evaluación**: el resumen de `python -m placas.evaluacion` sobre el dataset sintético (Fase 06) — porcentaje localizado, exactitud por placa y por carácter, tiempo por etapa.
   - **Análisis de fallas**: al menos dos casos donde el sistema se equivocó o dudó (con cámara real, esto es casi seguro que va a pasar) y una hipótesis concreta, basada en el código, de por qué ocurrió y qué fase sería responsable de corregirlo.

## Demostración en clase (lo que el docente verifica)

No hay `pytest` para "la demo" en sí (es un evento con hardware real), pero sí se puede verificar que el sistema *puede* correr end-to-end antes de pedirle al estudiante que grabe nada:

```bash
# 1. Generar dataset y confirmar que el pipeline sigue funcionando de punta a punta
python -m placas.generador --n 20 --semilla 42
python -m placas.evaluacion

# 2. Con camara o video real, vía la interfaz
streamlit run app/interfaz.py
# barra lateral -> origen "Camara"

# 3. Con el Runtime PLC ya activo y su mapa confirmado, abrir el HMI
python -m streamlit run hmi/monitor.py --server.port 8502
```

La interfaz toma fotografías; no procesa video continuo. Para demostrar control con watchdog y un HMI conectado, siga el [tutorial de PLC y HMI](../tutoriales/05-plc-hmi.md). `python -m placas.plc_simulado` es solo una demo local de consola.

## Preguntas de verificación

1. **¿Por qué "funciona con imágenes sintéticas al 100 %" (Fase 06) no es suficiente evidencia de que el sistema funciona con una cámara real?**
   Respuesta: las imágenes sintéticas tienen degradaciones controladas y conocidas (rotación, ruido, desenfoque dentro de rangos fijos); una cámara real introduce condiciones que el generador no modela necesariamente igual de bien (reflejos, suciedad en el lente, ángulos extremos, placas sucias o dobladas, iluminación nocturna real). El 100 % sintético es una cota superior optimista, no una garantía.

2. **Si en la demo el sistema reporta `LECTURA_DUDOSA` para una placa que a simple vista se lee bien, ¿en qué fase empezaría a investigar primero y por qué?**
   Respuesta: en la Fase 05 (OCR), revisando `confianza` y `formato_valido` de la `Lectura`; si la confianza está por debajo del umbral de `config/reglas.yaml` a pesar de que el texto se ve bien, puede ser un problema de iluminación o enfoque que afecta al OCR aunque el ojo humano compense fácilmente.

3. **¿Por qué el informe pide explícitamente "análisis de fallas" en vez de solo mostrar los casos que funcionaron?**
   Respuesta: porque un sistema que solo se demuestra en sus mejores condiciones no dice nada sobre su confiabilidad real; entender y explicar por qué falla (y en qué etapa) es la evidencia de que el estudiante entendió el pipeline completo, no solo que lo hizo correr una vez.

## Rúbrica sugerida

| Criterio | Insuficiente | Aceptable | Sobresaliente |
|---|---|---|---|
| Demo en video | No hay video, o no muestra decisiones distintas | Muestra al menos 2 categorías de decisión | Muestra las 3 categorías (permitido, rechazado, dudoso) con el HMI visible en paralelo |
| Mapa de señales | Ausente o copiado del ENUNCIADO sin datos propios | Incluye valores observados de al menos un caso | Incluye valores observados de varios casos distintos, correctamente interpretados |
| Resultados de evaluación | Ausentes | Se reportan las métricas de `evaluacion.py` | Se comparan las métricas sintéticas contra lo observado con cámara real, con hipótesis de la diferencia |
| Análisis de fallas | Ausente o superficial ("no funcionó") | Identifica al menos un fallo con una fase responsable | Identifica varios fallos, los conecta con líneas de código concretas y propone una mejora accionable |

---

[Fase anterior](fase12.md) · [Índice de guías](../README.md)
