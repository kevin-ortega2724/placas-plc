"""Localizacion de la placa dentro de la imagen (Fase 04).

Implementa dos metodos independientes para encontrar el rectangulo de la
placa y compararlos: por color (segmentacion del amarillo en HSV) y por
bordes (contornos sobre la salida de preproceso.py). Ambos devuelven un
recorte rectificado del mismo tamano, listo para el OCR de la Fase 05.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from placas.configuracion import Localizacion
from placas.preproceso import preprocesar
from placas.configuracion import Preproceso


@dataclass
class Deteccion:
    """Resultado de intentar localizar la placa en una imagen."""

    encontrada: bool
    metodo: str
    caja: np.ndarray | None  # 4 puntos (x, y), orden tl, tr, br, bl
    recorte: np.ndarray | None
    puntaje: float


def _ordenar_puntos(puntos: np.ndarray) -> np.ndarray:
    """Ordena 4 puntos como (arriba-izq, arriba-der, abajo-der, abajo-izq)."""
    puntos = puntos[np.argsort(puntos[:, 1])]
    superior = puntos[:2][np.argsort(puntos[:2, 0])]
    inferior = puntos[2:][np.argsort(puntos[2:, 0])]
    return np.array([superior[0], superior[1], inferior[1], inferior[0]], dtype=np.float32)


def _evaluar_contorno(contorno: np.ndarray, parametros: Localizacion) -> tuple[np.ndarray, float, float] | None:
    """Evalua si un contorno es un buen candidato a placa.

    Devuelve (caja_ordenada, area, puntaje) o None si no cumple los
    filtros minimos de area, relacion de aspecto o rectangularidad.
    """
    area = cv2.contourArea(contorno)
    if area < parametros.area_minima:
        return None

    rect = cv2.minAreaRect(contorno)
    (ancho, alto) = rect[1]
    if ancho == 0 or alto == 0:
        return None

    lado_mayor, lado_menor = max(ancho, alto), min(ancho, alto)
    aspecto = lado_mayor / lado_menor
    error_aspecto = abs(aspecto - parametros.relacion_aspecto_esperada)
    if error_aspecto > parametros.tolerancia_aspecto:
        return None

    area_caja = ancho * alto
    rectangularidad = area / area_caja if area_caja > 0 else 0.0
    if rectangularidad < parametros.rectangularidad_minima:
        return None

    puntaje_aspecto = 1.0 - min(error_aspecto / parametros.tolerancia_aspecto, 1.0)
    puntaje = 0.5 * puntaje_aspecto + 0.5 * min(rectangularidad, 1.0)

    caja = _ordenar_puntos(cv2.boxPoints(rect))
    return caja, area, puntaje


def _rectificar(imagen: np.ndarray, caja: np.ndarray, parametros: Localizacion) -> np.ndarray:
    """Corrige perspectiva y recorta la placa a un tamano fijo."""
    ancho, alto = parametros.ancho_rectificado, parametros.alto_rectificado
    destino = np.array(
        [[0, 0], [ancho - 1, 0], [ancho - 1, alto - 1], [0, alto - 1]], dtype=np.float32
    )
    matriz = cv2.getPerspectiveTransform(caja, destino)
    return cv2.warpPerspective(imagen, matriz, (ancho, alto))


def _mejor_deteccion(
    contornos: list[np.ndarray], imagen: np.ndarray, parametros: Localizacion, metodo: str
) -> Deteccion:
    candidatos = []
    for contorno in contornos:
        evaluado = _evaluar_contorno(contorno, parametros)
        if evaluado is not None:
            candidatos.append(evaluado)

    if not candidatos:
        return Deteccion(encontrada=False, metodo=metodo, caja=None, recorte=None, puntaje=0.0)

    caja, _area, puntaje = max(candidatos, key=lambda c: c[2])
    recorte = _rectificar(imagen, caja, parametros)
    return Deteccion(encontrada=True, metodo=metodo, caja=caja, recorte=recorte, puntaje=puntaje)


def localizar_por_color(imagen: np.ndarray, parametros: Localizacion) -> Deteccion:
    """Busca la placa segmentando el amarillo caracteristico en HSV.

    Convierte a HSV (mas robusto que BGR ante cambios de brillo), aisla
    los pixeles dentro del rango de amarillo configurado, limpia la
    mascara con morfologia y evalua los contornos resultantes.
    """
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, np.array(parametros.hsv_amarillo_bajo), np.array(parametros.hsv_amarillo_alto))

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return _mejor_deteccion(contornos, imagen, parametros, "color")


def localizar_por_bordes(
    imagen: np.ndarray,
    parametros: Localizacion,
    parametros_preproceso: Preproceso | None = None,
    bordes_precalculados: np.ndarray | None = None,
) -> Deteccion:
    """Busca la placa a partir de contornos sobre los bordes de preproceso.py.

    Usa el resultado ya cerrado (cierre morfologico) de la Fase 03, que
    conecta el contorno de la placa en una sola figura cuadrilatera. Si
    ya se calcularon los bordes en otra etapa (por ejemplo, pipeline.py),
    se pueden pasar en bordes_precalculados para no repetir el trabajo.
    """
    if bordes_precalculados is not None:
        bordes = bordes_precalculados
    else:
        parametros_preproceso = parametros_preproceso or _preproceso_por_defecto()
        bordes = preprocesar(imagen, parametros_preproceso).cerrado

    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return _mejor_deteccion(contornos, imagen, parametros, "bordes")


def _preproceso_por_defecto() -> Preproceso:
    return Preproceso(
        clahe_clip_limit=2.0,
        clahe_tamano_grilla=8,
        bilateral_diametro=9,
        bilateral_sigma_color=75.0,
        bilateral_sigma_espacio=75.0,
        canny_umbral_bajo=50,
        canny_umbral_alto=150,
        kernel_morfologico=5,
    )


def dibujar_candidatos(imagen: np.ndarray, deteccion: Deteccion) -> np.ndarray:
    """Dibuja la caja elegida sobre una copia de la imagen (depuracion)."""
    salida = imagen.copy()
    if deteccion.caja is not None:
        puntos = deteccion.caja.astype(int)
        cv2.polylines(salida, [puntos], isClosed=True, color=(0, 255, 0), thickness=3)
    return salida


if __name__ == "__main__":
    import argparse

    from placas.adquisicion import FuenteImagenes
    from placas.configuracion import cargar_reglas

    parser = argparse.ArgumentParser(
        description="Recorre una carpeta de imagenes y reporta el porcentaje de placas localizadas."
    )
    parser.add_argument("--fuente", type=str, default="data/sinteticas")
    parser.add_argument("--reglas", type=str, default="config/reglas.yaml")
    argumentos = parser.parse_args()

    reglas = cargar_reglas(argumentos.reglas)
    total = 0
    encontrados = {"color": 0, "bordes": 0}

    with FuenteImagenes(argumentos.fuente) as fuente:
        for fotograma in fuente:
            total += 1
            for metodo, funcion in (("color", localizar_por_color), ("bordes", localizar_por_bordes)):
                deteccion = funcion(fotograma.imagen, reglas.localizacion)
                if deteccion.encontrada:
                    encontrados[metodo] += 1

    print(f"Imagenes evaluadas: {total}")
    for metodo, cantidad in encontrados.items():
        porcentaje = 100 * cantidad / total if total else 0.0
        print(f"  Por {metodo}: {cantidad}/{total} ({porcentaje:.1f} %)")
