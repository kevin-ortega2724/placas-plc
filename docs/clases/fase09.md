# Clase Fase 09 — Interfaz gráfica

Duración estimada: 2 horas.

## Objetivos

Al terminar, el estudiante puede construir una interfaz de operador que solo orquesta módulos ya probados (sin duplicar lógica), y entiende por qué separar la interfaz de la lógica de negocio facilita las pruebas y el mantenimiento.

## Conceptos

- **Interfaz de operador**: una capa delgada que muestra estado y recibe entradas (imagen, fecha/hora simulada), pero no decide nada por sí misma — toda decisión viene de `pipeline`, `reglas` y `senales`, ya probados en fases anteriores.
- **Visualización de estado**: color por decisión (verde/rojo/ámbar/gris), lámparas virtuales para Q0-Q3, y una tabla con los valores exactos que se enviarían por Modbus, para que el operador vea *qué* decidió el sistema y *por qué*.
- **Separación interfaz/lógica**: si `interfaz.py` importa y llama funciones de otros módulos en vez de reimplementarlas, un cambio en las reglas de negocio (Fase 07) se refleja automáticamente en la interfaz sin tocarla.
- **Pruebas de una interfaz Streamlit**: `streamlit.testing.v1.AppTest` ejecuta el script real (sin navegador) y expone sus elementos (`sidebar.checkbox`, `sidebar.radio`, etc.) para simular interacción y comprobar que no lance excepciones.

## Demostración paso a paso

```bash
pytest tests/test_interfaz.py -v

streamlit run app/interfaz.py
# abrir http://localhost:8501, elegir una imagen de data/sinteticas,
# cambiar la fecha/hora simulada y observar como cambia la decision
```

Mostrar en vivo cómo la misma placa autorizada cambia de PERMITIDO a PICO_Y_PLACA con solo mover la fecha/hora simulada de la barra lateral a un lunes 7 a.m. — sin tocar ni una línea de código.

## Preguntas de verificación

1. **¿Por qué la interfaz no debería contener ninguna condición tipo `if decision == "PERMITIDO"` que decida algo de negocio, más allá de elegir un color para mostrar?**
   Respuesta: porque esa decisión ya la tomó `reglas.decidir()`; si la interfaz también decidiera (aunque sea de forma redundante), un cambio futuro en las reglas del Fase 07 podría no reflejarse en la interfaz si alguien olvida actualizar ambos lugares. Duplicar lógica crea una fuente de inconsistencias.

2. **¿Qué gana el proyecto al poder probar la interfaz con `AppTest` en vez de solo probarla manualmente en el navegador?**
   Respuesta: la prueba automática se puede correr en cada cambio (por ejemplo, en CI) y detecta de inmediato si una modificación rompe la interfaz, sin depender de que alguien recuerde abrirla manualmente y probar cada combinación de opciones.

3. **¿Por qué el selector de fecha/hora simulada es más útil en clase que solo poder usar la fecha y hora reales?**
   Respuesta: permite demostrar y probar el comportamiento de pico y placa en cualquier día y hora (un lunes a las 7 a.m., un festivo, un sábado) durante la clase, sin tener que esperar a que ese momento ocurra de verdad.

## Reto para estudiantes

Agregar un panel con escenarios predefinidos (botones como "Lunes 7 a.m.", "Sábado", "Festivo") que llenen automáticamente la fecha y hora simulada, para probar pico y placa sin escribir la fecha a mano cada vez.

**Criterios de evaluación:**
- Los botones solo modifican el valor de fecha/hora en el estado de la sesión de Streamlit (`st.session_state`), sin agregar lógica de decisión nueva.
- Al menos un escenario predefinido corresponde a un día festivo real (verificable con la librería `holidays`).
- La interfaz sigue pasando `pytest tests/test_interfaz.py`.

---

[Fase anterior](fase08.md) · [Índice de guías](../README.md) · [Fase siguiente](fase10.md)
