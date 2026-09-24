"""Servidor Modbus TCP de prueba (Fase 10).

Imprime cada escritura que recibe, para poder probar el cliente Modbus
del sistema de vision (src/placas/comunicacion.py) sin necesitar un PLC
real ni OpenPLC instalado.
"""
from __future__ import annotations

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext, ModbusSlaveContext
from pymodbus.server import StartTcpServer


class _BloqueImpresor(ModbusSequentialDataBlock):
    """Bloque de datos que imprime cada escritura recibida, para depurar."""

    def __init__(self, nombre: str, direccion: int, valores: list) -> None:
        self._nombre = nombre
        super().__init__(direccion, valores)

    def setValues(self, address: int, values) -> None:
        print(f"[{self._nombre}] escritura en direccion {address}: {values}")
        super().setValues(address, values)


def crear_contexto() -> ModbusServerContext:
    """Crea el contexto del servidor con 16 coils y 16 holding registers."""
    coils = _BloqueImpresor("coils", 0, [False] * 16)
    registros = _BloqueImpresor("registros", 0, [0] * 16)
    # zero_mode=True: la direccion 0 del protocolo es la direccion 0 del
    # bloque de datos (sin el desplazamiento +1 historico de Modbus).
    esclavo = ModbusSlaveContext(co=coils, hr=registros, zero_mode=True)
    return ModbusServerContext(slaves=esclavo, single=True)


def iniciar_servidor(host: str, puerto: int) -> None:
    """Arranca el servidor Modbus TCP (llamada bloqueante)."""
    contexto = crear_contexto()
    print(f"Servidor Modbus de prueba escuchando en {host}:{puerto}")
    StartTcpServer(context=contexto, address=(host, puerto))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Servidor Modbus TCP de prueba.")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument(
        "--puerto",
        type=int,
        default=5020,
        help="Puerto TCP (los puertos menores a 1024, como el 502 del ENUNCIADO, requieren privilegios de root en Linux).",
    )
    argumentos = parser.parse_args()
    iniciar_servidor(argumentos.host, argumentos.puerto)
