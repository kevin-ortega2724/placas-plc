"""Pruebas de preprocesamiento de imagenes (Fase 03)."""
import numpy as np

from placas.configuracion import Preproceso
from placas.preproceso import (
    a_grises,
    cerrar_morfologico,
    detectar_bordes_canny,
    ecualizar_clahe,
    filtrar_bilateral,
    preprocesar,
)

PARAMETROS = Preproceso(
    clahe_clip_limit=2.0,
    clahe_tamano_grilla=8,
    bilateral_diametro=9,
    bilateral_sigma_color=75.0,
    bilateral_sigma_espacio=75.0,
    canny_umbral_bajo=50,
    canny_umbral_alto=150,
    kernel_morfologico=5,
)


def _imagen_color(alto=120, ancho=160) -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.integers(0, 255, size=(alto, ancho, 3), dtype=np.uint8)


def test_a_grises_reduce_a_un_canal():
    imagen = _imagen_color()
    gris = a_grises(imagen)
    assert gris.shape == imagen.shape[:2]


def test_ecualizar_clahe_mantiene_el_tamano():
    gris = a_grises(_imagen_color())
    ecualizado = ecualizar_clahe(gris, PARAMETROS.clahe_clip_limit, PARAMETROS.clahe_tamano_grilla)
    assert ecualizado.shape == gris.shape
    assert ecualizado.dtype == gris.dtype


def test_filtrar_bilateral_reduce_el_ruido():
    rng = np.random.default_rng(1)
    base = np.full((100, 100), 128, dtype=np.uint8)
    ruidosa = np.clip(base.astype(int) + rng.normal(0, 25, base.shape), 0, 255).astype(np.uint8)

    filtrada = filtrar_bilateral(
        ruidosa,
        PARAMETROS.bilateral_diametro,
        PARAMETROS.bilateral_sigma_color,
        PARAMETROS.bilateral_sigma_espacio,
    )

    assert filtrada.shape == ruidosa.shape
    assert filtrada.std() < ruidosa.std()


def test_detectar_bordes_canny_devuelve_imagen_binaria():
    gris = a_grises(_imagen_color())
    bordes = detectar_bordes_canny(gris, PARAMETROS.canny_umbral_bajo, PARAMETROS.canny_umbral_alto)
    valores_unicos = set(np.unique(bordes).tolist())
    assert valores_unicos <= {0, 255}


def test_cerrar_morfologico_rellena_huecos_pequenos():
    bordes = np.zeros((50, 50), dtype=np.uint8)
    bordes[20, 10:20] = 255
    bordes[20, 22:32] = 255  # hueco de 2 px entre los dos segmentos

    cerrado = cerrar_morfologico(bordes, kernel_size=5)

    assert cerrado[20, 21] == 255  # el hueco se cerro


def test_preprocesar_encadena_todos_los_pasos():
    imagen = _imagen_color()
    resultado = preprocesar(imagen, PARAMETROS)

    assert resultado.gris.shape == imagen.shape[:2]
    assert resultado.ecualizado.shape == imagen.shape[:2]
    assert resultado.filtrado.shape == imagen.shape[:2]
    assert resultado.bordes.shape == imagen.shape[:2]
    assert resultado.cerrado.shape == imagen.shape[:2]


def test_preprocesar_depurar_guarda_pasos_en_carpeta(tmp_path):
    imagen = _imagen_color()

    preprocesar(imagen, PARAMETROS, depurar=True, carpeta_salidas=tmp_path)

    archivos = sorted(p.name for p in tmp_path.iterdir())
    assert "01_grises.png" in archivos
    assert "02_clahe.png" in archivos
    assert "03_bilateral.png" in archivos
    assert "04_canny.png" in archivos
    assert "05_cierre_morfologico.png" in archivos
    assert "00_mosaico.png" in archivos
