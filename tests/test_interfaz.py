"""Pruebas de humo de la interfaz Streamlit (Fase 09), via AppTest.

La logica de negocio (pipeline, reglas, senales) ya tiene sus propias
pruebas en cada modulo; aqui solo se verifica que la interfaz los
conecte sin lanzar excepciones en sus principales estados.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
RUTA_APP = str(RAIZ / "app" / "interfaz.py")


@pytest.fixture(scope="module", autouse=True)
def _dataset_de_prueba():
    from placas.generador import generar_dataset

    carpeta = RAIZ / "data" / "sinteticas"
    if not any(carpeta.glob("*.png")):
        generar_dataset(
            n=3,
            semilla=42,
            carpeta_salida=carpeta,
            ruta_autorizados=RAIZ / "config" / "autorizados.csv",
            ruta_reportados=RAIZ / "config" / "reportados.csv",
        )


def test_interfaz_corre_sin_excepciones_con_imagen_de_carpeta():
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=60)
    assert not at.exception


def test_interfaz_muestra_pasos_intermedios_sin_excepciones():
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=60)

    for casilla in at.sidebar.checkbox:
        if "pasos intermedios" in casilla.label.lower():
            casilla.set_value(True)
    at.run(timeout=60)

    assert not at.exception


def test_interfaz_sin_imagen_seleccionada_no_lanza_excepcion():
    at = AppTest.from_file(RUTA_APP)
    at.run(timeout=60)

    for radio in at.sidebar.radio:
        if "origen" in radio.label.lower():
            radio.set_value("Subir imagen")
    at.run(timeout=60)

    assert not at.exception
