# 03 · Explora la interfaz como operador

**Objetivo:** relacionar imagen, lectura, decisión y señales. Completa primero los tutoriales 00–02.

```bash
python -m streamlit run app/interfaz.py
```

## Práctica guiada

1. Abre `http://localhost:8501` y elige **Carpeta** → `data/sinteticas`.
2. Busca en `etiquetas.csv` una imagen de una placa autorizada. Selecciónala y compara la placa leída con la etiqueta.
3. Deja **PLC simulado** como destino y desactiva **Usar fecha y hora reales**.
4. Elige una fecha y horario restringidos para el último dígito de esa placa según `config/reglas.yaml`. Compara con un horario fuera de restricción. Verifica que la placa no tenga excepción.
5. Activa **Mostrar pasos intermedios** y abre el desplegable de preprocesamiento.
6. Prueba **Subir imagen** con un PNG/JPG local y **Camara** con una foto autorizada desde el navegador.
7. Anota lectura, confianza, decisión y coils para tres entradas.

Si el OCR devuelve baja confianza, la decisión puede ser `LECTURA_DUDOSA` aunque la placa verdadera esté autorizada. Aísla las reglas con el tutorial anterior.

| Imagen | Placa verdadera | Placa leída | Confianza | Fecha/hora | Decisión | Explicación |
|---|---|---|---|---|---|---|
| Completar | | | | | | |

## Qué estás observando

Las lámparas pertenecen al `PlcSimulado` local, incluso si seleccionas Modbus TCP. El simulador avanza un ciclo cuando se ejecuta la aplicación; no es un ciclo PLC continuo en segundo plano. Cambiar controles puede volver a procesar y enviar la imagen. No interpretes cada recarga como un vehículo distinto en una instalación real.

La opción cámara toma fotos; el flujo de video continuo no está implementado en esta interfaz.

```bash
python -m pytest tests/test_interfaz.py -q
```

**Reto:** diseña tres escenarios de operador y documenta sus entradas y resultados esperados antes de ejecutarlos.

**Criterio para avanzar:** distingues una lectura incorrecta de una decisión correcta aplicada a esa lectura y conservas tres filas de evidencia.

[Anterior](02-reglas.md) · [Siguiente: Modbus](04-modbus.md)
