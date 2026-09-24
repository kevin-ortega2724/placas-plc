(* ============================================================
   control_acceso.st - Control de acceso vehicular con pico y placa
   Fase 11. Texto estructurado (ST) equivalente al ladder del
   ENUNCIADO, para dibujar en OpenPLC Editor. Ver:
     - mapa_modbus.md      -> de donde salen las direcciones AT %...
     - ladder_paso_a_paso.md -> como dibujar cada renglon en el editor
     - src/placas/plc_simulado.py -> la misma logica, ya probada, en Python

   Dev-log de decisiones no evidentes:
   - La talanquera y la luz roja se implementan con TP (pulso no
     interrumpible), no con TON, porque deben quedar encendidas un
     tiempo fijo desde que se disparan, sin importar que las senales
     de entrada cambien antes de que termine el tiempo.
   - El renglon 3 calcula "validacion_abre_talanquera" ANTES de borrar
     lectura_dudosa_pendiente: si se calculara despues, la condicion ya
     estaria en FALSE y la talanquera nunca se abriria por este camino.
   ============================================================ *)
PROGRAM control_acceso
VAR
    (* --- Escritas por Modbus (cliente: sistema de vision) --- *)
    (* Direcciones a confirmar contra la version de OpenPLC instalada: ver mapa_modbus.md *)
    vehiculo_presente       AT %QX0.0 : BOOL;
    acceso_permitido        AT %QX0.1 : BOOL;
    acceso_denegado         AT %QX0.2 : BOOL;
    lectura_dudosa          AT %QX0.3 : BOOL;
    nueva_lectura           AT %QX0.4 : BOOL;
    codigo_decision         AT %QW0   : INT;
    confianza               AT %QW1   : INT;
    ultimo_digito           AT %QW2   : INT;
    watchdog_in             AT %QW3   : INT;

    (* --- Entradas fisicas del operador --- *)
    boton_validacion_manual AT %IX0.0 : BOOL;
    boton_emergencia        AT %IX0.1 : BOOL;

    (* --- Salidas fisicas --- *)
    Q0_talanquera           AT %QX1.0 : BOOL;
    Q1_luz_roja             AT %QX1.1 : BOOL;
    Q2_luz_ambar            AT %QX1.2 : BOOL;
    Q3_alarma_comunicacion  AT %QX1.3 : BOOL;

    (* --- Contadores legibles por el HMI de solo lectura (Fase 12) --- *)
    contador_ingresos       AT %QW10  : INT;
    contador_rechazos       AT %QW11  : INT;

    (* --- Temporizadores, contadores y detectores de flanco --- *)
    tp_talanquera   : TP;   (* renglones 1 y 3: talanquera abierta 5 s *)
    tp_luz_roja     : TP;   (* renglon 2: luz roja 3 s *)
    ton_watchdog    : TON;  (* renglon 5: 3 s sin cambio -> alarma *)
    ctu_ingresos    : CTU;
    ctu_rechazos    : CTU;

    flanco_permitido  : R_TRIG;  (* nueva_lectura AND acceso_permitido *)
    flanco_denegado   : R_TRIG;  (* nueva_lectura AND acceso_denegado *)
    flanco_dudosa     : R_TRIG;  (* nueva_lectura AND lectura_dudosa *)
    flanco_validacion : R_TRIG;  (* boton_validacion_manual (I0) *)

    validacion_abre_talanquera : BOOL;
    disparo_talanquera         : BOOL;
    lectura_dudosa_pendiente   : BOOL := FALSE;
    bloqueado                  : BOOL := FALSE;

    watchdog_anterior   : INT := -1;
    watchdog_sin_cambio : BOOL;
END_VAR

(* ============================================================
   Renglon 1: nueva_lectura AND acceso_permitido AND NOT bloqueado
              -> dispara apertura de talanquera y cuenta un ingreso
   ============================================================ *)
flanco_permitido(CLK := nueva_lectura AND acceso_permitido AND NOT bloqueado);
ctu_ingresos(CU := flanco_permitido.Q, R := FALSE, PV := 32767);
contador_ingresos := ctu_ingresos.CV;

(* ============================================================
   Renglon 2: nueva_lectura AND acceso_denegado
              -> luz roja 3 s y cuenta un rechazo
   ============================================================ *)
flanco_denegado(CLK := nueva_lectura AND acceso_denegado);
tp_luz_roja(IN := flanco_denegado.Q, PT := T#3s);
Q1_luz_roja := tp_luz_roja.Q;
ctu_rechazos(CU := flanco_denegado.Q, R := FALSE, PV := 32767);
contador_rechazos := ctu_rechazos.CV;

(* ============================================================
   Renglon 3: lectura_dudosa -> SET luz ambar (Q2); boton de
              validacion manual (I0) -> RESET luz ambar y abre
              la talanquera (comparte el TP del renglon 1)
   ============================================================ *)
flanco_dudosa(CLK := nueva_lectura AND lectura_dudosa);
IF flanco_dudosa.Q THEN
    lectura_dudosa_pendiente := TRUE;
END_IF;

flanco_validacion(CLK := boton_validacion_manual);
validacion_abre_talanquera := lectura_dudosa_pendiente AND flanco_validacion.Q;
IF validacion_abre_talanquera THEN
    lectura_dudosa_pendiente := FALSE;
END_IF;
Q2_luz_ambar := lectura_dudosa_pendiente;

(* ============================================================
   Renglon 4: acuse de nueva_lectura (handshake). Se limpia
   despues de haberla usado en los renglones 1 a 3 de este mismo
   ciclo de scan, para no perder el flanco.
   ============================================================ *)
nueva_lectura := FALSE;

(* Disparo compartido de la talanquera: renglon 1 O renglon 3 *)
disparo_talanquera := flanco_permitido.Q OR (validacion_abre_talanquera AND NOT bloqueado);
tp_talanquera(IN := disparo_talanquera, PT := T#5s);

(* ============================================================
   Renglon 5: si el watchdog no cambia durante 3 s -> alarma Q3
              y la talanquera permanece cerrada
   ============================================================ *)
watchdog_sin_cambio := (watchdog_in = watchdog_anterior);
ton_watchdog(IN := watchdog_sin_cambio, PT := T#3s);
Q3_alarma_comunicacion := ton_watchdog.Q;
watchdog_anterior := watchdog_in;

(* ============================================================
   Renglon 6: boton de emergencia (I1) bloquea el sistema (SET).
   Reto sugerido: agregar una entrada de rearme explicita en vez
   de depender de reiniciar el programa para desbloquear.
   ============================================================ *)
IF boton_emergencia THEN
    bloqueado := TRUE;
END_IF;

(* La talanquera solo abre si el pulso esta activo, el sistema no
   esta bloqueado por emergencia y no hay alarma de comunicacion *)
Q0_talanquera := tp_talanquera.Q AND NOT bloqueado AND NOT Q3_alarma_comunicacion;
END_PROGRAM
