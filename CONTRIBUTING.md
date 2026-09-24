# Cómo trabajar y entregar prácticas

## Flujo del estudiante

1. Crea un fork en GitHub y clónalo.
2. Sigue la instalación del README.
3. Crea una rama para tu ejercicio:

```bash
git switch -c practica/fase-03-equipo
```

4. Lee la clase y tutorial correspondientes. Registra un ensayo base antes de modificar.
5. Cambia una sola responsabilidad y añade pruebas si alteras comportamiento.
6. Ejecuta las pruebas del módulo; antes de entregar ejecuta `python -m pytest -q`.
7. Copia `docs/plantillas/informe.md` a `docs/entregas/tu-equipo.md` y completa evidencia.
8. Revisa `git status` y `git diff`. Agrega explícitamente los archivos del ejercicio, crea un commit descriptivo en español y sube tu rama.
9. Abre un pull request a tu fork o al destino indicado por el docente. Explica problema, cambio, pruebas y limitaciones.

## Convenciones

Consulta [CLAUDE.md](CLAUDE.md): identificadores en español sin tildes, funciones pequeñas, anotaciones de tipos y configuración externa. Conserva la separación entre visión, reglas, comunicación e interfaz.

## Qué no incluir

No subas entornos virtuales, cachés, imágenes reales ni salidas con datos personales. Usa ejemplos sintéticos. No cambies etiquetas históricas para entregar un ejercicio.

## Cómo proponer un tutorial

Incluye objetivo, prerrequisitos, comandos desde la raíz, resultado esperado, comprobación, reto y enlaces de navegación. Prueba los comandos y distingue simulación, comunicación y PLC real.
