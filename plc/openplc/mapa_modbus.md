# Mapa de direcciones: Modbus (ENUNCIADO) ↔ IEC 61131 (OpenPLC)

> **Advertencia de version:** el mapeo entre direcciones Modbus y direcciones IEC (`%QX`, `%IX`, `%QW`, `%IW`, `%MW`) que usa el servidor Modbus interno de OpenPLC Runtime ha cambiado entre versiones. Lo que sigue es el mapeo mas comun en las versiones recientes (OpenPLC Runtime v3), pero **el docente debe confirmarlo** abriendo OpenPLC Runtime → pestaña **Settings** → **Modbus Server**, y comparando contra la version realmente instalada antes de dar esto por definitivo. Si no coincide, ajuste las direcciones `AT %...` en `control_acceso.st` — la logica interna no cambia, solo las direcciones.

## Por que dos bancos de direcciones distintos

El cliente Modbus (`src/placas/comunicacion.py`, sistema de vision) **escribe** los coils 0-4 y los holding registers 0-3 del ENUNCIADO. Esos valores son *entradas* para la logica del PLC (le dicen que decidio el sistema de vision), pero Modbus solo tiene dos tipos de dato escribibles por un cliente externo: coils (bits) y holding registers (palabras). En OpenPLC, el rango escribible por Modbus que corresponde a coils es `%QX` (aunque conceptualmente estos bits funcionan aqui como entradas de datos, no como salidas fisicas).

Para no chocar direcciones, este proyecto separa:
- **Banco 0** (`%QX0.x`, `%QW0-3`): lo escribe el sistema de vision por Modbus. El ladder solo lo *lee*.
- **Banco 1** (`%QX1.x`, `%QW10-11`): son las salidas fisicas reales (talanquera, luces, contadores) que decide el ladder. Un HMI de solo lectura (Fase 12) las puede leer por Modbus sin chocar con el banco 0.
- **`%IX0.x`**: entradas fisicas del operador (boton de validacion manual, boton de emergencia), cableadas al modulo de entradas del PLC, no llegan por Modbus.

## Senales que escribe el sistema de vision (banco 0, solo lectura para el ladder)

| Direccion Modbus (ENUNCIADO) | Direccion IEC sugerida | Variable en `control_acceso.st` |
|---|---|---|
| Coil 0 `vehiculo_presente` | `%QX0.0` | `vehiculo_presente` |
| Coil 1 `acceso_permitido` | `%QX0.1` | `acceso_permitido` |
| Coil 2 `acceso_denegado` | `%QX0.2` | `acceso_denegado` |
| Coil 3 `lectura_dudosa` | `%QX0.3` | `lectura_dudosa` |
| Coil 4 `nueva_lectura` | `%QX0.4` | `nueva_lectura` |
| Holding 0 `codigo_decision` | `%QW0` (a confirmar; en algunas instalaciones puede ser `%MW0`) | `codigo_decision` |
| Holding 1 `confianza` | `%QW1` | `confianza` |
| Holding 2 `ultimo_digito` | `%QW2` | `ultimo_digito` |
| Holding 3 `watchdog` | `%QW3` | `watchdog_in` |

## Entradas fisicas del operador

| Entrada del ENUNCIADO | Direccion IEC | Variable |
|---|---|---|
| I0 boton de validacion manual | `%IX0.0` | `boton_validacion_manual` |
| I1 boton de emergencia | `%IX0.1` | `boton_emergencia` |

## Salidas fisicas (banco 1, las decide el ladder)

| Salida del ENUNCIADO | Direccion IEC | Variable |
|---|---|---|
| Q0 talanquera | `%QX1.0` | `Q0_talanquera` |
| Q1 luz roja | `%QX1.1` | `Q1_luz_roja` |
| Q2 luz ambar | `%QX1.2` | `Q2_luz_ambar` |
| Q3 alarma de comunicacion | `%QX1.3` | `Q3_alarma_comunicacion` |

## Contadores legibles por el HMI de solo lectura (Fase 12)

| Dato | Direccion IEC sugerida |
|---|---|
| Contador de ingresos | `%QW10` |
| Contador de rechazos | `%QW11` |

## Que debe confirmar el docente antes de usar esto en clase

1. Abrir OpenPLC Runtime → **Settings** → verificar el rango de direcciones que el servidor Modbus interno expone para coils y holding registers, y si holding registers se mapean a `%QW` o a `%MW` en la version instalada.
2. Confirmar que el rango `%QX0.0-%QX0.4` y `%QW0-%QW3` no colisione con otro programa o dispositivo Modbus ya configurado en el Runtime.
3. Verificar en el editor que las declaraciones `AT %...` de `control_acceso.st` compilen sin error de direccion invalida para la version de OpenPLC Editor instalada.
