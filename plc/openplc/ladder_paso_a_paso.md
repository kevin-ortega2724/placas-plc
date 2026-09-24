# Ladder paso a paso (para dibujar en OpenPLC Editor)

`control_acceso.st` es el texto estructurado equivalente. Esta guía describe cómo dibujar **la misma lógica** como diagrama de contactos (ladder) en OpenPLC Editor, renglón por renglón. Los nombres de variable coinciden con `control_acceso.st` y las direcciones con `mapa_modbus.md`.

Antes de empezar: cree las variables globales de la tabla de `mapa_modbus.md` en OpenPLC Editor (menú de variables del proyecto), con sus direcciones `%QX`/`%QW`/`%IX`.

## Renglón 1 — Abrir talanquera y contar ingreso

```
  vehiculo_presente   acceso_permitido      bloqueado          R_TRIG          CTU
  (no se usa aqui,        │                    │           ┌─────────┐    ┌─────────┐
   informativo)      ──┤ ├──┤ ├───────────┤/├──┤ CLK   Q ├──┤ CU   CV ├── contador_ingresos
  nueva_lectura            │                                └─────────┘    │  Q      │
  ──┤ ├────────────────────┘                                               └────┬────┘
                                                                                  │
                                                                          (Q no se usa: PV=32767)
```

- **Contactos en serie**: `nueva_lectura`, `acceso_permitido`, `NOT bloqueado`.
- Esa combinación entra al **CLK** de un bloque **R_TRIG** (detector de flanco de subida) llamado `flanco_permitido`.
- La salida `Q` del `R_TRIG` entra al **CU** (count up) de un bloque **CTU** llamado `ctu_ingresos`, con `PV := 32767` (no nos interesa que "se llene"; solo acumular).
- `ctu_ingresos.CV` (valor actual) se copia a la salida de memoria `contador_ingresos` (`%QW10`).
- La misma salida `flanco_permitido.Q` también alimenta el disparo compartido de la talanquera (ver más abajo).

## Renglón 2 — Luz roja y contar rechazo

```
  nueva_lectura   acceso_denegado      R_TRIG              TP                    CTU
  ──┤ ├──────────────┤ ├──────────┬──┤ CLK   Q ├──┬──┤ IN      Q ├── Q1_luz_roja
                                   │  └─────────┘  │  │  PT=T#3s │
                                   │                └──┤ CU   CV ├── contador_rechazos
                                   │                    └─────────┘
```

- Contactos en serie: `nueva_lectura`, `acceso_denegado` → `R_TRIG` (`flanco_denegado`).
- `flanco_denegado.Q` alimenta un **TP** (pulso, no interrumpible) de 3 s: mientras el pulso está activo, `Q1_luz_roja := TP.Q`.
- La misma señal `flanco_denegado.Q` alimenta el `CU` de `ctu_rechazos`; su `CV` va a `contador_rechazos` (`%QW11`).

## Renglón 3 — Luz ámbar con validación manual

```
  nueva_lectura   lectura_dudosa    R_TRIG                SET
  ──┤ ├──────────────┤ ├──────────┤ CLK  Q├──────────(S)── lectura_dudosa_pendiente

  boton_validacion_manual    R_TRIG            lectura_dudosa_pendiente     RESET
  ──┤ ├─────────────────────┤ CLK  Q├──────────────┤ ├───────────────(R)── lectura_dudosa_pendiente

  lectura_dudosa_pendiente ──────────────────────────────────────────────── Q2_luz_ambar
```

- Primer bloque: `nueva_lectura AND lectura_dudosa` → `R_TRIG` (`flanco_dudosa`) → **SET** de la marca interna `lectura_dudosa_pendiente`.
- Segundo bloque: `boton_validacion_manual` → `R_TRIG` (`flanco_validacion`); en serie con el contacto de `lectura_dudosa_pendiente`, activa el **RESET** de esa misma marca.
- `lectura_dudosa_pendiente` se copia directo a la bobina `Q2_luz_ambar` (mientras esté activa, la luz ámbar queda encendida).
- **Importante**: la condición que abre la talanquera (`validacion_abre_talanquera`) se calcula leyendo `lectura_dudosa_pendiente` **antes** del RESET de este mismo renglón, no después — en el diagrama, tome la salida del contacto en serie (`lectura_dudosa_pendiente AND flanco_validacion.Q`), no la marca ya reseteada.

## Renglón 4 — Acuse de nueva_lectura

```
  (siempre)  ──────────────────────────────────────(  )── nueva_lectura := FALSE
```

- Una bobina incondicional (o una asignación directa, si su versión de OpenPLC Editor lo permite en un bloque FBD/ST embebido) que pone `nueva_lectura` en `FALSE` al final del ciclo, después de haberla leído en los renglones 1 a 3.

## Disparo compartido de la talanquera

```
  flanco_permitido.Q ──┐
                        OR ──────┤ IN      Q ├── (a Q0, ver mas abajo)
  validacion_abre_talanquera ────┘  TP, PT=T#5s
       AND NOT bloqueado
```

## Renglón 5 — Watchdog (3 s sin cambio → alarma)

```
  watchdog_in = watchdog_anterior          TON                  
  ──────────┤ = ├──────────────────────┤ IN      Q ├────────── Q3_alarma_comunicacion
                                         │  PT=T#3s │
                                         └──────────┘
  (al final del renglon: watchdog_anterior := watchdog_in)
```

- Comparador `=` entre `watchdog_in` (valor que llega de Modbus) y `watchdog_anterior` (el valor del ciclo pasado).
- Si son iguales (no cambió), el **TON** acumula tiempo; si acumula 3 s seguidos sin cambio, `Q3_alarma_comunicacion` se activa.
- Al final de este renglón, actualice `watchdog_anterior := watchdog_in` para el próximo ciclo.

## Renglón 6 — Emergencia

```
  boton_emergencia ──────────────────────────────────────(S)── bloqueado
```

- Contacto de `boton_emergencia` → **SET** de la marca `bloqueado` (queda enclavada; no hay RESET automático en la versión base — ver el reto de la Fase 08).

## Salida final de la talanquera

```
  tp_talanquera.Q   NOT bloqueado   NOT Q3_alarma_comunicacion
  ──┤ ├────────────────┤ ├───────────────┤ ├───────────────────( )── Q0_talanquera
```

Los tres contactos en serie: el pulso de apertura debe estar activo, el sistema no debe estar bloqueado por emergencia, y no debe haber alarma de comunicación.
