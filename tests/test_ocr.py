"""Pruebas de normalizacion y validacion de OCR (Fase 05), sin EasyOCR."""
from placas.configuracion import Correcciones, FormatoPlaca
from placas.ocr import _determinar_tipo, normalizar_texto

CORRECCIONES = Correcciones(
    a_letra={"0": "O", "1": "I", "2": "Z", "5": "S", "8": "B", "6": "G"},
    a_numero={"O": "0", "I": "1", "Z": "2", "S": "5", "B": "8", "G": "6", "D": "0", "Q": "0"},
)
FORMATO = FormatoPlaca(carro="^[A-Z]{3}[0-9]{3}$", moto="^[A-Z]{3}[0-9]{2}[A-Z]$")


def test_normalizar_texto_corrige_letra_confundida_con_digito():
    assert normalizar_texto("A8C 12O", CORRECCIONES) == "ABC120"


def test_normalizar_texto_quita_guiones():
    assert normalizar_texto("UTP-123", CORRECCIONES) == "UTP123"


def test_normalizar_texto_pasa_a_mayusculas():
    assert normalizar_texto("abc123", CORRECCIONES) == "ABC123"


def test_normalizar_texto_quita_caracteres_extranos():
    assert normalizar_texto("ABC.123!", CORRECCIONES) == "ABC123"


def test_determinar_tipo_carro():
    assert _determinar_tipo("ABC123", FORMATO) == "carro"


def test_determinar_tipo_ninguno_si_no_cumple_formato():
    assert _determinar_tipo("AB12", FORMATO) is None
