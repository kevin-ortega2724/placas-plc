"""Comunicacion Modbus TCP con el PLC (Fase 10).

El sistema de vision es el cliente Modbus TCP; el PLC (o, para pruebas,
hmi/servidor_prueba.py) es el servidor. Ver docs/modbus.md para las
direcciones y los codigos de funcion usados.
"""
from __future__ import annotations

import threading
import time

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from placas.senales import Senales, a_modbus

DIRECCION_COIL_ACUSE = 4
DIRECCION_REGISTRO_WATCHDOG = 3


class ClienteModbusAcceso:
    """Cliente Modbus TCP que envia las senales del sistema de vision al PLC."""

    def __init__(
        self,
        host: str,
        puerto: int,
        unidad: int,
        intentos_conexion: int = 3,
        tiempo_espera_s: float = 3.0,
    ) -> None:
        self._unidad = unidad
        self._intentos_conexion = intentos_conexion
        self._tiempo_espera_s = tiempo_espera_s
        self._cliente = ModbusTcpClient(host, port=puerto, timeout=tiempo_espera_s)
        self._watchdog_valor = 0
        self._hilo_watchdog: threading.Thread | None = None
        self._detener_watchdog = threading.Event()

    def conectar(self) -> bool:
        """Intenta conectar al servidor Modbus, reintentando si falla."""
        for intento in range(1, self._intentos_conexion + 1):
            if self._cliente.connect():
                return True
            print(f"Intento {intento}/{self._intentos_conexion} de conexion al PLC fallido.")
            if intento < self._intentos_conexion:
                time.sleep(self._tiempo_espera_s)
        return False

    def enviar(self, senales: Senales) -> bool:
        """Escribe los coils (FC15, write_coils) y registros (FC16,
        write_registers) de senales en las direcciones del ENUNCIADO.

        No detiene la interfaz si falla: registra el error y devuelve False.
        """
        coils, registros = a_modbus(senales)
        try:
            self._cliente.write_coils(0, coils, slave=self._unidad)
            self._cliente.write_registers(0, registros, slave=self._unidad)
            return True
        except ModbusException as error:
            print(f"Error al escribir en el PLC: {error}")
            return False

    def leer_acuse(self) -> bool | None:
        """Lee el coil 4 (nueva_lectura) para saber si el PLC ya la proceso.

        Devuelve None si hay un error de comunicacion.
        """
        try:
            resultado = self._cliente.read_coils(DIRECCION_COIL_ACUSE, count=1, slave=self._unidad)
            if resultado.isError():
                return None
            return bool(resultado.bits[0])
        except ModbusException as error:
            print(f"Error al leer el acuse del PLC: {error}")
            return None

    def iniciar_watchdog(self, periodo_s: float) -> None:
        """Inicia un hilo que incrementa el registro watchdog cada periodo_s."""

        def _bucle() -> None:
            while not self._detener_watchdog.is_set():
                self._watchdog_valor = (self._watchdog_valor + 1) % 65536
                try:
                    self._cliente.write_registers(
                        DIRECCION_REGISTRO_WATCHDOG, [self._watchdog_valor], slave=self._unidad
                    )
                except ModbusException:
                    pass
                self._detener_watchdog.wait(periodo_s)

        self._hilo_watchdog = threading.Thread(target=_bucle, daemon=True)
        self._hilo_watchdog.start()

    def detener(self) -> None:
        """Detiene el hilo de watchdog (si esta activo) y cierra la conexion."""
        self._detener_watchdog.set()
        if self._hilo_watchdog is not None:
            self._hilo_watchdog.join(timeout=1.0)
        self._cliente.close()

    def __enter__(self) -> "ClienteModbusAcceso":
        self.conectar()
        return self

    def __exit__(self, *_excepcion) -> None:
        self.detener()
