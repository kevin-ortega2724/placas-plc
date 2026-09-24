"""Pruebas del pipeline completo (Fase 05), sin depender de EasyOCR."""
from pathlib import Path

import cv2
import numpy as np

import placas.pipeline as pipeline_mod
from placas.configuracion import cargar_reglas
from placas.generador import dibujar_placa, generar_fondo_vehiculo, pegar_placa_en_fondo
from placas.ocr import Lectura

RAIZ = Path(__file__).resolve().parent.parent
RUTA_REGLAS = RAIZ / "config" / "reglas.yaml"


def _imagen_con_placa(semilla=3) -> np.ndarray:
    rng = np.random.default_rng(semilla)
    placa_img = dibujar_placa("ABC123", "CIUDAD")
    placa_bgr = cv2.cvtColor(np.array(placa_img), cv2.COLOR_RGB2BGR)
    fondo = generar_fondo_vehiculo(1000, 700, rng)
    return pegar_placa_en_fondo(placa_bgr, fondo, rng)


def test_procesar_imagen_encuentra_placa_y_mide_tiempos(monkeypatch):
    lectura_falsa = Lectura(
        texto_crudo="ABC123",
        placa_normalizada="ABC123",
        confianza=0.95,
        formato_valido=True,
        tipo="carro",
    )
    monkeypatch.setattr(pipeline_mod, "leer_placa", lambda recorte, reglas: lectura_falsa)

    reglas = cargar_reglas(RUTA_REGLAS)
    imagen = _imagen_con_placa()

    resultado = pipeline_mod.procesar_imagen(imagen, reglas)

    assert resultado.deteccion.encontrada
    assert resultado.lectura.placa_normalizada == "ABC123"
    assert set(resultado.tiempos_s) >= {"preproceso", "localizacion", "ocr", "total"}
    assert resultado.tiempos_s["total"] > 0


def test_procesar_imagen_sin_placa_no_llama_ocr(monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        pipeline_mod, "leer_placa", lambda recorte, reglas: llamadas.append(1)
    )

    reglas = cargar_reglas(RUTA_REGLAS)
    imagen = np.full((300, 400, 3), 100, dtype=np.uint8)

    resultado = pipeline_mod.procesar_imagen(imagen, reglas)

    assert not resultado.deteccion.encontrada
    assert resultado.lectura is None
    assert llamadas == []
