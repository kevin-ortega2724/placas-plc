# Placas-PLC: de la imagen a la señal

Proyecto didáctico de la asignatura **Automatización Industrial**, Programa de Ingeniería Eléctrica, Universidad Tecnológica de Pereira.

Un sistema de visión en Python lee placas de vehículos. Unas reglas de acceso (pico y placa, autorizados, reportados) deciden si el vehículo entra, y la decisión se convierte en señales digitales y registros que recibe un PLC programado en ladder. Un tercer programa solo lee las salidas del PLC, como lo haría un operador.

```
Cámara / imágenes ──► Visión (Python) ──► Reglas ──► Señales ──Modbus TCP──► PLC (ladder) ──► HMI (solo lectura)
```

## Cómo trabajar con este repositorio

1. Haga un *fork* del repositorio y clónelo.
2. Cree un entorno virtual e instale dependencias:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Cada fase del curso tiene una etiqueta (`fase-01`, `fase-02`, ...). Para empezar desde una fase:
   ```bash
   git checkout -b mi-trabajo fase-03
   ```
4. Lea el enunciado en [`ENUNCIADO.md`](ENUNCIADO.md) y la ruta en [`docs/ROADMAP.md`](docs/ROADMAP.md).
5. Entregue su trabajo con un *pull request* a su propio fork o como indique el docente.

## Estructura

| Carpeta | Contenido |
|---|---|
| `config/` | Reglas de pico y placa, lista de autorizados y reportados |
| `data/crudas/` | Imágenes reales tomadas por el grupo (no se suben a GitHub) |
| `data/sinteticas/` | Placas generadas por software para pruebas (no se suben a GitHub, se regeneran con `python -m placas.generador`) |
| `src/placas/` | Módulos del sistema de visión, reglas y señales |
| `app/` | Interfaz gráfica |
| `plc/` | Proyectos de OpenPLC y CODESYS (ladder) |
| `hmi/` | Monitor que solo lee salidas del PLC |
| `tests/` | Pruebas automáticas |
| `notebooks/` | Cuadernos de exploración por fase |
| `salidas/` | Imágenes intermedias y reportes generados (no se suben) |

## Privacidad

Las placas son datos personales asociados a un vehículo. Use placas sintéticas o fotos de vehículos propios con autorización. No suba imágenes reales al repositorio: la carpeta `data/crudas/` está en `.gitignore`.
