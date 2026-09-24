"""PLC simulado en Python (Fase 08).

Imita la estructura de un programa ladder: una funcion por renglon, con
un comentario que describe el renglon equivalente, para que despues sea
facil de traducir a OpenPLC (Fase 11). Se ejecuta ciclicamente llamando
a ciclo(dt) cada 50 ms; dt se recibe como parametro (no time.sleep
dentro de la logica) para poder probarlo sin esperas reales.
"""
from __future__ import annotations

from placas.senales import Senales

DURACION_TALANQUERA_S = 5.0
DURACION_LUZ_ROJA_S = 3.0
TIEMPO_MAXIMO_SIN_WATCHDOG_S = 3.0


class PlcSimulado:
    """Simula el PLC del ENUNCIADO: talanquera, luces, contadores y watchdog."""

    def __init__(self) -> None:
        self.senales: Senales | None = None

        # Salidas (Q0-Q3)
        self.q0_talanquera = False
        self.q1_luz_roja = False
        self.q2_luz_ambar = False
        self.q3_alarma_comunicacion = False

        # Contadores (CTU)
        self.contador_ingresos = 0
        self.contador_rechazos = 0

        # Entradas del operador (I0, I1)
        self.boton_validacion_manual = False
        self.boton_emergencia = False

        self.bloqueado = False

        self._tiempo_restante_talanquera = 0.0
        self._tiempo_restante_luz_roja = 0.0
        self._lectura_dudosa_pendiente = False
        self._ultimo_watchdog: int | None = None
        self._tiempo_sin_cambio_watchdog = 0.0

    def recibir_senales(self, senales: Senales) -> None:
        """Entrega al PLC las senales que enviaria el sistema de vision."""
        self.senales = senales

    def ciclo(self, dt: float) -> None:
        """Ejecuta un ciclo de scan del PLC (por defecto, cada 50 ms)."""
        if self.senales is not None:
            self._renglon_1_abrir_talanquera()
            self._renglon_2_luz_roja()
            self._renglon_3_luz_ambar()
            self._renglon_5_watchdog(dt)

        self._renglon_6_emergencia()
        self._actualizar_temporizadores(dt)

        if self.senales is not None:
            self._renglon_4_acuse_nueva_lectura()

    def _renglon_1_abrir_talanquera(self) -> None:
        # Renglon 1: nueva_lectura AND acceso_permitido -> TON 5s en Q0, CTU ingresos
        if self.senales.nueva_lectura and self.senales.acceso_permitido and not self.bloqueado:
            self._tiempo_restante_talanquera = DURACION_TALANQUERA_S
            self.contador_ingresos += 1

    def _renglon_2_luz_roja(self) -> None:
        # Renglon 2: nueva_lectura AND acceso_denegado -> TON 3s en Q1, CTU rechazos
        if self.senales.nueva_lectura and self.senales.acceso_denegado:
            self._tiempo_restante_luz_roja = DURACION_LUZ_ROJA_S
            self.contador_rechazos += 1

    def _renglon_3_luz_ambar(self) -> None:
        # Renglon 3: lectura_dudosa -> SET Q2; boton_validacion_manual (I0) -> RESET Q2 y abre talanquera
        if self.senales.nueva_lectura and self.senales.lectura_dudosa:
            self._lectura_dudosa_pendiente = True

        if not self._lectura_dudosa_pendiente:
            return

        if self.boton_validacion_manual:
            self._lectura_dudosa_pendiente = False
            self.q2_luz_ambar = False
            if not self.bloqueado:
                self._tiempo_restante_talanquera = DURACION_TALANQUERA_S
        else:
            self.q2_luz_ambar = True

    def _renglon_4_acuse_nueva_lectura(self) -> None:
        # Renglon 4: tras procesar la lectura, nueva_lectura = 0 (acuse de recibo)
        self.senales.nueva_lectura = False

    def _renglon_5_watchdog(self, dt: float) -> None:
        # Renglon 5: si el watchdog no cambia en 3 s -> alarma Q3, talanquera bloqueada
        if self.senales.watchdog != self._ultimo_watchdog:
            self._ultimo_watchdog = self.senales.watchdog
            self._tiempo_sin_cambio_watchdog = 0.0
            self.q3_alarma_comunicacion = False
        else:
            self._tiempo_sin_cambio_watchdog += dt
            if self._tiempo_sin_cambio_watchdog >= TIEMPO_MAXIMO_SIN_WATCHDOG_S - 1e-9:
                self.q3_alarma_comunicacion = True
                self._tiempo_restante_talanquera = 0.0

    def _renglon_6_emergencia(self) -> None:
        # Renglon 6: boton de emergencia (I1) cierra la talanquera y bloquea el sistema
        if self.boton_emergencia:
            self.bloqueado = True
            self._tiempo_restante_talanquera = 0.0

    def _actualizar_temporizadores(self, dt: float) -> None:
        self._tiempo_restante_talanquera = max(0.0, self._tiempo_restante_talanquera - dt)
        self._tiempo_restante_luz_roja = max(0.0, self._tiempo_restante_luz_roja - dt)
        self.q0_talanquera = self._tiempo_restante_talanquera > 0.0 and not self.bloqueado
        self.q1_luz_roja = self._tiempo_restante_luz_roja > 0.0

    def reiniciar_emergencia(self) -> None:
        """Desbloquea el sistema despues de una parada de emergencia."""
        self.bloqueado = False

    def imprimir_estado(self) -> None:
        print(
            f"Q0 talanquera={self.q0_talanquera} "
            f"Q1 luz_roja={self.q1_luz_roja} "
            f"Q2 luz_ambar={self.q2_luz_ambar} "
            f"Q3 alarma_comunicacion={self.q3_alarma_comunicacion} | "
            f"ingresos={self.contador_ingresos} rechazos={self.contador_rechazos}"
        )


if __name__ == "__main__":
    import time

    from placas.reglas import CodigoDecision, Decision
    from placas.senales import a_senales

    plc = PlcSimulado()
    decision_demo = Decision(CodigoDecision.PERMITIDO, "PERMITIDO", "demostracion", 3)
    senales_demo = a_senales(decision_demo, None)
    senales_demo.watchdog = 0
    plc.recibir_senales(senales_demo)

    print("Demostracion: una lectura PERMITIDO, 3 s de simulacion (ciclo cada 50 ms).")
    for paso in range(60):
        senales_demo.watchdog = paso  # simula al sistema de vision incrementando el watchdog
        plc.ciclo(0.05)
        plc.imprimir_estado()
        time.sleep(0.05)
