"""Adquisicion de imagenes desde carpeta, camara o video (Fase 02).

Una imagen leida con OpenCV es una matriz numpy de forma (alto, ancho,
canales). Los tres canales de color vienen en orden BGR (azul, verde,
rojo) y no en RGB, por una decision historica de la libreria.
"""
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

EXTENSIONES_VALIDAS = (".png", ".jpg", ".jpeg", ".bmp")


@dataclass
class Fotograma:
    """Un fotograma leido por FuenteImagenes, con nombre y marca de tiempo."""

    nombre: str
    marca_tiempo: float
    imagen: np.ndarray


class FuenteImagenes:
    """Iterador de fotogramas con una misma interfaz para tres fuentes:
    una carpeta de imagenes, una camara web (indice entero) o un archivo
    de video.

    Uso tipico:
        with FuenteImagenes("data/sinteticas") as fuente:
            for fotograma in fuente:
                ...  # fotograma.imagen es una matriz (alto, ancho, 3) BGR
    """

    def __init__(self, fuente: str | int):
        self._captura: cv2.VideoCapture | None = None
        self._archivos: list[Path] | None = None
        self._tiempo_anterior: float | None = None
        self.fps: float = 0.0

        if isinstance(fuente, int) or (isinstance(fuente, str) and fuente.isdigit()):
            self._captura = cv2.VideoCapture(int(fuente))
            if not self._captura.isOpened():
                raise RuntimeError(f"No se pudo abrir la camara {fuente}.")
            return

        ruta = Path(fuente)
        if ruta.is_dir():
            self._archivos = sorted(
                p for p in ruta.iterdir() if p.suffix.lower() in EXTENSIONES_VALIDAS
            )
            if not self._archivos:
                raise FileNotFoundError(f"No hay imagenes en la carpeta: {ruta}")
        elif ruta.is_file():
            self._captura = cv2.VideoCapture(str(ruta))
            if not self._captura.isOpened():
                raise RuntimeError(f"No se pudo abrir el video: {ruta}")
        else:
            raise FileNotFoundError(f"Fuente de imagenes no encontrada: {fuente}")

    def __enter__(self) -> "FuenteImagenes":
        return self

    def __exit__(self, *_excepcion) -> None:
        self.liberar()

    def liberar(self) -> None:
        """Libera la camara o el archivo de video, si la fuente usa uno."""
        if self._captura is not None:
            self._captura.release()

    def __iter__(self) -> Iterator[Fotograma]:
        if self._archivos is not None:
            yield from self._iterar_carpeta()
        else:
            yield from self._iterar_captura()

    def _iterar_carpeta(self) -> Iterator[Fotograma]:
        for ruta in self._archivos:
            imagen = cv2.imread(str(ruta))
            if imagen is None:
                continue
            yield self._empacar(ruta.name, imagen)

    def _iterar_captura(self) -> Iterator[Fotograma]:
        assert self._captura is not None
        indice = 0
        while True:
            leido, imagen = self._captura.read()
            if not leido:
                break
            yield self._empacar(
                f"fotograma_{indice:06d}", imagen, self._captura.get(cv2.CAP_PROP_FPS)
            )
            indice += 1

    def _empacar(self, nombre: str, imagen: np.ndarray, fps_nativo: float = 0.0) -> Fotograma:
        ahora = time.time()
        if fps_nativo and fps_nativo > 0:
            self.fps = fps_nativo
        elif self._tiempo_anterior is not None:
            transcurrido = ahora - self._tiempo_anterior
            if transcurrido > 0:
                self.fps = 1.0 / transcurrido
        self._tiempo_anterior = ahora
        return Fotograma(nombre=nombre, marca_tiempo=ahora, imagen=imagen)


def _imprimir_info(fotograma: Fotograma, fps: float) -> None:
    alto, ancho, canales = fotograma.imagen.shape
    print(f"{fotograma.nombre}: {ancho}x{alto} px, {canales} canales, {fps:.1f} FPS")


def _recorrer_con_ventana(fuente_str: str) -> None:
    """Bucle interactivo con ventana de OpenCV (requiere entorno grafico).

    Teclas: espacio pausa o reanuda, "s" guarda el fotograma en salidas/,
    "q" cierra la ventana y termina.
    """
    Path("salidas").mkdir(exist_ok=True)
    pausado = False
    with FuenteImagenes(fuente_str) as fuente:
        for fotograma in fuente:
            _imprimir_info(fotograma, fuente.fps)
            cv2.imshow("Adquisicion", fotograma.imagen)
            while True:
                tecla = cv2.waitKey(0 if pausado else 30) & 0xFF
                if tecla == ord(" "):
                    pausado = not pausado
                    if not pausado:
                        break
                elif tecla == ord("s"):
                    ruta_guardado = Path("salidas") / f"guardado_{fotograma.nombre}"
                    cv2.imwrite(str(ruta_guardado), fotograma.imagen)
                    print(f"Guardado: {ruta_guardado}")
                elif tecla == ord("q"):
                    cv2.destroyAllWindows()
                    return
                else:
                    break
    cv2.destroyAllWindows()


def _recorrer_sin_ventana(fuente_str: str) -> None:
    """Recorre la fuente e imprime tamano, canales y FPS sin abrir ventana.

    Se usa cuando no hay entorno grafico disponible (servidor, pruebas).
    """
    with FuenteImagenes(fuente_str) as fuente:
        for fotograma in fuente:
            _imprimir_info(fotograma, fuente.fps)


def _analizar_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recorre una fuente de imagenes.")
    parser.add_argument(
        "--fuente",
        type=str,
        required=True,
        help="Carpeta de imagenes, indice de camara (0, 1, ...) o ruta a un video.",
    )
    parser.add_argument(
        "--sin-ventana",
        action="store_true",
        help="No abre ventana de OpenCV (util sin entorno grafico).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = _analizar_argumentos()
    if argumentos.sin_ventana:
        _recorrer_sin_ventana(argumentos.fuente)
    else:
        try:
            _recorrer_con_ventana(argumentos.fuente)
        except cv2.error as error:
            print(f"No se pudo abrir una ventana grafica ({error}).")
            print("Se continua sin ventana.")
            _recorrer_sin_ventana(argumentos.fuente)
