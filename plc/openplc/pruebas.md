# Protocolo de pruebas: `control_acceso` en OpenPLC

Prerrequisitos: OpenPLC Editor y OpenPLC Runtime instalados; el programa `control_acceso` (dibujado a partir de `ladder_paso_a_paso.md` o importado desde `control_acceso.st`) compilado y cargado en el Runtime; el Runtime con el servidor Modbus habilitado (Settings → Modbus Server, puerto 502 o el que confirme según `mapa_modbus.md`).

## 1. Verificación de direcciones (antes de cualquier prueba funcional)

1. En OpenPLC Runtime, revise en **Settings** el rango de direcciones Modbus que expone.
2. Con `hmi/servidor_prueba.py` **apagado** (no lo necesita aquí: el servidor Modbus es OpenPLC), use un cliente Modbus genérico (o una sesión rápida de Python con `pymodbus`) para escribir manualmente el coil 1 (`acceso_permitido`) en `TRUE` y confirmar que el monitor de variables de OpenPLC Runtime lo refleje en `%QX0.1`.
3. Si no coincide, ajuste las direcciones `AT %...` en el programa y vuelva a compilar antes de seguir.

## 2. Talanquera y contador de ingresos (Renglón 1)

1. Con la interfaz (`streamlit run app/interfaz.py`, destino "Modbus TCP", `config/reglas.yaml` apuntando al host/puerto del Runtime) o un cliente Modbus manual, envíe una decisión `PERMITIDO`: coils `[True, True, False, False, True]` (vehiculo_presente, acceso_permitido, acceso_denegado, lectura_dudosa, nueva_lectura).
2. **Verificar**: `Q0_talanquera` (`%QX1.0`) se enciende y el contador `contador_ingresos` (`%QW10`) sube en 1.
3. Espere 5 segundos sin enviar nada más. **Verificar**: `Q0_talanquera` se apaga solo.
4. Repita el envío 3 veces seguidas. **Verificar**: el contador sube exactamente 3 (uno por cada pulso de `nueva_lectura`, no más).

## 3. Luz roja y contador de rechazos (Renglón 2)

1. Envíe una decisión denegada (por ejemplo `NO_AUTORIZADO`): coils `[True, False, True, False, True]`.
2. **Verificar**: `Q1_luz_roja` (`%QX1.1`) se enciende y `contador_rechazos` (`%QW11`) sube en 1.
3. Espere 3 segundos. **Verificar**: `Q1_luz_roja` se apaga sola.

## 4. Luz ámbar y validación manual (Renglón 3)

1. Envíe una decisión `LECTURA_DUDOSA`: coils `[True, False, False, True, True]`.
2. **Verificar**: `Q2_luz_ambar` (`%QX1.2`) se enciende y permanece encendida (no se apaga sola).
3. Active el botón de validación manual (`%IX0.0`, físico o forzado desde el monitor de variables de OpenPLC).
4. **Verificar**: `Q2_luz_ambar` se apaga y `Q0_talanquera` se enciende durante 5 s.

## 5. Watchdog (Renglón 5)

1. Con la interfaz o un script enviando el registro `watchdog` (holding 3) incrementándose cada segundo, **verificar** que `Q3_alarma_comunicacion` (`%QX1.3`) permanezca apagada.
2. Deje de enviar (cierre la interfaz o el script) y espere al menos 3 segundos.
3. **Verificar**: `Q3_alarma_comunicacion` se enciende.
4. Con la alarma activa, intente abrir la talanquera enviando una decisión `PERMITIDO`. **Verificar**: `Q0_talanquera` **no** se enciende (la alarma la bloquea).
5. Reanude el envío del watchdog. **Verificar**: la alarma se apaga y la talanquera vuelve a operar con normalidad.

## 6. Emergencia (Renglón 6)

1. Con la talanquera abierta (repita el paso 2), active el botón de emergencia (`%IX0.1`).
2. **Verificar**: `Q0_talanquera` se apaga de inmediato.
3. Intente abrir la talanquera de nuevo enviando una decisión `PERMITIDO`. **Verificar**: no se abre (el sistema queda bloqueado).
4. Para liberar el bloqueo en esta versión base, reinicie el programa en el Runtime (recuerde: el reto de la Fase 08/11 es agregar una entrada de rearme explícita en vez de depender de un reinicio).

## 7. Registro de resultados

Para cada paso, anote: **Esperado / Obtenido / ¿Coincide?**. Si algún paso no coincide, antes de sospechar del ladder revise primero `mapa_modbus.md` (la causa más común es una dirección `%QW`/`%MW` mal confirmada para la versión de OpenPLC instalada).
