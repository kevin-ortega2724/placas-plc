"""Lectura y validacion de la placa por OCR (Fase 05).

EasyOCR se carga una sola vez, de forma perezosa: crear el lector toma
varios segundos (carga un modelo de red neuronal), asi que no tiene
sentido repetirlo en cada imagen.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from placas.configuracion import Correcciones, FormatoPlaca, Reglas

# Debe coincidir con la proporcion de la franja de ciudad en generador.py
# (ALTO_PLACA * 0.18). Se recorta antes del OCR para no leer el nombre de
# la ciudad como si fuera parte de la placa.
PROPORCION_FRANJA_INFERIOR = 0.18

_PATRON_NO_ALFANUMERICO = re.compile(r"[^A-Z0-9]")

_lector_ocr = None


@dataclass
class Lectura:
    """Resultado de leer una placa con OCR."""

    texto_crudo: str
    placa_normalizada: str
    confianza: float
    formato_valido: bool
    tipo: str | None


def _obtener_lector(idiomas: list[str]):
    global _lector_ocr
    if _lector_ocr is None:
        import easyocr

        _lector_ocr = easyocr.Reader(idiomas, gpu=False, verbose=False)
    return _lector_ocr


def normalizar_texto(texto: str, correcciones: Correcciones) -> str:
    """Normaliza el texto crudo del OCR a una posible placa.

    Pasa a mayusculas, quita espacios, guiones y cualquier caracter que
    no sea letra o numero, y aplica las correcciones de config segun la
    posicion: letras esperadas en 1-3, numeros esperados en 4-6 (formato
    de carro; las motos quedan como extension, ver el reto de esta fase).
    """
    limpio = _PATRON_NO_ALFANUMERICO.sub("", texto.upper())
    caracteres = list(limpio)

    for i in range(min(3, len(caracteres))):
        caracteres[i] = correcciones.a_letra.get(caracteres[i], caracteres[i])
    for i in range(3, min(6, len(caracteres))):
        caracteres[i] = correcciones.a_numero.get(caracteres[i], caracteres[i])

    return "".join(caracteres)


def _determinar_tipo(placa: str, formato: FormatoPlaca) -> str | None:
    if re.match(formato.carro, placa):
        return "carro"
    if re.match(formato.moto, placa):
        return "moto"
    return None


def leer_placa(recorte: np.ndarray, reglas: Reglas) -> Lectura:
    """Lee el texto de un recorte de placa ya localizado y rectificado.

    Ignora la franja inferior (nombre de ciudad) antes de pasar la
    imagen al OCR, para que ese texto no se mezcle con la placa.
    """
    alto = recorte.shape[0]
    limite = int(alto * (1 - PROPORCION_FRANJA_INFERIOR))
    recorte_util = recorte[:limite]

    lector = _obtener_lector(reglas.ocr.idiomas)
    resultados = lector.readtext(recorte_util, allowlist=reglas.ocr.caracteres_permitidos)

    if not resultados:
        return Lectura(
            texto_crudo="", placa_normalizada="", confianza=0.0, formato_valido=False, tipo=None
        )

    texto_crudo = " ".join(texto for _caja, texto, _confianza in resultados)
    confianza = float(np.mean([confianza for _caja, _texto, confianza in resultados]))
    placa_normalizada = normalizar_texto(texto_crudo, reglas.correcciones)
    tipo = _determinar_tipo(placa_normalizada, reglas.formato_placa)

    return Lectura(
        texto_crudo=texto_crudo,
        placa_normalizada=placa_normalizada,
        confianza=confianza,
        formato_valido=tipo is not None,
        tipo=tipo,
    )


if __name__ == "__main__":
    import argparse

    import cv2

    from placas.configuracion import cargar_reglas

    parser = argparse.ArgumentParser(description="Lee una placa ya recortada con OCR.")
    parser.add_argument("--recorte", type=str, required=True, help="Ruta a una imagen ya recortada.")
    parser.add_argument("--reglas", type=str, default="config/reglas.yaml")
    argumentos = parser.parse_args()

    reglas_cargadas = cargar_reglas(argumentos.reglas)
    imagen = cv2.imread(argumentos.recorte)
    if imagen is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {argumentos.recorte}")

    lectura = leer_placa(imagen, reglas_cargadas)
    print(lectura)
