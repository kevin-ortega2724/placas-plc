"""Generador de placas sinteticas para pruebas del sistema de vision (Fase 01).

No usa placas reales: genera placas colombianas ficticias con datos
inventados para no exponer informacion personal, y guarda la placa real
(verdad de terreno) junto con cada imagen en etiquetas.csv.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from placas.configuracion import cargar_autorizados, cargar_reportados

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"
CIUDADES_FICTICIAS = ["VALLERURAL", "NORTESOL", "RIOAZUL", "SIERRAVERDE", "PUERTOLUNA"]

# Proporcion real aproximada de una placa colombiana (33 x 16.5 cm = 2:1).
ANCHO_PLACA = 660
ALTO_PLACA = 330

# Fuentes sans condensadas comunes por sistema operativo. Se usa la primera
# que exista; si ninguna existe, se recurre a la fuente por defecto de Pillow.
FUENTES_CANDIDATAS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf",
    "C:/Windows/Fonts/arialnb.ttf",
    "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
]


@dataclass
class ParametrosDegradacion:
    """Parametros de degradacion aplicados a una imagen (para etiquetas.csv)."""

    rotacion_grados: float
    perspectiva_desplazamiento_px: int
    desenfoque_kernel: int
    ruido_sigma: float
    brillo: float
    contraste: float


def generar_placa_aleatoria(rng: np.random.Generator) -> str:
    """Genera una placa de carro aleatoria con formato ABC123."""
    letras = "".join(str(rng.choice(list(LETRAS))) for _ in range(3))
    numeros = "".join(str(rng.choice(list(DIGITOS))) for _ in range(3))
    return f"{letras}{numeros}"


def _cargar_fuente(ruta_fuente: str | Path | None, tamano: int) -> ImageFont.ImageFont:
    candidatos = [ruta_fuente] if ruta_fuente else []
    candidatos += FUENTES_CANDIDATAS
    for candidato in candidatos:
        if candidato and Path(candidato).exists():
            return ImageFont.truetype(str(candidato), tamano)
    return ImageFont.load_default(size=tamano)


_LIENZO_MEDIDA = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def _fuente_ajustada_al_ancho(
    texto: str, ruta_fuente: str | Path | None, ancho_max: int, tamano_inicial: int
) -> ImageFont.ImageFont:
    """Reduce el tamano de fuente hasta que el texto quepa en ancho_max.

    Evita que letras o numeros queden cortados contra el borde de la
    placa, lo que arruinaria la lectura en las fases de OCR.
    """
    tamano = tamano_inicial
    while tamano > 10:
        fuente = _cargar_fuente(ruta_fuente, tamano)
        caja = _LIENZO_MEDIDA.textbbox((0, 0), texto, font=fuente)
        if caja[2] - caja[0] <= ancho_max:
            return fuente
        tamano -= 2
    return _cargar_fuente(ruta_fuente, 10)


def dibujar_placa(placa: str, ciudad: str, ruta_fuente: str | Path | None = None) -> Image.Image:
    """Dibuja una placa colombiana ficticia.

    Fondo amarillo, borde y texto negro con la placa (p. ej. "ABC 123"),
    y una franja inferior con el nombre de una ciudad ficticia.
    """
    imagen = Image.new("RGB", (ANCHO_PLACA, ALTO_PLACA), (255, 205, 0))
    dibujo = ImageDraw.Draw(imagen)

    grosor_borde = 10
    dibujo.rectangle(
        [
            grosor_borde // 2,
            grosor_borde // 2,
            ANCHO_PLACA - grosor_borde // 2,
            ALTO_PLACA - grosor_borde // 2,
        ],
        outline=(0, 0, 0),
        width=grosor_borde,
    )

    alto_franja = int(ALTO_PLACA * 0.18)
    dibujo.rectangle(
        [grosor_borde, ALTO_PLACA - alto_franja, ANCHO_PLACA - grosor_borde, ALTO_PLACA - grosor_borde],
        fill=(0, 0, 0),
    )

    texto = f"{placa[:3]} {placa[3:]}"
    ancho_max_texto = ANCHO_PLACA - 2 * grosor_borde - 40
    fuente_placa = _fuente_ajustada_al_ancho(texto, ruta_fuente, ancho_max_texto, int(ALTO_PLACA * 0.5))
    caja = dibujo.textbbox((0, 0), texto, font=fuente_placa)
    x = (ANCHO_PLACA - (caja[2] - caja[0])) // 2 - caja[0]
    y = (ALTO_PLACA - alto_franja - (caja[3] - caja[1])) // 2 - caja[1] - grosor_borde // 2
    dibujo.text((x, y), texto, font=fuente_placa, fill=(0, 0, 0))

    ancho_max_ciudad = ANCHO_PLACA - 2 * grosor_borde - 20
    fuente_ciudad = _fuente_ajustada_al_ancho(ciudad, ruta_fuente, ancho_max_ciudad, int(alto_franja * 0.6))
    caja_ciudad = dibujo.textbbox((0, 0), ciudad, font=fuente_ciudad)
    x_ciudad = (ANCHO_PLACA - (caja_ciudad[2] - caja_ciudad[0])) // 2 - caja_ciudad[0]
    y_ciudad = (
        ALTO_PLACA
        - alto_franja
        + (alto_franja - (caja_ciudad[3] - caja_ciudad[1])) // 2
        - caja_ciudad[1]
    )
    dibujo.text((x_ciudad, y_ciudad), ciudad, font=fuente_ciudad, fill=(255, 255, 255))

    return imagen


def generar_fondo_vehiculo(ancho: int, alto: int, rng: np.random.Generator) -> np.ndarray:
    """Crea un fondo gris con degradado vertical y ruido, que simula la
    parte frontal de un vehiculo sobre la que despues se pega la placa.
    """
    base = rng.integers(70, 120)
    variacion = rng.integers(-20, 20, size=(alto,))
    gradiente = np.clip(base + variacion, 30, 200).astype(np.uint8)
    fondo = np.tile(gradiente[:, None], (1, ancho))
    fondo = cv2.cvtColor(fondo, cv2.COLOR_GRAY2BGR)
    ruido = rng.normal(0, 8, fondo.shape)
    return np.clip(fondo.astype(np.float64) + ruido, 0, 255).astype(np.uint8)


def pegar_placa_en_fondo(placa_bgr: np.ndarray, fondo: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Pega la placa sobre el fondo en una posicion aleatoria, para que
    las fases de localizacion tengan que buscarla en la imagen.
    """
    alto_f, ancho_f = fondo.shape[:2]
    escala = (ancho_f * 0.5) / placa_bgr.shape[1]
    nuevo_ancho = int(placa_bgr.shape[1] * escala)
    nuevo_alto = int(placa_bgr.shape[0] * escala)
    placa_redim = cv2.resize(placa_bgr, (nuevo_ancho, nuevo_alto))

    x = int(rng.integers(0, max(ancho_f - nuevo_ancho, 1)))
    y_min = int((alto_f - nuevo_alto) * 0.3)
    y = int(rng.integers(y_min, max(alto_f - nuevo_alto, y_min + 1)))

    resultado = fondo.copy()
    resultado[y : y + nuevo_alto, x : x + nuevo_ancho] = placa_redim
    return resultado


