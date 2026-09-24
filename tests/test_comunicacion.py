"""Pruebas de comunicacion Modbus TCP (Fase 10).

Usan un servidor Modbus TCP real (hmi/servidor_prueba.py) en localhost,
en un puerto alto para no requerir privilegios de root, para verificar
que un cliente externo pueda leer lo que escribe ClienteModbusAcceso.
"""
import threading
import time

import pytest
from pymodbus.client import ModbusTcpClient
from pymodbus.server import ServerStop

from hmi.servidor_prueba import iniciar_servidor
from placas.comunicacion import ClienteModbusAcceso
from placas.ocr import Lectura
from placas.reglas import CodigoDecision, Decision
from placas.senales import a_senales

PUERTO_PRUEBA = 15020


@pytest.fixture(scope="module")
def servidor_modbus():
    hilo = threading.Thread(
        target=iniciar_servidor, args=("127.0.0.1", PUERTO_PRUEBA), daemon=True
    )
    hilo.start()
    time.sleep(0.3)  # da tiempo a que el servidor abra el puerto
    yield
    ServerStop()
    hilo.join(timeout=2)


def test_enviar_escribe_coils_y_registros_legibles_por_otro_cliente(servidor_modbus):
    decision = Decision(CodigoDecision.PERMITIDO, "PERMITIDO", "motivo", 3)
    senales = a_senales(decision, Lectura("ABC123", "ABC123", 0.95, True, "carro"))
    senales.watchdog = 7

    with ClienteModbusAcceso("127.0.0.1", PUERTO_PRUEBA, unidad=1) as cliente:
        assert cliente.enviar(senales) is True

    cliente_externo = ModbusTcpClient("127.0.0.1", port=PUERTO_PRUEBA)
    assert cliente_externo.connect()
    coils = cliente_externo.read_coils(0, count=5, slave=1)
    registros = cliente_externo.read_holding_registers(0, count=4, slave=1)
    cliente_externo.close()

    assert list(coils.bits[:5]) == [True, True, False, False, True]
    assert list(registros.registers) == [5, 950, 3, 7]


def test_leer_acuse_lee_el_coil_4(servidor_modbus):
    escritor = ModbusTcpClient("127.0.0.1", port=PUERTO_PRUEBA)
    assert escritor.connect()

    escritor.write_coil(4, True, slave=1)
    with ClienteModbusAcceso("127.0.0.1", PUERTO_PRUEBA, unidad=1) as cliente:
        assert cliente.leer_acuse() is True

    escritor.write_coil(4, False, slave=1)
    with ClienteModbusAcceso("127.0.0.1", PUERTO_PRUEBA, unidad=1) as cliente:
        assert cliente.leer_acuse() is False

    escritor.close()


def test_watchdog_incrementa_el_registro_periodicamente(servidor_modbus):
    with ClienteModbusAcceso("127.0.0.1", PUERTO_PRUEBA, unidad=1) as cliente:
        cliente.iniciar_watchdog(periodo_s=0.05)
        time.sleep(0.3)
        cliente.detener()

    cliente_externo = ModbusTcpClient("127.0.0.1", port=PUERTO_PRUEBA)
    assert cliente_externo.connect()
    registro = cliente_externo.read_holding_registers(3, count=1, slave=1)
    cliente_externo.close()

    assert registro.registers[0] > 0


def test_conectar_falla_con_reintentos_si_no_hay_servidor():
    cliente = ClienteModbusAcceso(
        "127.0.0.1", puerto=15099, unidad=1, intentos_conexion=2, tiempo_espera_s=0.1
    )
    assert cliente.conectar() is False
