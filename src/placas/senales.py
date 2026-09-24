"""Traduccion de la decision a senales digitales y analogicas (Fase 08).

Convierte una Decision (Fase 07) en la tabla de coils y holding registers
del ENUNCIADO, lista para enviar por Modbus TCP (Fase 10) o para el PLC
simulado de este mismo archivo.
"""
from __future__ import annotations

from dataclasses import dataclass

from placas.ocr import Lectura
from placas.reglas import CodigoDecision, Decision


@dataclass
class Senales:
    """Espejo de la tabla de coils y holding registers del ENUNCIADO."""

    vehiculo_presente: bool  # Coil 0
    acceso_permitido: bool  # Coil 1
    acceso_denegado: bool  # Coil 2
    lectura_dudosa: bool  # Coil 3
    nueva_lectura: bool  # Coil 4 (pulso)
    codigo_decision: int  # Holding 0 (0-5)
    confianza: int  # Holding 1 (0-1000)
    ultimo_digito: int  # Holding 2 (0-9)
    watchdog: int = 0  # Holding 3 (lo incrementa el sistema de vision cada segundo)


_CODIGOS_ACCESO_DENEGADO = (
    CodigoDecision.REPORTADO,
    CodigoDecision.NO_AUTORIZADO,
    CodigoDecision.PICO_Y_PLACA,
)


def a_senales(decision: Decision, lectura: Lectura | None) -> Senales:
    """Traduce una Decision (y la Lectura que la origino) a Senales."""
    confianza = lectura.confianza if lectura is not None else 0.0
    return Senales(
        vehiculo_presente=lectura is not None,
        acceso_permitido=decision.codigo == CodigoDecision.PERMITIDO,
        acceso_denegado=decision.codigo in _CODIGOS_ACCESO_DENEGADO,
        lectura_dudosa=decision.codigo == CodigoDecision.LECTURA_DUDOSA,
        nueva_lectura=True,
        codigo_decision=int(decision.codigo),
        confianza=round(confianza * 1000),
        ultimo_digito=decision.ultimo_digito if decision.ultimo_digito is not None else 0,
    )


def a_modbus(senales: Senales) -> tuple[list[bool], list[int]]:
    """Devuelve (coils, registros) en el orden de direcciones del ENUNCIADO."""
    coils = [
        senales.vehiculo_presente,
        senales.acceso_permitido,
        senales.acceso_denegado,
        senales.lectura_dudosa,
        senales.nueva_lectura,
    ]
    registros = [
        senales.codigo_decision,
        senales.confianza,
        senales.ultimo_digito,
        senales.watchdog,
    ]
    return coils, registros
