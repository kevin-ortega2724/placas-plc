"""Evaluacion del sistema de vision sobre el dataset sintetico (Fase 06).

Compara lo que lee el pipeline completo contra la verdad de terreno de
etiquetas.csv, y reporta metricas de localizacion, exactitud de OCR y
tiempos, para decidir donde vale la pena mejorar el sistema.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import cv2

from placas.configuracion import Reglas
from placas.pipeline import procesar_imagen


def exactitud_por_caracter(esperado: str, obtenido: str) -> float:
    """Proporcion de caracteres de 'esperado' que aparecen en la misma
    posicion en 'obtenido'. Una posicion faltante o de mas cuenta como error.
    """
    if not esperado:
        return 1.0 if not obtenido else 0.0
    aciertos = sum(1 for i, c in enumerate(esperado) if i < len(obtenido) and obtenido[i] == c)
    return aciertos / len(esperado)


def exactitud_placa_completa(esperadas: list[str], obtenidas: list[str]) -> float:
    """Proporcion de placas leidas exactamente igual a la verdad de terreno."""
    if not esperadas:
        return 0.0
    aciertos = sum(1 for e, o in zip(esperadas, obtenidas) if e == o)
    return aciertos / len(esperadas)


def matriz_confusion(pares: list[tuple[str, str]]) -> Counter:
    """Cuenta, por posicion, que caracter se leyo (obtenido) en vez de
    cual (esperado). La diagonal (esperado == obtenido) son aciertos. Un
    caracter faltante en 'obtenido' se registra como '_'.
    """
    conteo: Counter = Counter()
    for esperado, obtenido in pares:
        for i, caracter_esperado in enumerate(esperado):
            caracter_obtenido = obtenido[i] if i < len(obtenido) else "_"
            conteo[(caracter_esperado, caracter_obtenido)] += 1
    return conteo


def evaluar_dataset(
    carpeta: str | Path,
    ruta_etiquetas: str | Path,
    reglas: Reglas,
    carpeta_salidas: str | Path = "salidas",
) -> dict:
    """Corre el pipeline sobre cada imagen de carpeta y compara contra
    ruta_etiquetas. Guarda evaluacion.csv y confusiones.png en
    carpeta_salidas, y devuelve un resumen con las metricas principales.
    """
    carpeta = Path(carpeta)
    with Path(ruta_etiquetas).open(encoding="utf-8") as archivo:
        filas_etiquetas = list(csv.DictReader(archivo))

    filas_resultado = []
    pares_caracteres = []
    tiempos_por_etapa: dict[str, list[float]] = {"preproceso": [], "localizacion": [], "ocr": [], "total": []}
    localizadas = 0

    for fila in filas_etiquetas:
        imagen = cv2.imread(str(carpeta / fila["archivo"]))
        resultado = procesar_imagen(imagen, reglas)

        placa_esperada = fila["placa"]
        placa_obtenida = resultado.lectura.placa_normalizada if resultado.lectura else ""

        if resultado.deteccion.encontrada:
            localizadas += 1
        if resultado.lectura is not None:
            pares_caracteres.append((placa_esperada, placa_obtenida))

        for etapa, lista in tiempos_por_etapa.items():
            if etapa in resultado.tiempos_s:
                lista.append(resultado.tiempos_s[etapa])

        filas_resultado.append(
            {
                "archivo": fila["archivo"],
                "placa_esperada": placa_esperada,
                "placa_obtenida": placa_obtenida,
                "localizada": resultado.deteccion.encontrada,
                "exactitud_caracter": round(exactitud_por_caracter(placa_esperada, placa_obtenida), 4),
                "desenfoque_kernel": fila.get("desenfoque_kernel", ""),
                "tiempo_preproceso_s": round(resultado.tiempos_s.get("preproceso", 0.0), 5),
                "tiempo_localizacion_s": round(resultado.tiempos_s.get("localizacion", 0.0), 5),
                "tiempo_ocr_s": round(resultado.tiempos_s.get("ocr", 0.0), 5),
                "tiempo_total_s": round(resultado.tiempos_s.get("total", 0.0), 5),
            }
        )

    total = len(filas_etiquetas)
    resumen = {
        "total_imagenes": total,
        "porcentaje_localizadas": 100 * localizadas / total if total else 0.0,
        "exactitud_placa_completa": exactitud_placa_completa(
            [f["placa_esperada"] for f in filas_resultado],
            [f["placa_obtenida"] for f in filas_resultado],
        ),
        "exactitud_caracter_promedio": (
            sum(f["exactitud_caracter"] for f in filas_resultado) / total if total else 0.0
        ),
        "tiempo_medio_s": {
            etapa: (sum(valores) / len(valores) if valores else 0.0)
            for etapa, valores in tiempos_por_etapa.items()
        },
    }

    carpeta_salidas = Path(carpeta_salidas)
    carpeta_salidas.mkdir(parents=True, exist_ok=True)
    _guardar_csv(filas_resultado, carpeta_salidas / "evaluacion.csv")
    _guardar_matriz_confusion(matriz_confusion(pares_caracteres), carpeta_salidas / "confusiones.png")

    return resumen


def _guardar_csv(filas: list[dict], ruta: Path) -> None:
    if not filas:
        return
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def _guardar_matriz_confusion(matriz: Counter, ruta: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    if not matriz:
        return

    caracteres = sorted({c for par in matriz for c in par})
    indice = {c: i for i, c in enumerate(caracteres)}
    tabla = np.zeros((len(caracteres), len(caracteres)), dtype=int)
    for (esperado, obtenido), cantidad in matriz.items():
        tabla[indice[esperado], indice[obtenido]] = cantidad

    figura, ejes = plt.subplots(figsize=(max(6, len(caracteres) * 0.4), max(6, len(caracteres) * 0.4)))
    imagen = ejes.imshow(tabla, cmap="viridis")
    ejes.set_xticks(range(len(caracteres)))
    ejes.set_xticklabels(caracteres, fontsize=6)
    ejes.set_yticks(range(len(caracteres)))
    ejes.set_yticklabels(caracteres, fontsize=6)
    ejes.set_xlabel("Caracter leido (obtenido)")
    ejes.set_ylabel("Caracter esperado")
    ejes.set_title("Matriz de confusion de caracteres")
    figura.colorbar(imagen, ax=ejes)
    figura.tight_layout()
    figura.savefig(ruta, dpi=150)
    plt.close(figura)


if __name__ == "__main__":
    import argparse

    from placas.configuracion import cargar_reglas

    parser = argparse.ArgumentParser(description="Evalua el sistema de vision sobre un dataset.")
    parser.add_argument("--fuente", type=str, default="data/sinteticas")
    parser.add_argument("--etiquetas", type=str, default="data/sinteticas/etiquetas.csv")
    parser.add_argument("--reglas", type=str, default="config/reglas.yaml")
    parser.add_argument("--salida", type=str, default="salidas")
    argumentos = parser.parse_args()

    reglas_cargadas = cargar_reglas(argumentos.reglas)
    resumen = evaluar_dataset(argumentos.fuente, argumentos.etiquetas, reglas_cargadas, argumentos.salida)

    print(f"Imagenes evaluadas: {resumen['total_imagenes']}")
    print(f"Localizadas: {resumen['porcentaje_localizadas']:.1f} %")
    print(f"Exactitud por placa completa: {resumen['exactitud_placa_completa'] * 100:.1f} %")
    print(f"Exactitud por caracter: {resumen['exactitud_caracter_promedio'] * 100:.1f} %")
    print("Tiempo medio por etapa (s):", {k: round(v, 4) for k, v in resumen["tiempo_medio_s"].items()})
    print(f"Detalle: {argumentos.salida}/evaluacion.csv")
    print(f"Matriz de confusion: {argumentos.salida}/confusiones.png")
