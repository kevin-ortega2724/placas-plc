"""Pruebas de carga y validacion de configuracion (Fase 00)."""
from pathlib import Path

import pytest

from placas.configuracion import (
    ErrorConfiguracion,
    cargar_autorizados,
    cargar_reglas,
    cargar_reportados,
)

RAIZ = Path(__file__).resolve().parent.parent
RUTA_REGLAS = RAIZ / "config" / "reglas.yaml"
RUTA_AUTORIZADOS = RAIZ / "config" / "autorizados.csv"
RUTA_REPORTADOS = RAIZ / "config" / "reportados.csv"


def test_cargar_reglas_lee_pico_y_placa():
    reglas = cargar_reglas(RUTA_REGLAS)

    assert reglas.pico_y_placa.activo is True
    assert reglas.pico_y_placa.restricciones["lunes"] == [1, 2]
    assert reglas.pico_y_placa.restricciones["viernes"] == [9, 0]
    assert reglas.pico_y_placa.restricciones["sabado"] == []
    assert reglas.pico_y_placa.horarios[0].inicio == "06:00"
    assert reglas.pico_y_placa.horarios[0].fin == "09:00"


def test_cargar_reglas_lee_ocr_formato_correcciones_y_plc():
    reglas = cargar_reglas(RUTA_REGLAS)

    assert reglas.ocr.confianza_minima == pytest.approx(0.80)
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" == reglas.ocr.caracteres_permitidos
    assert reglas.formato_placa.carro == "^[A-Z]{3}[0-9]{3}$"
    assert reglas.correcciones.a_letra["0"] == "O"
    assert reglas.correcciones.a_numero["O"] == "0"
    assert reglas.plc.host == "127.0.0.1"
    assert reglas.plc.puerto == 502
    assert reglas.preproceso.clahe_clip_limit == pytest.approx(2.0)
    assert reglas.preproceso.canny_umbral_bajo == 50
    assert reglas.preproceso.canny_umbral_alto == 150


def test_cargar_reglas_rechaza_dia_invalido(tmp_path):
    ruta = tmp_path / "reglas.yaml"
    ruta.write_text(
        """
pico_y_placa:
  activo: true
  horarios:
    - inicio: "06:00"
      fin: "09:00"
  restricciones:
    lunfardo: [1, 2]
  aplicar_en_festivos: false
  pais_festivos: "CO"
ocr:
  confianza_minima: 0.8
  idiomas: ["es"]
  caracteres_permitidos: "ABC"
formato_placa:
  carro: "^[A-Z]{3}[0-9]{3}$"
  moto: "^[A-Z]{3}[0-9]{2}[A-Z]$"
correcciones:
  a_letra: {}
  a_numero: {}
preproceso:
  clahe_clip_limit: 2.0
  clahe_tamano_grilla: 8
  bilateral_diametro: 9
  bilateral_sigma_color: 75
  bilateral_sigma_espacio: 75
  canny_umbral_bajo: 50
  canny_umbral_alto: 150
  kernel_morfologico: 5
localizacion:
  hsv_amarillo_bajo: [15, 80, 80]
  hsv_amarillo_alto: [35, 255, 255]
  area_minima: 2000
  relacion_aspecto_esperada: 2.0
  tolerancia_aspecto: 0.6
  rectangularidad_minima: 0.6
  ancho_rectificado: 400
  alto_rectificado: 200
plc:
  host: "127.0.0.1"
  puerto: 502
  unidad: 1
  periodo_watchdog_s: 1.0
""",
        encoding="utf-8",
    )

    with pytest.raises(ErrorConfiguracion, match="lunfardo"):
        cargar_reglas(ruta)


def test_cargar_reglas_rechaza_digito_fuera_de_rango(tmp_path):
    ruta = tmp_path / "reglas.yaml"
    ruta.write_text(
        """
pico_y_placa:
  activo: true
  horarios:
    - inicio: "06:00"
      fin: "09:00"
  restricciones:
    lunes: [1, 12]
  aplicar_en_festivos: false
  pais_festivos: "CO"
ocr:
  confianza_minima: 0.8
  idiomas: ["es"]
  caracteres_permitidos: "ABC"
formato_placa:
  carro: "^[A-Z]{3}[0-9]{3}$"
  moto: "^[A-Z]{3}[0-9]{2}[A-Z]$"
correcciones:
  a_letra: {}
  a_numero: {}
preproceso:
  clahe_clip_limit: 2.0
  clahe_tamano_grilla: 8
  bilateral_diametro: 9
  bilateral_sigma_color: 75
  bilateral_sigma_espacio: 75
  canny_umbral_bajo: 50
  canny_umbral_alto: 150
  kernel_morfologico: 5
localizacion:
  hsv_amarillo_bajo: [15, 80, 80]
  hsv_amarillo_alto: [35, 255, 255]
  area_minima: 2000
  relacion_aspecto_esperada: 2.0
  tolerancia_aspecto: 0.6
  rectangularidad_minima: 0.6
  ancho_rectificado: 400
  alto_rectificado: 200
plc:
  host: "127.0.0.1"
  puerto: 502
  unidad: 1
  periodo_watchdog_s: 1.0
""",
        encoding="utf-8",
    )

    with pytest.raises(ErrorConfiguracion, match="digito"):
        cargar_reglas(ruta)


