"""Pruebas de humo del HMI de solo lectura (Fase 12), via AppTest.

Usa un servidor Modbus real (hmi/servidor_prueba.py) con datos
precargados, simulando lo que un PLC real expondria en sus salidas.
"""
import threading
import time
from pathlib import Path

import pytest
from pymodbus.client import ModbusTcpClient
from pymodbus.server import ServerStop
from streamlit.testing.v1 import AppTest

from hmi.servidor_prueba import iniciar_servidor

RAIZ = Path(__file__).resolve().parent.parent
RUTA_APP = str(RAIZ / "hmi" / "monitor.py")
PUERTO_PRUEBA = 15021


@pytest.fixture(scope="module")
def servidor_con_datos():
    hilo = threading.Thread(
        target=iniciar_servidor, args=("127.0.0.1", PUERTO_PRUEBA), daemon=True
    )
    hilo.start()
    time.sleep(0.3)

    escritor = ModbusTcpClient("127.0.0.1", port=PUERTO_PRUEBA)
    escritor.connect()
    escritor.write_coils(8, [True, False, False, False], slave=1)  # talanquera abierta
    escritor.write_registers(0, [5, 950], slave=1)  # PERMITIDO, confianza 0.95
    escritor.write_registers(10, [3, 1], slave=1)  # 3 ingresos, 1 rechazo
    escritor.close()

    yield
    ServerStop()
    hilo.join(timeout=2)


def test_monitor_muestra_estado_sin_excepciones(servidor_con_datos, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=30)

    at.sidebar.number_input[0].set_value(PUERTO_PRUEBA)
    at.run(timeout=30)

    assert not at.exception


def test_monitor_registra_historico(servidor_con_datos, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=30)

    at.sidebar.number_input[0].set_value(PUERTO_PRUEBA)
    at.run(timeout=30)

    assert (tmp_path / "salidas" / "historico.csv").exists()


def test_monitor_sin_conexion_muestra_aviso_claro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=30)

    at.sidebar.number_input[0].set_value(15099)  # puerto sin servidor
    at.run(timeout=30)

    assert not at.exception
    assert len(at.error) > 0
