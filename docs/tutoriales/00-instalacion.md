# 00 · Instalación y primera ejecución

**¿Trabajas en Windows? Sigue la [guía completa de PowerShell](00-windows.md)**, con comandos que no requieren activar scripts.


**Objetivo:** abrir la interfaz con datos sintéticos. Necesitas Git, Python (3.11 recomendado), terminal y navegador. Reserva conexión a Internet para dependencias y la primera descarga de modelos OCR.

## 1. Obtén el proyecto

```bash
git clone https://github.com/kevin-ortega2724/placas-plc.git
cd placas-plc
```

Si vas a entregar cambios, crea primero un fork desde GitHub y clona la URL de tu fork. Si ya tienes el proyecto, entra a su carpeta; no lo clones dentro de sí mismo.

## 2. Crea un entorno

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes ejecutar directamente `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos siguientes.

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m placas.configuracion
python -m pytest tests/test_configuracion.py -q
```

**Comprueba:** la configuración se imprime y las pruebas pasan. La instalación editable permite importar `placas` desde `src/`.

## 3. Genera una primera muestra

```bash
python -m placas.generador --n 20 --semilla 42
```

Busca `data/sinteticas/etiquetas.csv` y los PNG. El CSV asocia cada imagen con su placa verdadera. Guarda la semilla y el tamaño del conjunto en tu informe. Para comparar ejecuciones, usa también la misma fuente tipográfica y entorno.

## 4. Abre la aplicación

```bash
python -m streamlit run app/interfaz.py
```

Abre `http://localhost:8501`. Elige **Carpeta**, una imagen y **PLC simulado**. La primera lectura puede tardar mientras EasyOCR prepara sus modelos. Detén el servidor con Ctrl+C. En otra sesión basta activar el entorno y repetir este comando.

## Comprueba y entrega

- [ ] La configuración carga sin error.
- [ ] Hay imágenes y etiquetas.
- [ ] La aplicación muestra una imagen y una decisión sin excepción.
- [ ] Anotaste versión de Python, sistema operativo y resultado de la prueba.

**Reto:** genera otro conjunto en `data/sinteticas/otra` usando `--salida data/sinteticas/otra --semilla 7` y selecciona esa carpeta en la interfaz. Compara dos imágenes; no sobrescribas tu conjunto de referencia.

[Continuar: visión](01-vision.md) · [Ayuda](../SOLUCION_DE_PROBLEMAS.md)
