# Clase Fase 00 — Entorno y repositorio

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede explicar por qué se separa la configuración del código, crear y usar un entorno virtual de Python, instalar un paquete propio en modo editable, y leer un mensaje de error de validación para corregir un archivo de configuración.

## Conceptos

- **Entorno virtual**: una copia aislada del intérprete de Python con sus propias dependencias, para que un proyecto no choque con las librerías de otro (ni con las del sistema operativo).
- **Gestión de dependencias**: `requirements.txt` declara qué versiones necesita el proyecto; `pip install -e .` instala el paquete propio en modo editable (los cambios en `src/` se reflejan sin reinstalar).
- **Control de versiones**: `git init`, commits pequeños y descriptivos, y una etiqueta (`git tag fase-NN`) por cada fase cerrada.
- **Configuración externa vs. valores mágicos**: umbrales, rutas y reglas de negocio viven en `config/*.yaml` y `config/*.csv`, no dentro del código Python (ver `CLAUDE.md`).
- **Validación con mensajes claros**: cada error de configuración debe decir *qué* está mal y *dónde*, en español, para que se pueda corregir sin leer el código fuente.

## Demostración paso a paso

```bash
cd placas-plc
git init && git add -A && git commit -m "Agrega estructura base del proyecto"

python3 -m venv .venv
unset PYTHONPATH   # solo si el sistema tiene otro entorno (p. ej. ROS) cargado globalmente
source .venv/bin/activate
pip install pyyaml numpy opencv-python pillow pytest
pip install -e .

pytest tests/test_configuracion.py -v
python -m placas.configuracion
```

Mostrar en vivo qué pasa si se edita `config/reglas.yaml` con un día mal escrito (por ejemplo `lunfardo` en vez de `lunes`) y se vuelve a correr `python -m placas.configuracion`: debe fallar con un `ErrorConfiguracion` que nombra el valor inválido.

## Preguntas de verificación

1. **¿Por qué el umbral de confianza del OCR vive en `reglas.yaml` y no en el código Python?**
   Respuesta: para que se pueda cambiar sin tocar ni reinstalar el código, y para evitar "valores mágicos" dispersos en varios archivos. Cualquiera (docente o estudiante) ajusta el comportamiento editando un archivo de texto.

2. **¿Qué diferencia hay entre el entorno virtual del proyecto y el intérprete global del sistema?**
   Respuesta: el entorno virtual aísla las versiones de las librerías de este proyecto; instalar o desinstalar algo ahí no afecta otros proyectos ni herramientas del sistema (por ejemplo, un entorno con ROS instalado globalmente).

3. **Si `cargar_reglas` recibe un YAML con `restricciones: {lunfardo: [1, 2]}`, ¿qué pasa y por qué es una buena práctica?**
   Respuesta: se lanza `ErrorConfiguracion` con un mensaje que incluye la palabra `lunfardo` y la lista de días válidos. Es buena práctica porque el error aparece inmediatamente al cargar la configuración, con un mensaje entendible, en vez de fallar más adelante (o silenciosamente) en medio de la lógica de decisión.

## Reto para estudiantes

Agregar una regla nueva en `config/reglas.yaml`: restringir el dígito `5` los sábados (hoy sin restricción).

**Criterios de evaluación:**
- El cambio se hace solo en `config/reglas.yaml`, sin tocar `configuracion.py`.
- `python -m placas.configuracion` muestra la nueva restricción del sábado.
- `pytest` sigue pasando sin modificar las pruebas existentes.
