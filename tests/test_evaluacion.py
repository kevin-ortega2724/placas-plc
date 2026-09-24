"""Pruebas de las metricas de evaluacion (Fase 06), sin depender de EasyOCR."""
import pytest

from placas.evaluacion import exactitud_placa_completa, exactitud_por_caracter, matriz_confusion


def test_exactitud_por_caracter_todo_correcto():
    assert exactitud_por_caracter("ABC123", "ABC123") == 1.0


def test_exactitud_por_caracter_un_error():
    assert exactitud_por_caracter("ABC123", "ABC120") == pytest.approx(5 / 6)


def test_exactitud_por_caracter_penaliza_caracteres_faltantes():
    assert exactitud_por_caracter("ABC123", "ABC12") == pytest.approx(5 / 6)


def test_exactitud_por_caracter_cadena_vacia_esperada():
    assert exactitud_por_caracter("", "") == 1.0


def test_exactitud_placa_completa():
    esperadas = ["ABC123", "DEF456"]
    obtenidas = ["ABC123", "DEF450"]
    assert exactitud_placa_completa(esperadas, obtenidas) == 0.5


def test_matriz_confusion_cuenta_aciertos_y_errores():
    matriz = matriz_confusion([("ABC123", "ABC120")])

    assert matriz[("A", "A")] == 1
    assert matriz[("3", "0")] == 1


def test_matriz_confusion_marca_caracter_faltante():
    matriz = matriz_confusion([("ABC123", "ABC12")])

    assert matriz[("3", "_")] == 1
