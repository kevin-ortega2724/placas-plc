"""Pruebas del PLC simulado (Fase 08): temporizadores, contadores y watchdog.

Se avanza el tiempo pasando dt explicito a ciclo(), nunca con time.sleep,
para que las pruebas sean deterministas y rapidas.
"""
from placas.plc_simulado import PlcSimulado
from placas.senales import Senales


def _senales(**overrides) -> Senales:
    base = dict(
        vehiculo_presente=True,
        acceso_permitido=False,
        acceso_denegado=False,
        lectura_dudosa=False,
        nueva_lectura=True,
        codigo_decision=5,
        confianza=950,
        ultimo_digito=3,
        watchdog=1,
    )
    base.update(overrides)
    return Senales(**base)


def test_renglon_1_abre_talanquera_y_cuenta_ingreso():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(acceso_permitido=True))

    plc.ciclo(0.05)

    assert plc.q0_talanquera is True
    assert plc.contador_ingresos == 1


def test_renglon_4_acuse_pone_nueva_lectura_en_falso():
    plc = PlcSimulado()
    senales = _senales(acceso_permitido=True)
    plc.recibir_senales(senales)

    plc.ciclo(0.05)

    assert senales.nueva_lectura is False


def test_talanquera_se_cierra_despues_de_5_segundos():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(acceso_permitido=True))
    plc.ciclo(0.05)
    assert plc.q0_talanquera is True

    plc.ciclo(5.0)

    assert plc.q0_talanquera is False


def test_renglon_2_luz_roja_y_contador_rechazos():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(acceso_denegado=True))

    plc.ciclo(0.05)

    assert plc.q1_luz_roja is True
    assert plc.contador_rechazos == 1

    plc.ciclo(3.0)
    assert plc.q1_luz_roja is False


def test_renglon_3_luz_ambar_persiste_hasta_validacion_manual():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(lectura_dudosa=True))

    plc.ciclo(0.05)
    assert plc.q2_luz_ambar is True

    plc.recibir_senales(_senales(lectura_dudosa=False, nueva_lectura=False))
    plc.ciclo(0.05)
    assert plc.q2_luz_ambar is True  # sigue pendiente, no ha llegado el I0

    plc.boton_validacion_manual = True
    plc.ciclo(0.05)

    assert plc.q2_luz_ambar is False
    assert plc.q0_talanquera is True  # el I0 abre la talanquera


def test_renglon_5_watchdog_activa_alarma_tras_3_segundos_sin_cambio():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(watchdog=1))
    plc.ciclo(0.05)
    assert plc.q3_alarma_comunicacion is False

    for _ in range(60):  # 60 x 0.05 s = 3.0 s sin que watchdog cambie
        plc.ciclo(0.05)

    assert plc.q3_alarma_comunicacion is True


def test_watchdog_que_cambia_no_activa_alarma():
    plc = PlcSimulado()
    for valor in range(1, 80):
        plc.recibir_senales(_senales(watchdog=valor))
        plc.ciclo(0.05)

    assert plc.q3_alarma_comunicacion is False


def test_alarma_de_watchdog_fuerza_cierre_de_talanquera():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(acceso_permitido=True, watchdog=1))
    plc.ciclo(0.05)
    assert plc.q0_talanquera is True

    for _ in range(60):
        plc.recibir_senales(_senales(nueva_lectura=False, watchdog=1))
        plc.ciclo(0.05)

    assert plc.q3_alarma_comunicacion is True
    assert plc.q0_talanquera is False


def test_renglon_6_emergencia_bloquea_y_cierra_talanquera():
    plc = PlcSimulado()
    plc.recibir_senales(_senales(acceso_permitido=True))
    plc.ciclo(0.05)
    assert plc.q0_talanquera is True

    plc.boton_emergencia = True
    plc.ciclo(0.05)

    assert plc.q0_talanquera is False
    assert plc.bloqueado is True


def test_bloqueado_por_emergencia_impide_abrir_talanquera_de_nuevo():
    plc = PlcSimulado()
    plc.boton_emergencia = True
    plc.recibir_senales(_senales(acceso_permitido=True))

    plc.ciclo(0.05)

    assert plc.q0_talanquera is False


def test_reiniciar_emergencia_permite_operar_de_nuevo():
    plc = PlcSimulado()
    plc.boton_emergencia = True
    plc.recibir_senales(_senales(acceso_permitido=True))
    plc.ciclo(0.05)
    assert plc.bloqueado is True

    plc.boton_emergencia = False
    plc.reiniciar_emergencia()
    plc.recibir_senales(_senales(acceso_permitido=True))
    plc.ciclo(0.05)

    assert plc.q0_talanquera is True
