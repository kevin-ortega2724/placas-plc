"""Pruebas del generador de placas sinteticas (Fase 01)."""
import csv
import re
from pathlib import Path

import numpy as np

from placas.generador import generar_dataset, generar_placa_aleatoria

RAIZ = Path(__file__).resolve().parent.parent
RUTA_AUTORIZADOS = RAIZ / "config" / "autorizados.csv"
RUTA_REPORTADOS = RAIZ / "config" / "reportados.csv"
PATRON_PLACA_CARRO = re.compile(r"^[A-Z]{3}[0-9]{3}$")


def test_generar_placa_aleatoria_cumple_formato():
    rng = np.random.default_rng(1)
    for _ in range(20):
        placa = generar_placa_aleatoria(rng)
        assert PATRON_PLACA_CARRO.match(placa)


def test_generar_dataset_crea_n_archivos_de_imagen(tmp_path):
    generar_dataset(
        n=5,
        semilla=42,
        carpeta_salida=tmp_path,
        ruta_autorizados=RUTA_AUTORIZADOS,
        ruta_reportados=RUTA_REPORTADOS,
    )

    imagenes = list(tmp_path.glob("*.png"))
    assert len(imagenes) == 5


def test_generar_dataset_escribe_etiquetas_con_formato_valido(tmp_path):
    ruta_csv = generar_dataset(
        n=5,
        semilla=42,
        carpeta_salida=tmp_path,
        ruta_autorizados=RUTA_AUTORIZADOS,
        ruta_reportados=RUTA_REPORTADOS,
    )

    with ruta_csv.open(encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))

    assert len(filas) == 5
    for fila in filas:
        assert PATRON_PLACA_CARRO.match(fila["placa"])
        assert (tmp_path / fila["archivo"]).exists()


def test_generar_dataset_incluye_placas_autorizadas_y_reportadas(tmp_path):
    ruta_csv = generar_dataset(
        n=20,
        semilla=42,
        carpeta_salida=tmp_path,
        ruta_autorizados=RUTA_AUTORIZADOS,
        ruta_reportados=RUTA_REPORTADOS,
    )

    with ruta_csv.open(encoding="utf-8") as archivo:
        placas_generadas = {fila["placa"] for fila in csv.DictReader(archivo)}

    assert "UTP123" in placas_generadas  # config/autorizados.csv
    assert "XYZ999" in placas_generadas  # config/reportados.csv


def test_generar_dataset_es_reproducible_con_la_misma_semilla(tmp_path):
    carpeta_a = tmp_path / "a"
    carpeta_b = tmp_path / "b"

    csv_a = generar_dataset(
        n=5,
        semilla=7,
        carpeta_salida=carpeta_a,
        ruta_autorizados=RUTA_AUTORIZADOS,
        ruta_reportados=RUTA_REPORTADOS,
    )
    csv_b = generar_dataset(
        n=5,
        semilla=7,
        carpeta_salida=carpeta_b,
        ruta_autorizados=RUTA_AUTORIZADOS,
        ruta_reportados=RUTA_REPORTADOS,
    )

    with csv_a.open(encoding="utf-8") as archivo:
        placas_a = [fila["placa"] for fila in csv.DictReader(archivo)]
    with csv_b.open(encoding="utf-8") as archivo:
        placas_b = [fila["placa"] for fila in csv.DictReader(archivo)]

    assert placas_a == placas_b
