# 04 · Envía señales por Modbus TCP

**Objetivo:** observar escrituras reales sin necesitar OpenPLC. Activa el entorno y entra en la raíz del repositorio en cada terminal.

## 1. Inicia el receptor (terminal A)

```bash
python -m hmi.servidor_prueba --host 127.0.0.1 --puerto 5020
```

Espera el mensaje de escucha. El proceso permanece activo hasta Ctrl+C.

## 2. Configura y abre la interfaz (terminal B)

Edita solo estos campos dentro de la sección `plc` de `config/reglas.yaml`, conservando `unidad` y `periodo_watchdog_s`:

```yaml
plc:
  host: "127.0.0.1"
  puerto: 5020
  unidad: 1
  periodo_watchdog_s: 1.0
```

Reinicia Streamlit después de cambiar la configuración, porque la aplicación la mantiene en caché.

```bash
python -m streamlit run app/interfaz.py
```

Selecciona una imagen y **Modbus TCP**. **Resultado esperado:** confirmación de envío en la interfaz y escrituras de coils/registros impresas en la terminal A.

## 3. Verifica una falla controlada

Detén la terminal A y cambia de imagen. La interfaz debe mostrar el fallo de conexión sin terminar abruptamente. Reinicia el servidor y repite.

```bash
python -m pytest tests/test_comunicacion.py -q
```

## 4. Interpreta lo recibido

Usa el [mapa de direcciones y funciones](../modbus.md). Compara los cinco coils y cuatro registros con las tablas de la interfaz.

| Ensayo | Resultado esperado | Resultado observado |
|---|---|---|
| Receptor activo | Escrituras y confirmación | Completar |
| Receptor apagado | Error visible de conexión | Completar |
| Receptor reiniciado | Se recupera el envío | Completar |

El servidor almacena valores y muestra escrituras. No procesa `nueva_lectura`, no ejecuta ladder ni incrementa contadores. La interfaz tampoco mantiene el watchdog activo entre envíos: para una práctica continua debes usar un cliente persistente como el del tutorial siguiente.

**Reto:** captura tráfico en Wireshark sobre la interfaz de bucle local. Usa `tcp.port == 5020` como filtro de visualización; si hace falta, decodifica ese puerto como Modbus/TCP. Identifica FC15 y FC16. No esperes FC05/06 del cliente actual, que escribe en grupo.

**Criterio para avanzar:** puedes asociar un valor enviado con su dirección y demostrar pérdida y recuperación de conexión.

[Anterior](03-interfaz.md) · [Siguiente: PLC y HMI](05-plc-hmi.md)
