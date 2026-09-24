# 06 · Integra, mide y entrega

**Objetivo:** demostrar qué funciona con evidencia y delimitar lo pendiente.

## 1. Conserva una referencia

Anota el commit con `git rev-parse HEAD`, versión de Python, semilla, tamaño del dataset y configuración. No cambies varios parámetros entre ensayos.

```bash
python -m pytest -q
python -m placas.evaluacion --fuente data/sinteticas --etiquetas data/sinteticas/etiquetas.csv
```

Conserva el resumen de pruebas y las métricas. Una suite aprobada no reemplaza una demostración del OCR real ni del PLC.

## 2. Prepara la demostración

Muestra un permitido, un rechazo y una lectura dudosa. Anota la entrada y el resultado esperado antes de ejecutarlos. Puedes aislar decisiones con lecturas construidas, pero identifica claramente esas pruebas frente a las que usan OCR real.

Si cuentas con PLC, usa el procedimiento del tutorial 05 y muestra el HMI en paralelo. Si solo cuentas con el simulador, demuestra ese alcance y deja explícita la integración pendiente. Para una demostración visual puedes grabar la pantalla de la interfaz; la aplicación recibe fotos, no un video continuo.

## 3. Entrega el informe

Copia [esta plantilla](../plantillas/informe.md) en `docs/entregas/tu-equipo.md`. Completa entradas, resultados, tabla de señales y al menos dos fallas o limitaciones. Añade enlaces a evidencia sintética o autorizada que pueda compartirse.

| Entregable | Comprobación |
|---|---|
| Video de 2–5 minutos | Se distinguen entradas, decisiones y alcance de simulación/PLC |
| Informe | Incluye configuración, métricas y tabla esperado/obtenido |
| Cambio del estudiante | Explica problema, modificación y prueba |
| Análisis de fallas | Señala etapa responsable e hipótesis comprobable |

## 4. Revisa y comparte

Sigue [CONTRIBUTING](../../CONTRIBUTING.md), revisa `git diff` y abre un pull request con tu ejercicio. No incluyas `.venv`, imágenes reales ni salidas privadas. Consulta la [rúbrica de la fase 13](../clases/fase13.md).

**Cierre:** otra persona puede repetir tu experimento a partir del informe y obtener una conclusión comparable, aunque los tiempos de procesamiento cambien con el equipo.

[Anterior](05-plc-hmi.md) · [Índice](../README.md)