def aplicar_degradaciones(
    imagen: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, ParametrosDegradacion]:
    """Aplica rotacion, perspectiva, desenfoque, ruido gaussiano y cambios
    de brillo/contraste, y devuelve la imagen junto a los parametros usados.
    """
    alto, ancho = imagen.shape[:2]

    rotacion = float(rng.uniform(-15, 15))
    matriz_rot = cv2.getRotationMatrix2D((ancho / 2, alto / 2), rotacion, 1.0)
    imagen = cv2.warpAffine(imagen, matriz_rot, (ancho, alto), borderMode=cv2.BORDER_REPLICATE)

    desplazamiento = int(rng.integers(0, 15))
    origen = np.float32([[0, 0], [ancho, 0], [0, alto], [ancho, alto]])
    destino = np.float32(
        [
            [rng.integers(0, desplazamiento + 1), rng.integers(0, desplazamiento + 1)],
            [ancho - rng.integers(0, desplazamiento + 1), rng.integers(0, desplazamiento + 1)],
            [rng.integers(0, desplazamiento + 1), alto - rng.integers(0, desplazamiento + 1)],
            [ancho - rng.integers(0, desplazamiento + 1), alto - rng.integers(0, desplazamiento + 1)],
        ]
    )
    matriz_persp = cv2.getPerspectiveTransform(origen, destino)
    imagen = cv2.warpPerspective(imagen, matriz_persp, (ancho, alto), borderMode=cv2.BORDER_REPLICATE)

    kernel = int(rng.choice([1, 3, 5]))
    if kernel > 1:
        imagen = cv2.GaussianBlur(imagen, (kernel, kernel), 0)

    sigma = float(rng.uniform(0, 12))
    ruido = rng.normal(0, sigma, imagen.shape)
    imagen = np.clip(imagen.astype(np.float64) + ruido, 0, 255).astype(np.uint8)

    brillo = float(rng.uniform(-30, 30))
    contraste = float(rng.uniform(0.8, 1.2))
    imagen = np.clip(imagen.astype(np.float64) * contraste + brillo, 0, 255).astype(np.uint8)

    parametros = ParametrosDegradacion(
        rotacion_grados=round(rotacion, 2),
        perspectiva_desplazamiento_px=desplazamiento,
        desenfoque_kernel=kernel,
        ruido_sigma=round(sigma, 2),
        brillo=round(brillo, 2),
        contraste=round(contraste, 3),
    )
    return imagen, parametros


