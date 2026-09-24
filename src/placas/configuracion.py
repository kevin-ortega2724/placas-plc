"""Carga y validacion de la configuracion del sistema (Fase 00).

Lee config/reglas.yaml, config/autorizados.csv y config/reportados.csv, y
valida que los valores sean consistentes con lo que espera el resto del
sistema: dias de la semana, digitos de placa, horas y confianza del OCR.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

DIAS_VALIDOS = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")
_PATRON_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ErrorConfiguracion(ValueError):
    """Un archivo de configuracion tiene un valor invalido."""


@dataclass
class Horario:
    inicio: str
    fin: str


@dataclass
class PicoYPlaca:
    activo: bool
    horarios: list[Horario]
    restricciones: dict[str, list[int]]
    aplicar_en_festivos: bool
    pais_festivos: str


@dataclass
class Ocr:
    confianza_minima: float
    idiomas: list[str]
    caracteres_permitidos: str


@dataclass
class FormatoPlaca:
    carro: str
    moto: str


@dataclass
class Correcciones:
    a_letra: dict[str, str]
    a_numero: dict[str, str]


@dataclass
class Plc:
    host: str
    puerto: int
    unidad: int
    periodo_watchdog_s: float


@dataclass
class Preproceso:
    clahe_clip_limit: float
    clahe_tamano_grilla: int
    bilateral_diametro: int
    bilateral_sigma_color: float
    bilateral_sigma_espacio: float
    canny_umbral_bajo: int
    canny_umbral_alto: int
    kernel_morfologico: int


@dataclass
class Reglas:
    pico_y_placa: PicoYPlaca
    ocr: Ocr
    formato_placa: FormatoPlaca
    correcciones: Correcciones
    plc: Plc
    preproceso: Preproceso


def cargar_reglas(ruta: str | Path) -> Reglas:
    """Lee y valida config/reglas.yaml y devuelve un objeto Reglas.

    Lanza ErrorConfiguracion con un mensaje en espanol si algun valor no
    es valido (dia de la semana, digito, hora o confianza del OCR).
    """
    contenido = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))

    return Reglas(
        pico_y_placa=_construir_pico_y_placa(contenido["pico_y_placa"]),
        ocr=_construir_ocr(contenido["ocr"]),
        formato_placa=FormatoPlaca(**contenido["formato_placa"]),
        correcciones=Correcciones(**contenido["correcciones"]),
        plc=Plc(**contenido["plc"]),
        preproceso=_construir_preproceso(contenido["preproceso"]),
    )


def _construir_pico_y_placa(datos: dict) -> PicoYPlaca:
    horarios = [_validar_horario(h) for h in datos["horarios"]]

    restricciones: dict[str, list[int]] = {}
    for dia, digitos in datos["restricciones"].items():
        if dia not in DIAS_VALIDOS:
            raise ErrorConfiguracion(
                f"Dia invalido en restricciones de pico y placa: '{dia}'. "
                f"Debe ser uno de: {', '.join(DIAS_VALIDOS)}."
            )
        for digito in digitos:
            if not (0 <= digito <= 9):
                raise ErrorConfiguracion(
                    f"El dia '{dia}' tiene un digito fuera de rango: {digito}. "
                    "Debe estar entre 0 y 9."
                )
        restricciones[dia] = list(digitos)

    return PicoYPlaca(
        activo=bool(datos["activo"]),
        horarios=horarios,
        restricciones=restricciones,
        aplicar_en_festivos=bool(datos["aplicar_en_festivos"]),
        pais_festivos=datos["pais_festivos"],
    )


def _validar_horario(datos: dict) -> Horario:
    for clave in ("inicio", "fin"):
        valor = datos[clave]
        if not _PATRON_HORA.match(valor):
            raise ErrorConfiguracion(
                f"Formato de hora invalido: '{valor}'. Debe usar HH:MM en 24 horas."
            )
    return Horario(inicio=datos["inicio"], fin=datos["fin"])


def _construir_ocr(datos: dict) -> Ocr:
    confianza = float(datos["confianza_minima"])
    if not (0.0 <= confianza <= 1.0):
        raise ErrorConfiguracion(
            f"confianza_minima invalida: {confianza}. Debe estar entre 0 y 1."
        )
    return Ocr(
        confianza_minima=confianza,
        idiomas=list(datos["idiomas"]),
        caracteres_permitidos=datos["caracteres_permitidos"],
    )


def _construir_preproceso(datos: dict) -> Preproceso:
    bajo = int(datos["canny_umbral_bajo"])
    alto = int(datos["canny_umbral_alto"])
    if not (0 <= bajo < alto <= 255):
        raise ErrorConfiguracion(
            f"Umbrales de Canny invalidos: bajo={bajo}, alto={alto}. "
            "Deben cumplir 0 <= bajo < alto <= 255."
        )
    if datos["clahe_clip_limit"] <= 0:
        raise ErrorConfiguracion(
            f"clahe_clip_limit invalido: {datos['clahe_clip_limit']}. Debe ser mayor que 0."
        )
    if datos["kernel_morfologico"] < 1:
        raise ErrorConfiguracion(
            f"kernel_morfologico invalido: {datos['kernel_morfologico']}. Debe ser mayor o igual a 1."
        )
    return Preproceso(
        clahe_clip_limit=float(datos["clahe_clip_limit"]),
        clahe_tamano_grilla=int(datos["clahe_tamano_grilla"]),
        bilateral_diametro=int(datos["bilateral_diametro"]),
        bilateral_sigma_color=float(datos["bilateral_sigma_color"]),
        bilateral_sigma_espacio=float(datos["bilateral_sigma_espacio"]),
        canny_umbral_bajo=bajo,
        canny_umbral_alto=alto,
        kernel_morfologico=int(datos["kernel_morfologico"]),
    )


def cargar_autorizados(ruta: str | Path) -> dict[str, dict]:
    """Lee config/autorizados.csv y devuelve un diccionario indexado por placa."""
    return _cargar_csv_por_placa(ruta)


def cargar_reportados(ruta: str | Path) -> dict[str, dict]:
    """Lee config/reportados.csv y devuelve un diccionario indexado por placa."""
    return _cargar_csv_por_placa(ruta)


def _cargar_csv_por_placa(ruta: str | Path) -> dict[str, dict]:
    resultado: dict[str, dict] = {}
    with Path(ruta).open(newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            fila = dict(fila)
            placa = fila.pop("placa")
            for clave, valor in fila.items():
                if valor in ("true", "false"):
                    fila[clave] = valor == "true"
            resultado[placa] = fila
    return resultado


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[2]
    reglas = cargar_reglas(raiz / "config" / "reglas.yaml")

    print("Reglas de pico y placa")
    print(f"  Activo: {reglas.pico_y_placa.activo}")
    for horario in reglas.pico_y_placa.horarios:
        print(f"  Horario restringido: {horario.inicio} - {horario.fin}")
    for dia in DIAS_VALIDOS:
        digitos = reglas.pico_y_placa.restricciones.get(dia, [])
        texto = ", ".join(str(d) for d in digitos) if digitos else "sin restriccion"
        print(f"  {dia.capitalize()}: {texto}")
    print(
        f"  Aplica en festivos: {reglas.pico_y_placa.aplicar_en_festivos} "
        f"({reglas.pico_y_placa.pais_festivos})"
    )

    print("\nOCR")
    print(f"  Confianza minima: {reglas.ocr.confianza_minima}")
    print(f"  Caracteres permitidos: {reglas.ocr.caracteres_permitidos}")

    print("\nFormato de placa")
    print(f"  Carro: {reglas.formato_placa.carro}")
    print(f"  Moto: {reglas.formato_placa.moto}")

    print("\nPLC")
    print(f"  Host: {reglas.plc.host}:{reglas.plc.puerto} (unidad {reglas.plc.unidad})")
