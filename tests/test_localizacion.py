"""Pruebas de localizacion de la placa (Fase 04)."""
import cv2
import numpy as np

from placas.configuracion import Localizacion
from placas.generador import dibujar_placa, generar_fondo_vehiculo, pegar_placa_en_fondo
from placas.localizacion import localizar_por_bordes, localizar_por_color

PARAMETROS = Localizacion(
    hsv_amarillo_bajo=(15, 80, 80),
    hsv_amarillo_alto=(35, 255, 255),
    area_minima=2000,
    relacion_aspecto_esperada=2.0,
    tolerancia_aspecto=0.6,
    rectangularidad_minima=0.6,
    ancho_rectificado=400,
    alto_rectificado=200,
)


def _imagen_con_placa(semilla=1) -> np.ndarray:
    rng = np.random.default_rng(semilla)
    placa_img = dibujar_placa("ABC123", "CIUDAD")
    placa_bgr = cv2.cvtColor(np.array(placa_img), cv2.COLOR_RGB2BGR)
    fondo = generar_fondo_vehiculo(1000, 700, rng)
    return pegar_placa_en_fondo(placa_bgr, fondo, rng)


def test_localizar_por_color_encuentra_la_placa():
    imagen = _imagen_con_placa()
    deteccion = localizar_por_color(imagen, PARAMETROS)

    assert deteccion.encontrada is True
    assert deteccion.metodo == "color"
    assert deteccion.recorte.shape == (PARAMETROS.alto_rectificado, PARAMETROS.ancho_rectificado, 3)
    assert deteccion.caja.shape == (4, 2)


def test_localizar_por_bordes_encuentra_la_placa():
    imagen = _imagen_con_placa()
    deteccion = localizar_por_bordes(imagen, PARAMETROS)

    assert deteccion.encontrada is True
    assert deteccion.metodo == "bordes"
    assert deteccion.recorte.shape == (PARAMETROS.alto_rectificado, PARAMETROS.ancho_rectificado, 3)


def test_localizar_por_color_no_encuentra_nada_en_imagen_sin_placa():
    imagen = np.full((300, 400, 3), 100, dtype=np.uint8)  # solo fondo gris
    deteccion = localizar_por_color(imagen, PARAMETROS)

    assert deteccion.encontrada is False
    assert deteccion.recorte is None


def test_deteccion_puntaje_entre_cero_y_uno():
    imagen = _imagen_con_placa()
    deteccion = localizar_por_color(imagen, PARAMETROS)

    assert 0.0 <= deteccion.puntaje <= 1.0
