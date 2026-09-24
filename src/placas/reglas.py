"""Reglas de acceso: pico y placa, autorizados y reportados (Fase 07).

Aplica las reglas del ENUNCIADO en orden de prioridad y se detiene en la
primera que corresponda. La fecha y hora siempre entran como parametro
(nunca datetime.now() dentro de esta logica) para poder probar cualquier
dia y hora sin esperar a que ocurra de verdad.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import time as _time
from enum import IntEnum

from placas.configuracion import DIAS_VALIDOS, Horario, PicoYPlaca, Reglas
from placas.ocr import Lectura


class CodigoDecision(IntEnum):
    """Codigos de decision de la tabla del ENUNCIADO, en orden de prioridad."""

    SIN_VEHICULO = 0
    LECTURA_DUDOSA = 1
    REPORTADO = 2
    NO_AUTORIZADO = 3
    PICO_Y_PLACA = 4
    PERMITIDO = 5


@dataclass
class Decision:
    """Resultado de aplicar las reglas de acceso a una lectura."""

    codigo: CodigoDecision
    nombre: str
    motivo: str
    ultimo_digito: int | None


def decidir(
    lectura: Lectura | None,
    fecha_hora: datetime,
    reglas: Reglas,
    autorizados: dict[str, dict],
    reportados: dict[str, dict],
) -> Decision:
    """Aplica las seis reglas del ENUNCIADO, en orden, y devuelve la
    primera que corresponda.
    """
    if lectura is None:
        return Decision(
            CodigoDecision.SIN_VEHICULO,
            "SIN_VEHICULO",
            "No se detecto vehiculo ni placa en la imagen.",
            None,
        )

    if lectura.confianza < reglas.ocr.confianza_minima or not lectura.formato_valido:
        return Decision(
            CodigoDecision.LECTURA_DUDOSA,
            "LECTURA_DUDOSA",
            f"Confianza {lectura.confianza:.2f} o formato invalido para '{lectura.placa_normalizada}'.",
            None,
        )

    placa = lectura.placa_normalizada
    ultimo_digito = int(placa[-1])

    if placa in reportados:
        motivo = reportados[placa].get("motivo", "Placa reportada.")
        return Decision(CodigoDecision.REPORTADO, "REPORTADO", motivo, ultimo_digito)

    if placa not in autorizados:
        return Decision(
            CodigoDecision.NO_AUTORIZADO,
            "NO_AUTORIZADO",
            f"La placa '{placa}' no esta en la lista de autorizados.",
            ultimo_digito,
        )

    tiene_excepcion = bool(autorizados[placa].get("excepcion_pico_placa", False))
    if not tiene_excepcion and _aplica_pico_y_placa(ultimo_digito, fecha_hora, reglas.pico_y_placa):
        return Decision(
            CodigoDecision.PICO_Y_PLACA,
            "PICO_Y_PLACA",
            f"Digito {ultimo_digito} restringido hoy en el horario actual.",
            ultimo_digito,
        )

    return Decision(CodigoDecision.PERMITIDO, "PERMITIDO", "Acceso permitido.", ultimo_digito)


def _aplica_pico_y_placa(ultimo_digito: int, fecha_hora: datetime, config: PicoYPlaca) -> bool:
    if not config.activo:
        return False

    if _es_festivo(fecha_hora, config.pais_festivos) and not config.aplicar_en_festivos:
        return False

    dia = DIAS_VALIDOS[fecha_hora.weekday()]
    if ultimo_digito not in config.restricciones.get(dia, []):
        return False

    hora = fecha_hora.time()
    return any(_hora_en_rango(hora, horario) for horario in config.horarios)


def _hora_en_rango(hora: _time, horario: Horario) -> bool:
    inicio = _parsear_hora(horario.inicio)
    fin = _parsear_hora(horario.fin)
    return inicio <= hora < fin


def _parsear_hora(texto: str) -> _time:
    horas, minutos = texto.split(":")
    return _time(int(horas), int(minutos))


def _es_festivo(fecha_hora: datetime, pais: str) -> bool:
    import holidays

    festivos = holidays.country_holidays(pais)
    return fecha_hora.date() in festivos
