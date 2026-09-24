"""Pruebas de las reglas de acceso (Fase 07): pico y placa, prioridades."""
from datetime import datetime
from pathlib import Path

import pytest

from placas.configuracion import cargar_autorizados, cargar_reglas, cargar_reportados
from placas.ocr import Lectura
from placas.reglas import CodigoDecision, decidir

RAIZ = Path(__file__).resolve().parent.parent
REGLAS = cargar_reglas(RAIZ / "config" / "reglas.yaml")
AUTORIZADOS = cargar_autorizados(RAIZ / "config" / "autorizados.csv")
REPORTADOS = cargar_reportados(RAIZ / "config" / "reportados.csv")

# UTP123: docente, sin excepcion, ultimo digito 3 (miercoles restringe 5,6 -> no aplica)
# AMB911: ambulancia, CON excepcion_pico_placa, ultimo digito 1
# ELE100: electrico, CON excepcion, ultimo digito 0
# XYZ999: reportada

LUNES_NO_FESTIVO_7AM = datetime(2024, 1, 15, 7, 0)  # lunes, restringe digitos 1 y 2
LUNES_FESTIVO_7AM = datetime(2024, 1, 1, 7, 0)  # lunes festivo (Ano Nuevo)
SABADO_7AM = datetime(2024, 1, 20, 7, 0)


def _lectura(placa: str, confianza: float = 0.95, formato_valido: bool = True) -> Lectura:
    return Lectura(
        texto_crudo=placa,
        placa_normalizada=placa,
        confianza=confianza,
        formato_valido=formato_valido,
        tipo="carro" if formato_valido else None,
    )


def test_sin_vehiculo_cuando_no_hay_lectura():
    decision = decidir(None, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.SIN_VEHICULO


def test_lectura_dudosa_por_confianza_baja():
    lectura = _lectura("UTP123", confianza=0.5)
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.LECTURA_DUDOSA


def test_lectura_dudosa_por_formato_invalido():
    lectura = _lectura("AB1234X", confianza=0.99, formato_valido=False)
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.LECTURA_DUDOSA


def test_reportado_tiene_prioridad_sobre_no_autorizado():
    lectura = _lectura("XYZ999")
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.REPORTADO


def test_no_autorizado_si_la_placa_no_esta_en_la_lista():
    lectura = _lectura("QQQ000")
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.NO_AUTORIZADO


def test_pico_y_placa_aplica_a_autorizado_sin_excepcion_en_horario_restringido():
    # ABC120 (estudiante, sin excepcion, ultimo digito 0): lunes restringe 1 y 2, no 0.
    # Usamos una placa autorizada cuyo ultimo digito SI este restringido el lunes.
    lectura = _lectura("ABC231")  # estudiante, ultimo digito 1 -> restringido el lunes
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.PICO_Y_PLACA


def test_pico_y_placa_no_aplica_con_excepcion():
    # AMB911: ambulancia con excepcion_pico_placa=true, ultimo digito 1 (restringido el lunes)
    lectura = _lectura("AMB911")
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.PERMITIDO


def test_pico_y_placa_no_aplica_en_festivo():
    # ABC231, digito 1, restringido el lunes, pero 2024-01-01 es festivo
    # y aplicar_en_festivos es false -> no deberia aplicar.
    lectura = _lectura("ABC231")
    decision = decidir(lectura, LUNES_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.PERMITIDO


def test_pico_y_placa_no_aplica_en_sabado():
    lectura = _lectura("ABC231")
    decision = decidir(lectura, SABADO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.PERMITIDO


def test_permitido_fuera_de_pico_y_placa():
    lectura = _lectura("UTP123")  # ultimo digito 3, lunes restringe 1 y 2
    decision = decidir(lectura, LUNES_NO_FESTIVO_7AM, REGLAS, AUTORIZADOS, REPORTADOS)
    assert decision.codigo == CodigoDecision.PERMITIDO


@pytest.mark.parametrize(
    "hora, se_espera_restriccion",
    [
        ((5, 59), False),  # justo antes del horario
        ((6, 0), True),  # inicio del horario, inclusivo
        ((8, 59), True),  # justo antes del fin
        ((9, 0), False),  # fin del horario, exclusivo
    ],
)
def test_bordes_de_horario_de_pico_y_placa(hora, se_espera_restriccion):
    fecha_hora = datetime(2024, 1, 15, hora[0], hora[1])  # lunes no festivo
    lectura = _lectura("ABC231")  # ultimo digito 1, restringido el lunes
    decision = decidir(lectura, fecha_hora, REGLAS, AUTORIZADOS, REPORTADOS)

    if se_espera_restriccion:
        assert decision.codigo == CodigoDecision.PICO_Y_PLACA
    else:
        assert decision.codigo == CodigoDecision.PERMITIDO


# Tabla de casos para usar en clase (Fase 07):
#
# | Placa   | Fecha/hora            | Codigo esperado | Motivo                          |
# |---------|------------------------|------------------|----------------------------------|
# | (ninguna)| -                     | SIN_VEHICULO     | no se detecto placa              |
# | UTP123  | lunes 07:00, conf 0.5  | LECTURA_DUDOSA   | confianza bajo el minimo         |
# | XYZ999  | lunes 07:00            | REPORTADO        | placa reportada                  |
# | QQQ000  | lunes 07:00            | NO_AUTORIZADO    | no esta en autorizados.csv       |
# | ABC231  | lunes 07:00            | PICO_Y_PLACA     | digito 1 restringido el lunes    |
# | AMB911  | lunes 07:00            | PERMITIDO        | tiene excepcion (ambulancia)     |
# | ABC231  | festivo 07:00          | PERMITIDO        | festivo sin restriccion          |
# | ABC231  | sabado 07:00           | PERMITIDO        | sabado sin restriccion           |
# | ABC231  | lunes 05:59            | PERMITIDO        | antes del horario restringido    |
# | ABC231  | lunes 06:00            | PICO_Y_PLACA     | inicio del horario (inclusivo)   |
# | ABC231  | lunes 08:59            | PICO_Y_PLACA     | justo antes del fin del horario  |
# | ABC231  | lunes 09:00            | PERMITIDO        | fin del horario (exclusivo)      |
