"""Pruebas de traduccion de decision a senales (Fase 08)."""
from placas.ocr import Lectura
from placas.reglas import CodigoDecision, Decision
from placas.senales import a_modbus, a_senales


def _lectura(confianza=0.95):
    return Lectura("ABC123", "ABC123", confianza, True, "carro")


def test_a_senales_sin_vehiculo():
    decision = Decision(CodigoDecision.SIN_VEHICULO, "SIN_VEHICULO", "motivo", None)
    senales = a_senales(decision, None)

    assert senales.vehiculo_presente is False
    assert senales.acceso_permitido is False
    assert senales.acceso_denegado is False
    assert senales.lectura_dudosa is False
    assert senales.codigo_decision == 0
    assert senales.confianza == 0
    assert senales.ultimo_digito == 0


def test_a_senales_lectura_dudosa():
    decision = Decision(CodigoDecision.LECTURA_DUDOSA, "LECTURA_DUDOSA", "motivo", None)
    senales = a_senales(decision, _lectura(confianza=0.4))

    assert senales.vehiculo_presente is True
    assert senales.lectura_dudosa is True
    assert senales.acceso_permitido is False
    assert senales.acceso_denegado is False
    assert senales.codigo_decision == 1
    assert senales.confianza == 400


def test_a_senales_reportado_es_acceso_denegado():
    decision = Decision(CodigoDecision.REPORTADO, "REPORTADO", "motivo", 3)
    senales = a_senales(decision, _lectura())

    assert senales.acceso_denegado is True
    assert senales.acceso_permitido is False
    assert senales.codigo_decision == 2
    assert senales.ultimo_digito == 3


def test_a_senales_no_autorizado_es_acceso_denegado():
    decision = Decision(CodigoDecision.NO_AUTORIZADO, "NO_AUTORIZADO", "motivo", 3)
    senales = a_senales(decision, _lectura())

    assert senales.acceso_denegado is True
    assert senales.codigo_decision == 3


def test_a_senales_pico_y_placa_es_acceso_denegado():
    decision = Decision(CodigoDecision.PICO_Y_PLACA, "PICO_Y_PLACA", "motivo", 1)
    senales = a_senales(decision, _lectura())

    assert senales.acceso_denegado is True
    assert senales.codigo_decision == 4
    assert senales.ultimo_digito == 1


def test_a_senales_permitido():
    decision = Decision(CodigoDecision.PERMITIDO, "PERMITIDO", "motivo", 3)
    senales = a_senales(decision, _lectura(confianza=0.987))

    assert senales.acceso_permitido is True
    assert senales.acceso_denegado is False
    assert senales.lectura_dudosa is False
    assert senales.codigo_decision == 5
    assert senales.confianza == 987
    assert senales.nueva_lectura is True


def test_a_modbus_orden_de_coils_y_registros():
    decision = Decision(CodigoDecision.PERMITIDO, "PERMITIDO", "motivo", 3)
    senales = a_senales(decision, _lectura(confianza=0.95))
    senales.watchdog = 7

    coils, registros = a_modbus(senales)

    assert coils == [True, True, False, False, True]
    assert registros == [5, 950, 3, 7]
