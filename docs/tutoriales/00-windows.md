# Inicio en Windows con PowerShell

**Objetivo:** instalar el proyecto, probarlo y abrir la interfaz en Windows. Esta ruta usa Python 3.11 de 64 bits y PowerShell. Las primeras prácticas usan el simulador local y no necesitan OpenPLC ni WSL.

## 1. Prepara las herramientas

Instala Git desde [Git para Windows](https://git-scm.com/install/windows) y prepara Python 3.11 de 64 bits siguiendo la [documentación oficial de Python en Windows](https://docs.python.org/3.11/using/windows.html). Si el laboratorio administra los equipos, solicita que ambas herramientas estén disponibles. VS Code es opcional.

Abre una ventana nueva de PowerShell después de instalar y comprueba:

```powershell
git --version
py -3.11 --version
py -3.11 -c "import struct; print(struct.calcsize('P') * 8)"
```

**Resultado esperado:** Git muestra su versión, Python indica `3.11.x` y el último comando imprime `64`. Si `py -3.11` no encuentra esa versión, resuelve la instalación antes de continuar.

## 2. Descarga el proyecto

Entra a una carpeta donde puedas guardar tus prácticas y ejecuta:

```powershell
git clone https://github.com/kevin-ortega2724/placas-plc.git
cd placas-plc
Get-Location
Get-ChildItem
```

Debes ver `requirements.txt`, `config`, `app` y `src`. Si el proyecto ya está descargado, entra a esa carpeta sin volver a clonarlo. Para entregar cambios, clona tu fork siguiendo [CONTRIBUTING](../../CONTRIBUTING.md).

## 3. Crea el entorno e instala

Ejecuta cada línea y comprueba que termine sin error antes de continuar:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m placas.configuracion
.\.venv\Scripts\python.exe -m pytest tests/test_configuracion.py -q
```

Usamos directamente el Python del entorno. No necesitas activar `Activate.ps1` ni cambiar la política de ejecución de PowerShell. Python documenta este uso sin activación en [venv](https://docs.python.org/3.11/library/venv.html).

**Resultado esperado:** configuración impresa y pruebas aprobadas. La instalación inicial incluye dependencias de visión que pueden tardar en descargarse.

## 4. Genera imágenes y abre la interfaz

```powershell
.\.venv\Scripts\python.exe -m placas.generador --n 20 --semilla 42
.\.venv\Scripts\python.exe -m streamlit run app/interfaz.py
```

Abre `http://localhost:8501` en el navegador. Deja esa terminal abierta mientras usas la aplicación.

1. Selecciona **Carpeta** y conserva `data/sinteticas`.
2. Elige una imagen y **PLC simulado**.
3. Compara la placa leída con `data/sinteticas/etiquetas.csv`.
4. Activa **Mostrar pasos intermedios**.
5. Cambia fecha y hora simuladas y anota la decisión.

La primera lectura puede descargar modelos de EasyOCR. El procesamiento usa CPU; no necesitas configurar CUDA. Detén Streamlit con **Ctrl+C**.

Si las letras generadas no se ven bien, revisa la fuente. El generador intenta usar Arial Narrow Bold en Windows; si no existe, puedes indicar un archivo TrueType disponible en tu equipo:

```powershell
Test-Path 'C:\Windows\Fonts\arial.ttf'
.\.venv\Scripts\python.exe -m placas.generador --n 20 --semilla 42 --fuente 'C:\Windows\Fonts\arial.ttf'
```

Ejecuta el segundo comando solo si la comprobación devuelve `True`. Registra la fuente en el informe: una misma semilla con fuentes distintas puede producir imágenes y métricas diferentes.

## 5. Continúa los tutoriales por etapas

Los comandos `python -m ...` de los siguientes tutoriales se ejecutan en PowerShell sustituyendo `python` por `.\.venv\Scripts\python.exe`. Por ejemplo:

```powershell
.\.venv\Scripts\python.exe -m placas.adquisicion --fuente data/sinteticas --sin-ventana
.\.venv\Scripts\python.exe -m placas.preproceso --imagen data/sinteticas/placa_0000.png
.\.venv\Scripts\python.exe -m placas.pipeline --imagen data/sinteticas/placa_0000.png
.\.venv\Scripts\python.exe -m placas.evaluacion
.\.venv\Scripts\python.exe -m pytest -q
```

Para los fragmentos de código Python del tutorial de reglas, abre primero el intérprete:

```powershell
.\.venv\Scripts\python.exe
```

Pega allí el código Python; no lo pegues directamente en PowerShell. Usa `exit()` para volver a la terminal.

Las rutas relativas como `config/reglas.yaml` de los argumentos también funcionan en Windows. No copies `source`, `sudo` ni `env -u PYTHONPATH`: son instrucciones para otros sistemas. Si una ruta absoluta contiene espacios, escríbela entre comillas.

## 6. Modbus con varias terminales

Abre una ventana PowerShell por proceso. En **cada una**, entra a la carpeta `placas-plc`. No hace falta activar el entorno porque todos estos comandos usan su ejecutable directamente.

**Terminal A — receptor de prueba:**

```powershell
.\.venv\Scripts\python.exe -m hmi.servidor_prueba --host 127.0.0.1 --puerto 5020
```

**Terminal B — interfaz:** modifica `plc.host` a `127.0.0.1` y `plc.puerto` a `5020` en `config/reglas.yaml`; después inicia la aplicación y selecciona **Modbus TCP**.

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/interfaz.py
```

**Resultado esperado:** la terminal A imprime escrituras y la interfaz confirma el envío. Sigue los ensayos de desconexión del [tutorial Modbus](04-modbus.md).

**Terminal C — monitor opcional:**

```powershell
.\.venv\Scripts\python.exe -m streamlit run hmi/monitor.py --server.port 8502
```

Abre `http://localhost:8502` y ajusta el puerto del monitor a `5020` para leer el servidor de prueba. Ese servidor no ejecuta lógica de talanquera: sus contadores y salidas pueden permanecer en cero. Para ver control real necesitas un Runtime PLC con el mapa confirmado; sigue [PLC y HMI](05-plc-hmi.md). La instalación de ese Runtime es una preparación separada del laboratorio.

## 7. Vuelve al proyecto otro día

Abre PowerShell, entra a la carpeta donde clonaste el repositorio y ejecuta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/interfaz.py
```

No necesitas recrear el entorno ni regenerar los datos en cada sesión. Si recibiste cambios en dependencias, vuelve a ejecutar la instalación de `requirements.txt`.

## Problemas frecuentes en Windows

| Síntoma | Acción |
|---|---|
| `git` no se reconoce | Instala Git y abre una nueva terminal |
| `py` no se reconoce o no encuentra 3.11 | Revisa la instalación y el lanzador de Python |
| `python` abre Microsoft Store | Usa el ejecutable `.\.venv\Scripts\python.exe` después de crear el entorno |
| No existe `.\.venv\Scripts\python.exe` | Comprueba la carpeta actual y que la creación del entorno terminó |
| `Activate.ps1` está bloqueado | Sigue esta guía sin activación; no necesitas cambiar políticas |
| No encuentra `config/reglas.yaml` | Ejecuta desde la raíz `placas-plc` |
| No hay distribución compatible al instalar | Comprueba Python 3.11 de 64 bits y conserva el error exacto del paquete |
| Puerto 8501 ocupado | Cierra la instancia anterior con Ctrl+C o usa `--server.port 8503` y abre ese puerto |
| No conecta con Modbus | Comprueba receptor activo y coincidencia de host/puerto; para esta práctica todos están en `127.0.0.1` |
| Cámara no funciona | Comprueba permisos del navegador o utiliza **Subir imagen** |

## Evidencia para cerrar esta práctica

- [ ] Anotaste versiones de Windows y Python.
- [ ] La configuración y sus pruebas funcionan.
- [ ] La interfaz muestra una imagen y su decisión.
- [ ] Registraste el resultado de la suite completa, incluidos errores si los hay.
- [ ] Sabes abrir dos terminales para probar Modbus.

La validación realizada por el mantenedor hasta esta actualización fue en Linux; esta guía no representa una ejecución ya verificada en un equipo Windows. Registra los resultados del laboratorio con la [plantilla de informe](../plantillas/informe.md).

[Continuar: visión](01-vision.md) · [Índice](../README.md) · [Ayuda general](../SOLUCION_DE_PROBLEMAS.md)
