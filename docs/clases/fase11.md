# Clase Fase 11 — PLC en ladder (OpenPLC)

Duración estimada: 2 horas (más tiempo de laboratorio para la verificación en hardware/software real).

## Objetivos

Al terminar, el estudiante puede traducir una especificación de comportamiento (el ENUNCIADO) a un programa ladder completo con temporizadores, contadores y flancos, y entiende por qué el mapeo de direcciones Modbus↔IEC de un PLC concreto siempre debe verificarse contra la documentación de esa versión, no asumirse.

## Conceptos

- **Temporizador de pulso (TP) vs. temporizador de retardo (TON)**: un TP se dispara una vez y se mantiene encendido un tiempo fijo sin importar qué pase después en su entrada; un TON solo está activo mientras su entrada se mantenga activa. La talanquera y la luz roja necesitan un TP (tiempo fijo), no un TON.
- **Contador ascendente (CTU)**: acumula una cuenta cada vez que su entrada `CU` tiene un flanco de subida; se usa para los contadores de ingresos y rechazos, que nunca deben "perder" una cuenta ni contar de más.
- **Detector de flanco (R_TRIG)**: convierte una señal que se mantiene activa varios ciclos de scan en un pulso de un solo ciclo, indispensable para no re-disparar una acción (como abrir la talanquera) mientras la condición de entrada siga activa.
- **SET/RESET (enclavamiento)**: una marca que se activa con una condición y solo se desactiva con otra condición distinta (no automáticamente); se usa para la luz ámbar (activa con lectura dudosa, se apaga con la validación manual) y el bloqueo por emergencia.
- **Orden de evaluación en ST/ladder**: el valor de una variable en un renglón depende de en qué orden se ejecutaron los renglones anteriores en el mismo ciclo de scan; un error común es leer una marca después de haberla modificado en el mismo ciclo, obteniendo el valor nuevo en vez del que se necesitaba.

## Demostración paso a paso

Esta fase no tiene `pytest` (es lógica de PLC, no código Python), así que la verificación es manual sobre el software/hardware real:

1. Abrir `plc/openplc/mapa_modbus.md` y confirmar las direcciones contra la versión de OpenPLC instalada (Settings → Modbus Server).
2. Dibujar el ladder en OpenPLC Editor siguiendo `plc/openplc/ladder_paso_a_paso.md`, renglón por renglón (o importar/adaptar `control_acceso.st` si el editor lo permite).
3. Compilar y cargar el programa en OpenPLC Runtime.
4. Seguir el protocolo de `plc/openplc/pruebas.md` paso a paso, con la interfaz (`streamlit run app/interfaz.py`, destino Modbus TCP) enviando señales reales.

## Preguntas de verificación

1. **¿Por qué la talanquera se implementa con un temporizador TP y no con un TON?**
   Respuesta: un TON solo mantiene su salida activa mientras la entrada siga activa; como `nueva_lectura` se limpia (acuse) casi inmediatamente después de dispararse, un TON apenas alcanzaría a activarse un instante. El TP, en cambio, se dispara con un pulso de entrada y se mantiene encendido los 5 segundos completos sin importar qué pase con la entrada después.

2. **En el renglón 3, ¿por qué `validacion_abre_talanquera` se calcula antes de poner `lectura_dudosa_pendiente` en `FALSE`, y no después?**
   Respuesta: porque si se calculara después, la condición ya encontraría `lectura_dudosa_pendiente` en `FALSE` (recién reseteada) y la talanquera nunca se abriría por esta vía, aunque la validación manual sí haya ocurrido. El orden de las asignaciones dentro de un mismo ciclo de scan importa.

3. **¿Por qué el documento de mapeo de direcciones (`mapa_modbus.md`) insiste en que el docente lo confirme, en vez de dar las direcciones como definitivas?**
   Respuesta: porque el mapeo entre direcciones Modbus (coils, holding registers) y direcciones IEC (`%QX`, `%QW`, `%MW`) depende de la versión de OpenPLC Runtime, y ha cambiado entre versiones. Usar una dirección sin verificarla contra la instalación real puede hacer que el programa compile pero no reciba las señales del sistema de visión, sin ningún error visible.

## Reto para estudiantes

Agregar un segundo carril de entrada con su propia talanquera (según el ROADMAP): duplicar las salidas físicas (`Q0`-`Q3` de un segundo carril) y decidir si comparten o no las entradas de emergencia y validación manual.

**Criterios de evaluación:**
- El segundo carril usa un rango de direcciones IEC propio, documentado en una copia actualizada de `mapa_modbus.md`, sin chocar con el primero.
- Se justifica explícitamente si el botón de emergencia es compartido (una sola entrada detiene ambos carriles) o independiente, y por qué esa es la decisión de seguridad correcta.
- El protocolo de `pruebas.md` se extiende para verificar el segundo carril de forma independiente del primero.

---

[Fase anterior](fase10.md) · [Índice de guías](../README.md) · [Fase siguiente](fase12.md)
