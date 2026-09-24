"""Pipeline completo: preprocesamiento, localizacion y OCR (Fase 05).

Encadena las fases anteriores y mide el tiempo de cada etapa, para poder
identificar despues (Fase 06) donde se concentra el costo de procesar
una imagen.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from placas.configuracion import Reglas
from placas.localizacion import Deteccion, localizar_por_bordes, localizar_por_color
from placas.ocr import Lectura, leer_placa
from placas.preproceso import preprocesar


@dataclass
class ResultadoPipeline:
    """Resultado de correr el pipeline completo sobre una imagen."""

    deteccion: Deteccion
    lectura: Lectura | None
    tiempos_s: dict[str, float] = field(default_factory=dict)


def procesar_imagen(imagen: np.ndarray, reglas: Reglas) -> ResultadoPipeline:
    """Corre preproceso, localizacion (color, con bordes como respaldo) y
    OCR sobre una imagen, midiendo el tiempo de cada etapa en segundos.
    """
    tiempos: dict[str, float] = {}

    inicio = time.perf_counter()
    resultado_preproceso = preprocesar(imagen, reglas.preproceso)
    tiempos["preproceso"] = time.perf_counter() - inicio

    inicio = time.perf_counter()
    deteccion = localizar_por_color(imagen, reglas.localizacion)
    if not deteccion.encontrada:
        deteccion = localizar_por_bordes(
            imagen, reglas.localizacion, bordes_precalculados=resultado_preproceso.cerrado
        )
    tiempos["localizacion"] = time.perf_counter() - inicio

    lectura: Lectura | None = None
    if deteccion.encontrada:
        inicio = time.perf_counter()
        lectura = leer_placa(deteccion.recorte, reglas)
        tiempos["ocr"] = time.perf_counter() - inicio

    tiempos["total"] = sum(tiempos.values())
    return ResultadoPipeline(deteccion=deteccion, lectura=lectura, tiempos_s=tiempos)


if __name__ == "__main__":
    import argparse

    import cv2

    from placas.configuracion import cargar_reglas

    parser = argparse.ArgumentParser(description="Corre el pipeline completo sobre una imagen.")
    parser.add_argument("--imagen", type=str, required=True)
    parser.add_argument("--reglas", type=str, default="config/reglas.yaml")
    argumentos = parser.parse_args()

    reglas_cargadas = cargar_reglas(argumentos.reglas)
    imagen_leida = cv2.imread(argumentos.imagen)
    if imagen_leida is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {argumentos.imagen}")

    resultado = procesar_imagen(imagen_leida, reglas_cargadas)
    print(f"Detectada: {resultado.deteccion.encontrada} (metodo: {resultado.deteccion.metodo})")
    if resultado.lectura is not None:
        print(f"Placa leida: {resultado.lectura.placa_normalizada} (confianza: {resultado.lectura.confianza:.2f})")
    print("Tiempos (s):", {k: round(v, 4) for k, v in resultado.tiempos_s.items()})
