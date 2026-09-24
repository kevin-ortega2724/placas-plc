"""Interfaz grafica del sistema de control de acceso (Fase 09).

Esta interfaz no reimplementa ninguna logica: solo llama al pipeline de
vision (Fase 05), las reglas de acceso (Fase 07) y la traduccion a
senales con el PLC simulado (Fase 08). Si algo se ve mal aqui, el error
esta en esos modulos, no en esta interfaz.
"""
from __future__ import annotations

from datetime import date, datetime
from datetime import time as dtime
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from placas.comunicacion import ClienteModbusAcceso
from placas.configuracion import Plc, cargar_autorizados, cargar_reglas, cargar_reportados
from placas.localizacion import dibujar_candidatos
from placas.pipeline import procesar_imagen
from placas.plc_simulado import PlcSimulado
from placas.preproceso import preprocesar
from placas.reglas import decidir
from placas.senales import Senales, a_modbus, a_senales

RUTA_REGLAS = "config/reglas.yaml"
RUTA_AUTORIZADOS = "config/autorizados.csv"
RUTA_REPORTADOS = "config/reportados.csv"

COLOR_DECISION = {
    "PERMITIDO": "#2ecc71",
    "REPORTADO": "#e74c3c",
    "NO_AUTORIZADO": "#e74c3c",
    "PICO_Y_PLACA": "#e74c3c",
    "LECTURA_DUDOSA": "#f39c12",
    "SIN_VEHICULO": "#95a5a6",
}


@st.cache_resource
def _cargar_configuracion():
    reglas = cargar_reglas(RUTA_REGLAS)
    autorizados = cargar_autorizados(RUTA_AUTORIZADOS)
    reportados = cargar_reportados(RUTA_REPORTADOS)
    return reglas, autorizados, reportados


@st.cache_resource
def _obtener_plc() -> PlcSimulado:
    return PlcSimulado()


def _barra_lateral() -> tuple[np.ndarray | None, str | None, datetime, bool, str]:
    st.sidebar.header("Fuente")
    origen = st.sidebar.radio("Origen de la imagen", ["Carpeta", "Subir imagen", "Camara"])

    imagen = None
    nombre = None
    if origen == "Carpeta":
        carpeta = Path(st.sidebar.text_input("Carpeta", value="data/sinteticas"))
        archivos = sorted(p.name for p in carpeta.glob("*.png")) if carpeta.exists() else []
        if archivos:
            nombre = st.sidebar.selectbox("Imagen", archivos)
            imagen = cv2.imread(str(carpeta / nombre))
        else:
            st.sidebar.warning("No hay imagenes .png en esa carpeta.")
    elif origen == "Subir imagen":
        archivo_subido = st.sidebar.file_uploader("Imagen", type=["png", "jpg", "jpeg"])
        if archivo_subido is not None:
            datos = np.frombuffer(archivo_subido.read(), np.uint8)
            imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
            nombre = archivo_subido.name
    else:  # Camara: usa la camara del navegador (st.camera_input), no cv2.VideoCapture,
        # porque un servidor Streamlit no deberia mantener un dispositivo de camara
        # abierto entre una recarga de pagina y otra.
        foto = st.sidebar.camera_input("Tomar foto del vehiculo")
        if foto is not None:
            datos = np.frombuffer(foto.getvalue(), np.uint8)
            imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
            nombre = "camara.png"

    st.sidebar.header("Fecha y hora")
    usar_fecha_real = st.sidebar.checkbox("Usar fecha y hora reales", value=False)
    if usar_fecha_real:
        fecha_hora = datetime.now()
        st.sidebar.caption(f"Usando: {fecha_hora:%Y-%m-%d %H:%M}")
    else:
        fecha_sel = st.sidebar.date_input("Fecha simulada", value=date(2024, 1, 15))
        hora_sel = st.sidebar.time_input("Hora simulada", value=dtime(7, 0))
        fecha_hora = datetime.combine(fecha_sel, hora_sel)

    mostrar_pasos = st.sidebar.checkbox("Mostrar pasos intermedios", value=False)

    st.sidebar.header("Destino de las senales")
    destino = st.sidebar.selectbox("Enviar a", ["PLC simulado", "Modbus TCP"])

    return imagen, nombre, fecha_hora, mostrar_pasos, destino


def _lampara(etiqueta: str, encendida: bool, color_encendido: str) -> str:
    color = color_encendido if encendida else "#555555"
    return (
        "<div style='display:inline-block;text-align:center;margin-right:16px'>"
        f"<div style='width:28px;height:28px;border-radius:50%;background:{color};"
        "margin:auto;border:2px solid #222'></div>"
        f"<small>{etiqueta}</small></div>"
    )


