# Problemas frecuentes

| Síntoma | Qué comprobar | Acción |
|---|---|---|
| `No module named placas` | Entorno activo e instalación editable | `python -m pip install -e .` desde la raíz |
| No encuentra `config/reglas.yaml` | Directorio de ejecución | Entra a `placas-plc` antes de ejecutar |
| Carpeta sin imágenes | Ruta y extensión | Genera datos; el selector de carpeta busca PNG |
| Primera lectura lenta | Preparación de modelos OCR en CPU | Espera la carga; verifica Internet si falta descargar modelos |
| Error de descarga OCR | Conectividad y permisos de caché | Repite con conexión y conserva el mensaje si persiste |
| Error al importar datastore Modbus | Versión instalada | Reinstala `python -m pip install -r requirements.txt`; se requiere pymodbus >=3.6,<3.8 |
| Conexión rechazada | Receptor, host y puerto | Inicia receptor y usa 5020 para el ensayo local |
| Cambios YAML sin efecto | Caché de configuración | Detén y reinicia Streamlit |
| HMI no abre por puerto ocupado | Dos servidores Streamlit | Inícialo con `--server.port 8502` |
| HMI conectado pero contadores en cero | Tipo de receptor y mapa | El servidor de prueba no ejecuta lógica PLC |
| Alarma watchdog con interfaz abierta | Ausencia de emisor continuo | Usa la sesión persistente del tutorial 05 |
| Cámara no disponible | Permisos del navegador | Autoriza cámara en localhost o prueba subir una imagen |
| Aparece `launch_testing`, ROS o falta `lark` al ejecutar pytest | `PYTHONPATH` de ROS contamina el entorno | En Linux usa `env -u PYTHONPATH .venv/bin/python -m pytest -q` |

Para problemas de instalación, lanzador `py`, políticas de PowerShell o rutas en Windows, consulta la [guía específica](tutoriales/00-windows.md).

## Antes de reportar un error

Copia el comando, versión de Python, traceback y pasos mínimos para repetirlo. Indica si usas simulador, servidor de prueba u OpenPLC. Adjunta solo datos sintéticos o autorizados.

[Volver al índice](README.md)
