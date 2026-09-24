# Enunciado: control de acceso vehicular con pico y placa

## Contexto

El parqueadero de un campus universitario tiene una talanquera en la entrada. Se quiere automatizar el acceso: una cámara captura la parte frontal del vehículo, un sistema de visión lee la placa y un PLC decide si abre la talanquera.

El municipio aplica una medida de **pico y placa** para vehículos particulares: según el día de la semana, los vehículos cuya placa termina en ciertos dígitos no pueden circular en determinados horarios. El parqueadero debe respetar esa medida.

> Las reglas de este enunciado son didácticas y se configuran en `config/reglas.yaml`. No corresponden necesariamente a la medida vigente en ninguna ciudad.

## Alcance

- Vehículos particulares tipo automóvil, placa colombiana de formato `ABC123` (tres letras y tres números).
- Las motocicletas (formato `ABC12D`) quedan como extensión opcional.

## Reglas de acceso

El sistema evalúa las reglas en este orden y se detiene en la primera que aplique:

| Prioridad | Condición | Decisión | Código |
|---|---|---|---|
| 1 | No se detecta vehículo o placa en la imagen | `SIN_VEHICULO` | 0 |
| 2 | La placa se detectó pero la confianza del OCR es menor al mínimo configurado, o el texto no cumple el formato | `LECTURA_DUDOSA` | 1 |
| 3 | La placa está en la lista de reportados | `REPORTADO` | 2 |
| 4 | La placa no está en la lista de autorizados | `NO_AUTORIZADO` | 3 |
| 5 | El último dígito está restringido hoy, la hora está dentro del horario de pico y placa y la placa no tiene excepción | `PICO_Y_PLACA` | 4 |
| 6 | Ninguna de las anteriores | `PERMITIDO` | 5 |

Configuración inicial de pico y placa (editable):

| Día | Dígitos restringidos |
|---|---|
| Lunes | 1 y 2 |
| Martes | 3 y 4 |
| Miércoles | 5 y 6 |
| Jueves | 7 y 8 |
| Viernes | 9 y 0 |
| Sábado, domingo y festivos | Sin restricción |

Horarios de restricción: 06:00 a 09:00 y 16:00 a 20:00.

## Señales hacia el PLC

La decisión se traduce en señales. El sistema de visión es el cliente Modbus TCP y el PLC es el servidor.

| Dirección | Nombre | Tipo | Descripción |
|---|---|---|---|
| Coil 0 | `vehiculo_presente` | Bit | Hay vehículo con placa detectada |
| Coil 1 | `acceso_permitido` | Bit | Decisión = `PERMITIDO` |
| Coil 2 | `acceso_denegado` | Bit | Decisión = `REPORTADO`, `NO_AUTORIZADO` o `PICO_Y_PLACA` |
| Coil 3 | `lectura_dudosa` | Bit | Decisión = `LECTURA_DUDOSA` |
| Coil 4 | `nueva_lectura` | Bit | Pulso: hay un resultado nuevo. El PLC lo pone en 0 como acuse de recibo |
| Holding 0 | `codigo_decision` | Entero 0 a 5 | Código de la tabla de reglas |
| Holding 1 | `confianza` | Entero 0 a 1000 | Confianza del OCR × 1000 |
| Holding 2 | `ultimo_digito` | Entero 0 a 9 | Último dígito de la placa |
| Holding 3 | `watchdog` | Entero | Contador que el sistema de visión incrementa cada segundo |

## Lógica del PLC (ladder)

1. Si `nueva_lectura` y `acceso_permitido`: abrir talanquera (Q0) durante 5 s y sumar 1 al contador de ingresos.
2. Si `nueva_lectura` y `acceso_denegado`: luz roja (Q1) durante 3 s y sumar 1 al contador de rechazos.
3. Si `lectura_dudosa`: luz ámbar (Q2) hasta que el operador pulse el botón de validación manual (I0), que abre la talanquera.
4. Tras procesar una lectura, el PLC escribe `nueva_lectura = 0`.
5. Si `watchdog` no cambia durante 3 s: alarma de falla de comunicación (Q3) y la talanquera permanece cerrada.
6. El botón de emergencia (I1) cierra la talanquera y bloquea el sistema.

## Entregables por fase

Ver [`docs/ROADMAP.md`](docs/ROADMAP.md).
