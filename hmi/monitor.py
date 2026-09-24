"""HMI de solo lectura (Fase 12).

Aplicacion Streamlit independiente que solo LEE del PLC por Modbus:
nunca escribe ningun coil ni registro. Muestra el estado de la
talanquera, las luces, la alarma de comunicacion, los contadores y la
ultima decision, actualizando cada 500 ms. Guarda un historico en
salidas/historico.csv para graficar ingresos por hora.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Direcciones de lectura: banco de salidas fisicas que decide el ladder
# (ver plc/openplc/mapa_modbus.md). Confirmar contra la version real de
# OpenPLC antes de apuntar esto a un PLC de verdad.
DIRECCION_COIL_TALANQUERA = 8
DIRECCION_HOLDING_CODIGO_DECISION = 0
DIRECCION_HOLDING_CONTADOR_INGRESOS = 10

RUTA_HISTORICO = Path("salidas/historico.csv")

NOMBRES_DECISION = {
    0: "SIN_VEHICULO",
    1: "LECTURA_DUDOSA",
    2: "REPORTADO",
    3: "NO_AUTORIZADO",
    4: "PICO_Y_PLACA",
    5: "PERMITIDO",
}


@dataclass
class EstadoPlc:
    """Snapshot de solo lectura del estado del PLC."""

    conectado: bool
    talanquera: bool = False
    luz_roja: bool = False
    luz_ambar: bool = False
    alarma_comunicacion: bool = False
    contador_ingresos: int = 0
    contador_rechazos: int = 0
    codigo_decision: int | None = None
    confianza: float | None = None


def leer_estado(cliente: ModbusTcpClient, unidad: int) -> EstadoPlc:
    """Lee el estado del PLC (talanquera, luces, contadores, decision).

    Nunca escribe nada: este es un HMI de solo lectura. Devuelve
    EstadoPlc(conectado=False) ante cualquier error de comunicacion.
    """
    try:
        coils = cliente.read_coils(DIRECCION_COIL_TALANQUERA, count=4, slave=unidad)
        registros_decision = cliente.read_holding_registers(
            DIRECCION_HOLDING_CODIGO_DECISION, count=2, slave=unidad
        )
        registros_contadores = cliente.read_holding_registers(
            DIRECCION_HOLDING_CONTADOR_INGRESOS, count=2, slave=unidad
        )
    except ModbusException:
        return EstadoPlc(conectado=False)

    if coils.isError() or registros_decision.isError() or registros_contadores.isError():
        return EstadoPlc(conectado=False)

    return EstadoPlc(
        conectado=True,
        talanquera=bool(coils.bits[0]),
        luz_roja=bool(coils.bits[1]),
        luz_ambar=bool(coils.bits[2]),
        alarma_comunicacion=bool(coils.bits[3]),
        codigo_decision=registros_decision.registers[0],
        confianza=registros_decision.registers[1] / 1000,
        contador_ingresos=registros_contadores.registers[0],
        contador_rechazos=registros_contadores.registers[1],
    )


def registrar_historico(estado: EstadoPlc) -> None:
    """Agrega una fila al historico CSV, base para graficar ingresos por hora."""
    RUTA_HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    escribir_encabezado = not RUTA_HISTORICO.exists()
    with RUTA_HISTORICO.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        if escribir_encabezado:
            escritor.writerow(
                ["marca_tiempo", "contador_ingresos", "contador_rechazos", "codigo_decision"]
            )
        escritor.writerow(
            [
                datetime.now().isoformat(timespec="seconds"),
                estado.contador_ingresos,
                estado.contador_rechazos,
                estado.codigo_decision,
            ]
        )


def _lampara(etiqueta: str, encendida: bool, color: str) -> str:
    color_real = color if encendida else "#555555"
    return (
        "<div style='display:inline-block;text-align:center;margin-right:16px'>"
        f"<div style='width:28px;height:28px;border-radius:50%;background:{color_real};"
        "margin:auto;border:2px solid #222'></div>"
        f"<small>{etiqueta}</small></div>"
    )


@st.fragment(run_every="0.5s")
def _panel_en_vivo(host: str, puerto: int, unidad: int) -> None:
    cliente = ModbusTcpClient(host, port=puerto, timeout=1.0)
    if not cliente.connect():
        st.error(f"Sin conexion con el PLC en {host}:{puerto}.")
        return

    estado = leer_estado(cliente, unidad)
    cliente.close()

    if not estado.conectado:
        st.error(f"Sin conexion con el PLC en {host}:{puerto}.")
        return

    registrar_historico(estado)

    st.markdown(
        "".join(
            [
                _lampara("Talanquera", estado.talanquera, "#2ecc71"),
                _lampara("Luz roja", estado.luz_roja, "#e74c3c"),
                _lampara("Luz ambar", estado.luz_ambar, "#f39c12"),
                _lampara("Alarma comunicacion", estado.alarma_comunicacion, "#e67e22"),
            ]
        ),
        unsafe_allow_html=True,
    )

    columna1, columna2, columna3 = st.columns(3)
    columna1.metric("Ingresos", estado.contador_ingresos)
    columna2.metric("Rechazos", estado.contador_rechazos)
    columna3.metric("Ultima decision", NOMBRES_DECISION.get(estado.codigo_decision, "-"))
    if estado.confianza is not None:
        st.caption(f"Ultima confianza OCR: {estado.confianza:.2f}")


def _grafica_ingresos_por_hora() -> None:
    if not RUTA_HISTORICO.exists():
        st.info("Aun no hay historico para graficar.")
        return

    df = pd.read_csv(RUTA_HISTORICO, parse_dates=["marca_tiempo"])
    if df.empty:
        st.info("Aun no hay historico para graficar.")
        return

    df["hora"] = df["marca_tiempo"].dt.floor("h")
    maximo_por_hora = df.groupby("hora")["contador_ingresos"].max()
    ingresos_por_hora = maximo_por_hora.diff().fillna(maximo_por_hora.iloc[0])
    st.bar_chart(ingresos_por_hora)


def main() -> None:
    st.set_page_config(page_title="Monitor del PLC (solo lectura)", layout="wide")
    st.title("Monitor del PLC - solo lectura")
    st.caption("Este panel nunca escribe en el PLC: solo lee su estado por Modbus.")

    host = st.sidebar.text_input("Host del PLC", value="127.0.0.1")
    puerto = st.sidebar.number_input("Puerto", value=502, step=1)
    unidad = st.sidebar.number_input("Unidad Modbus", value=1, step=1)

    _panel_en_vivo(host, int(puerto), int(unidad))

    st.subheader("Historico: ingresos por hora")
    _grafica_ingresos_por_hora()


if __name__ == "__main__":
    main()