def test_cargar_reglas_rechaza_hora_mal_formada(tmp_path):
    ruta = tmp_path / "reglas.yaml"
    ruta.write_text(
        """
pico_y_placa:
  activo: true
  horarios:
    - inicio: "25:00"
      fin: "09:00"
  restricciones:
    lunes: [1, 2]
  aplicar_en_festivos: false
  pais_festivos: "CO"
ocr:
  confianza_minima: 0.8
  idiomas: ["es"]
  caracteres_permitidos: "ABC"
formato_placa:
  carro: "^[A-Z]{3}[0-9]{3}$"
  moto: "^[A-Z]{3}[0-9]{2}[A-Z]$"
correcciones:
  a_letra: {}
  a_numero: {}
preproceso:
  clahe_clip_limit: 2.0
  clahe_tamano_grilla: 8
  bilateral_diametro: 9
  bilateral_sigma_color: 75
  bilateral_sigma_espacio: 75
  canny_umbral_bajo: 50
  canny_umbral_alto: 150
  kernel_morfologico: 5
localizacion:
  hsv_amarillo_bajo: [15, 80, 80]
  hsv_amarillo_alto: [35, 255, 255]
  area_minima: 2000
  relacion_aspecto_esperada: 2.0
  tolerancia_aspecto: 0.6
  rectangularidad_minima: 0.6
  ancho_rectificado: 400
  alto_rectificado: 200
plc:
  host: "127.0.0.1"
  puerto: 502
  unidad: 1
  periodo_watchdog_s: 1.0
""",
        encoding="utf-8",
    )

    with pytest.raises(ErrorConfiguracion, match="hora"):
        cargar_reglas(ruta)


def test_cargar_reglas_rechaza_confianza_fuera_de_rango(tmp_path):
    ruta = tmp_path / "reglas.yaml"
    ruta.write_text(
        """
pico_y_placa:
  activo: true
  horarios:
    - inicio: "06:00"
      fin: "09:00"
  restricciones:
    lunes: [1, 2]
  aplicar_en_festivos: false
  pais_festivos: "CO"
ocr:
  confianza_minima: 1.5
  idiomas: ["es"]
  caracteres_permitidos: "ABC"
formato_placa:
  carro: "^[A-Z]{3}[0-9]{3}$"
  moto: "^[A-Z]{3}[0-9]{2}[A-Z]$"
correcciones:
  a_letra: {}
  a_numero: {}
preproceso:
  clahe_clip_limit: 2.0
  clahe_tamano_grilla: 8
  bilateral_diametro: 9
  bilateral_sigma_color: 75
  bilateral_sigma_espacio: 75
  canny_umbral_bajo: 50
  canny_umbral_alto: 150
  kernel_morfologico: 5
localizacion:
  hsv_amarillo_bajo: [15, 80, 80]
  hsv_amarillo_alto: [35, 255, 255]
  area_minima: 2000
  relacion_aspecto_esperada: 2.0
  tolerancia_aspecto: 0.6
  rectangularidad_minima: 0.6
  ancho_rectificado: 400
  alto_rectificado: 200
plc:
  host: "127.0.0.1"
  puerto: 502
  unidad: 1
  periodo_watchdog_s: 1.0
""",
        encoding="utf-8",
    )

    with pytest.raises(ErrorConfiguracion, match="confianza"):
        cargar_reglas(ruta)


def test_cargar_autorizados_indexa_por_placa():
    autorizados = cargar_autorizados(RUTA_AUTORIZADOS)

    assert "UTP123" in autorizados
    assert autorizados["UTP123"]["categoria"] == "docente"
    assert autorizados["AMB911"]["excepcion_pico_placa"] is True
    assert autorizados["UTP123"]["excepcion_pico_placa"] is False


def test_cargar_reportados_indexa_por_placa():
    reportados = cargar_reportados(RUTA_REPORTADOS)

    assert "XYZ999" in reportados
    assert reportados["XYZ999"]["motivo"] == "Reportado por seguridad"