def _placas_conocidas(ruta_autorizados: str | Path, ruta_reportados: str | Path) -> list[str]:
    autorizados = cargar_autorizados(ruta_autorizados)
    reportados = cargar_reportados(ruta_reportados)
    return list(autorizados.keys()) + list(reportados.keys())


def generar_dataset(
    n: int,
    semilla: int,
    carpeta_salida: str | Path,
    ruta_autorizados: str | Path,
    ruta_reportados: str | Path,
    ruta_fuente: str | Path | None = None,
) -> Path:
    """Genera n imagenes de placas sinteticas y su archivo etiquetas.csv.

    Incluye primero las placas de autorizados.csv y reportados.csv, y
    completa con placas aleatorias, para que existan ejemplos de todos
    los casos de decision del ENUNCIADO.
    """
    rng = np.random.default_rng(semilla)
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    placas = _placas_conocidas(ruta_autorizados, ruta_reportados)[:n]
    while len(placas) < n:
        placas.append(generar_placa_aleatoria(rng))

    filas = []
    for indice, placa in enumerate(placas):
        ciudad = str(rng.choice(CIUDADES_FICTICIAS))
        placa_img = dibujar_placa(placa, ciudad, ruta_fuente)
        placa_bgr = cv2.cvtColor(np.array(placa_img), cv2.COLOR_RGB2BGR)

        fondo = generar_fondo_vehiculo(1000, 700, rng)
        compuesta = pegar_placa_en_fondo(placa_bgr, fondo, rng)
        final, parametros = aplicar_degradaciones(compuesta, rng)

        nombre_archivo = f"placa_{indice:04d}.png"
        cv2.imwrite(str(carpeta_salida / nombre_archivo), final)

        fila = {"archivo": nombre_archivo, "placa": placa}
        fila.update(asdict(parametros))
        filas.append(fila)

    ruta_csv = carpeta_salida / "etiquetas.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)

    return ruta_csv


def _analizar_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera placas sinteticas para pruebas.")
    parser.add_argument("--n", type=int, default=200, help="Numero de imagenes a generar.")
    parser.add_argument("--semilla", type=int, default=42, help="Semilla para reproducibilidad.")
    parser.add_argument("--salida", type=str, default="data/sinteticas", help="Carpeta de salida.")
    parser.add_argument("--autorizados", type=str, default="config/autorizados.csv")
    parser.add_argument("--reportados", type=str, default="config/reportados.csv")
    parser.add_argument("--fuente", type=str, default=None, help="Ruta a una fuente TrueType.")
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = _analizar_argumentos()
    ruta_csv = generar_dataset(
        n=argumentos.n,
        semilla=argumentos.semilla,
        carpeta_salida=argumentos.salida,
        ruta_autorizados=argumentos.autorizados,
        ruta_reportados=argumentos.reportados,
        ruta_fuente=argumentos.fuente,
    )
    print(f"Generadas {argumentos.n} placas en {argumentos.salida}")
    print(f"Etiquetas: {ruta_csv}")