def _enviar_por_modbus(senales: Senales, config_plc: Plc) -> None:
    """Envia las senales a un servidor Modbus real (por ejemplo,
    hmi/servidor_prueba.py). Un fallo de conexion se muestra en la
    interfaz, pero nunca la detiene (ver Fase 10).
    """
    cliente = ClienteModbusAcceso(
        config_plc.host, config_plc.puerto, config_plc.unidad, intentos_conexion=1, tiempo_espera_s=1.0
    )
    if not cliente.conectar():
        st.error(f"No se pudo conectar al PLC en {config_plc.host}:{config_plc.puerto}.")
        return
    try:
        if cliente.enviar(senales):
            st.success(f"Senales enviadas por Modbus a {config_plc.host}:{config_plc.puerto}.")
        else:
            st.error("Se conecto al PLC, pero fallo el envio de las senales.")
    finally:
        cliente.detener()


def main() -> None:
    st.set_page_config(page_title="Control de acceso - placas", layout="wide")
    st.title("Control de acceso vehicular con pico y placa")

    reglas, autorizados, reportados = _cargar_configuracion()
    plc = _obtener_plc()

    imagen, nombre, fecha_hora, mostrar_pasos, destino = _barra_lateral()

    if imagen is None:
        st.info("Seleccione o suba una imagen en la barra lateral para comenzar.")
        return

    resultado = procesar_imagen(imagen, reglas)
    decision = decidir(resultado.lectura, fecha_hora, reglas, autorizados, reportados)
    senales = a_senales(decision, resultado.lectura)
    coils, registros = a_modbus(senales)

    plc.recibir_senales(senales)
    plc.ciclo(0.05)

    if destino == "Modbus TCP":
        _enviar_por_modbus(senales, reglas.plc)

    columna_imagen, columna_info = st.columns([2, 1])

    with columna_imagen:
        imagen_anotada = dibujar_candidatos(imagen, resultado.deteccion)
        st.image(cv2.cvtColor(imagen_anotada, cv2.COLOR_BGR2RGB), caption=nombre, width="stretch")
        if resultado.deteccion.encontrada:
            st.image(
                cv2.cvtColor(resultado.deteccion.recorte, cv2.COLOR_BGR2RGB),
                caption=f"Recorte (metodo: {resultado.deteccion.metodo})",
                width=300,
            )

    with columna_info:
        color = COLOR_DECISION[decision.nombre]
        st.markdown(
            f"<div style='background:{color};color:white;padding:12px;border-radius:8px;"
            f"text-align:center;font-size:1.3em'><b>{decision.nombre}</b></div>",
            unsafe_allow_html=True,
        )
        st.caption(decision.motivo)

        if resultado.lectura is not None:
            st.metric("Placa leida", resultado.lectura.placa_normalizada)
            st.metric("Confianza OCR", f"{resultado.lectura.confianza:.2f}")
        else:
            st.metric("Placa leida", "-")

        st.subheader("Lamparas del PLC")
        html_lamparas = "".join(
            [
                _lampara("Q0 talanquera", plc.q0_talanquera, "#2ecc71"),
                _lampara("Q1 luz roja", plc.q1_luz_roja, "#e74c3c"),
                _lampara("Q2 luz ambar", plc.q2_luz_ambar, "#f39c12"),
                _lampara("Q3 alarma com.", plc.q3_alarma_comunicacion, "#e67e22"),
            ]
        )
        st.markdown(html_lamparas, unsafe_allow_html=True)

        st.subheader("Senales que se enviarian")
        st.table(
            {
                "Coil": [
                    "vehiculo_presente",
                    "acceso_permitido",
                    "acceso_denegado",
                    "lectura_dudosa",
                    "nueva_lectura",
                ],
                "Valor": coils,
            }
        )
        st.table(
            {
                "Registro": ["codigo_decision", "confianza", "ultimo_digito", "watchdog"],
                "Valor": registros,
            }
        )

    if mostrar_pasos:
        with st.expander("Pasos intermedios del preprocesamiento"):
            pasos = preprocesar(imagen, reglas.preproceso)
            columnas = st.columns(5)
            etiquetas_pasos = [
                ("Grises", pasos.gris),
                ("CLAHE", pasos.ecualizado),
                ("Bilateral", pasos.filtrado),
                ("Canny", pasos.bordes),
                ("Cierre", pasos.cerrado),
            ]
            for columna, (etiqueta, paso) in zip(columnas, etiquetas_pasos):
                columna.image(paso, caption=etiqueta, width="stretch")


if __name__ == "__main__":
    main()
