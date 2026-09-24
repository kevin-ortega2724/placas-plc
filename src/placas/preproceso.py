"""Preprocesamiento de imagenes antes de buscar la placa (Fase 03).

Cada funcion hace un solo paso, documentado, para que se pueda observar
el efecto individual de cada filtro sobre la imagen antes de encadenarlos.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from placas.configuracion import Preproceso


@dataclass
class ResultadoPreproceso:
    """Resultado de cada paso del preprocesamiento, en orden."""

    gris: np.ndarray
    ecualizado: np.ndarray
    filtrado: np.ndarray
    bordes: np.ndarray
    cerrado: np.ndarray


def a_grises(imagen: np.ndarray) -> np.ndarray:
    """Convierte una imagen BGR a escala de grises.

    Reduce la imagen de 3 canales a 1: se pierde el color pero se
    simplifica el resto del procesamiento, que solo necesita el
    contraste entre la placa y el fondo, no su color exacto.
    """
    return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)


def ecualizar_clahe(gris: np.ndarray, clip_limit: float, tamano_grilla: int) -> np.ndarray:
    """Ecualiza el contraste de forma adaptativa (CLAHE).

    A diferencia de una ecualizacion global, CLAHE trabaja por regiones
    (una grilla de tamano_grilla x tamano_grilla), lo que mejora el
    contraste en zonas con sombra o brillo desigual sin saturar el resto
    de la imagen.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tamano_grilla, tamano_grilla))
    return clahe.apply(gris)


def filtrar_bilateral(
    gris: np.ndarray, diametro: int, sigma_color: float, sigma_espacio: float
) -> np.ndarray:
    """Suaviza el ruido conservando los bordes (filtro bilateral).

    A diferencia de un desenfoque comun, el filtro bilateral promedia
    solo pixeles vecinos con intensidad parecida, por lo que reduce el
    ruido de fondo sin borrar el contorno de la placa.
    """
    return cv2.bilateralFilter(gris, diametro, sigma_color, sigma_espacio)


def detectar_bordes_canny(imagen: np.ndarray, umbral_bajo: int, umbral_alto: int) -> np.ndarray:
    """Detecta bordes con el algoritmo de Canny.

    Devuelve una imagen binaria (solo 0 o 255): 255 donde hay un cambio
    de intensidad fuerte (un borde), 0 en el resto. El borde de la placa
    (rectangulo amarillo sobre fondo gris) suele producir un contorno
    limpio y cerrado.
    """
    return cv2.Canny(imagen, umbral_bajo, umbral_alto)


def cerrar_morfologico(bordes: np.ndarray, kernel_size: int) -> np.ndarray:
    """Cierra huecos pequenos en los bordes (operacion morfologica de cierre).

    El cierre (dilatar y despues erosionar) une segmentos de borde que
    quedaron separados por un par de pixeles, para que el contorno de la
    placa quede completo y se pueda usar en la fase de localizacion.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, kernel)


def crear_mosaico(pasos: dict[str, np.ndarray]) -> np.ndarray:
    """Combina los pasos del preprocesamiento en una sola imagen con
    etiquetas, para comparar el efecto de cada filtro de un vistazo."""
    celdas = []
    for etiqueta, paso in pasos.items():
        color = cv2.cvtColor(paso, cv2.COLOR_GRAY2BGR) if paso.ndim == 2 else paso.copy()
        cv2.putText(
            color, etiqueta, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        celdas.append(color)

    alto = max(c.shape[0] for c in celdas)
    ancho = max(c.shape[1] for c in celdas)
    celdas_uniformes = [cv2.resize(c, (ancho, alto)) for c in celdas]

    columnas = 3
    filas = -(-len(celdas_uniformes) // columnas)
    relleno = [np.zeros((alto, ancho, 3), dtype=np.uint8)] * (filas * columnas - len(celdas_uniformes))
    celdas_uniformes += relleno

    filas_imagenes = [
        np.hstack(celdas_uniformes[i * columnas : (i + 1) * columnas]) for i in range(filas)
    ]
    return np.vstack(filas_imagenes)


def preprocesar(
    imagen: np.ndarray,
    parametros: Preproceso,
    depurar: bool = False,
    carpeta_salidas: str | Path = "salidas",
) -> ResultadoPreproceso:
    """Encadena escala de grises, CLAHE, filtro bilateral, Canny y cierre
    morfologico. Si depurar=True, guarda cada paso y un mosaico en
    carpeta_salidas, para que se pueda ver el efecto de cada filtro.
    """
    gris = a_grises(imagen)
    ecualizado = ecualizar_clahe(gris, parametros.clahe_clip_limit, parametros.clahe_tamano_grilla)
    filtrado = filtrar_bilateral(
        ecualizado,
        parametros.bilateral_diametro,
        parametros.bilateral_sigma_color,
        parametros.bilateral_sigma_espacio,
    )
    bordes = detectar_bordes_canny(filtrado, parametros.canny_umbral_bajo, parametros.canny_umbral_alto)
    cerrado = cerrar_morfologico(bordes, parametros.kernel_morfologico)

    resultado = ResultadoPreproceso(
        gris=gris, ecualizado=ecualizado, filtrado=filtrado, bordes=bordes, cerrado=cerrado
    )

    if depurar:
        _guardar_pasos(resultado, carpeta_salidas)

    return resultado


def _guardar_pasos(resultado: ResultadoPreproceso, carpeta_salidas: str | Path) -> None:
    carpeta = Path(carpeta_salidas)
    carpeta.mkdir(parents=True, exist_ok=True)

    pasos = {
        "01_grises.png": resultado.gris,
        "02_clahe.png": resultado.ecualizado,
        "03_bilateral.png": resultado.filtrado,
        "04_canny.png": resultado.bordes,
        "05_cierre_morfologico.png": resultado.cerrado,
    }
    for nombre, paso in pasos.items():
        cv2.imwrite(str(carpeta / nombre), paso)

    mosaico = crear_mosaico({nombre.replace(".png", ""): paso for nombre, paso in pasos.items()})
    cv2.imwrite(str(carpeta / "00_mosaico.png"), mosaico)


if __name__ == "__main__":
    import argparse

    from placas.configuracion import cargar_reglas

    parser = argparse.ArgumentParser(description="Preprocesa una imagen y guarda el mosaico de pasos.")
    parser.add_argument("--imagen", type=str, required=True, help="Ruta de la imagen a procesar.")
    parser.add_argument("--reglas", type=str, default="config/reglas.yaml")
    parser.add_argument("--salida", type=str, default="salidas")
    argumentos = parser.parse_args()

    reglas = cargar_reglas(argumentos.reglas)
    imagen_leida = cv2.imread(argumentos.imagen)
    if imagen_leida is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {argumentos.imagen}")

    preprocesar(imagen_leida, reglas.preproceso, depurar=True, carpeta_salidas=argumentos.salida)
    print(f"Pasos guardados en {argumentos.salida}/ (ver 00_mosaico.png)")
