"""Pruebas de adquisicion de imagenes (Fase 02)."""
from pathlib import Path

import cv2
import numpy as np
import pytest

from placas.adquisicion import FuenteImagenes


def _crear_imagenes(carpeta: Path, cantidad: int) -> list[str]:
    nombres = []
    for i in range(cantidad):
        imagen = np.full((50, 80, 3), i * 10, dtype=np.uint8)
        nombre = f"img_{i:02d}.png"
        cv2.imwrite(str(carpeta / nombre), imagen)
        nombres.append(nombre)
    return nombres


def test_fuente_imagenes_carpeta_itera_todos_los_archivos(tmp_path):
    _crear_imagenes(tmp_path, 3)

    with FuenteImagenes(str(tmp_path)) as fuente:
        fotogramas = list(fuente)

    assert len(fotogramas) == 3
    for fotograma in fotogramas:
        assert fotograma.imagen.shape == (50, 80, 3)


def test_fuente_imagenes_carpeta_respeta_orden_alfabetico(tmp_path):
    nombres = _crear_imagenes(tmp_path, 3)

    with FuenteImagenes(str(tmp_path)) as fuente:
        nombres_leidos = [f.nombre for f in fuente]

    assert nombres_leidos == sorted(nombres)


def test_fuente_imagenes_ignora_archivos_que_no_son_imagenes(tmp_path):
    _crear_imagenes(tmp_path, 2)
    (tmp_path / "notas.txt").write_text("no es una imagen")

    with FuenteImagenes(str(tmp_path)) as fuente:
        fotogramas = list(fuente)

    assert len(fotogramas) == 2


def test_fuente_imagenes_carpeta_vacia_lanza_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        FuenteImagenes(str(tmp_path))


def test_fuente_imagenes_fuente_inexistente_lanza_error():
    with pytest.raises(FileNotFoundError):
        FuenteImagenes("carpeta/que/no/existe")


def test_fuente_imagenes_es_context_manager_y_libera_sin_error(tmp_path):
    _crear_imagenes(tmp_path, 1)

    fuente = FuenteImagenes(str(tmp_path))
    with fuente as f:
        list(f)
    fuente.liberar()


def test_fuente_imagenes_expone_fps_no_negativo(tmp_path):
    _crear_imagenes(tmp_path, 3)

    with FuenteImagenes(str(tmp_path)) as fuente:
        for _ in fuente:
            pass

    assert fuente.fps >= 0
