import pytest
from unittest.mock import Mock, patch
from modelo.temporizador import Temporizador


@pytest.fixture
def sala_simulada():
    sala = Mock()
    sala.sala_id = "sala_de_prueba"
    sala.manejar_tiempo_agotado = Mock()
    return sala

@pytest.fixture
def sio_simulado():
    sio = Mock()
    sio.emit = Mock()
    sio.start_background_task = Mock(side_effect=lambda func, *args, **kwargs: func)
    return sio


def test_el_temporizador_empieza_correctamente(sala_simulada):
    temporizador = Temporizador(sala_simulada, tiempo_turno=45)
    assert temporizador.sala == sala_simulada
    assert temporizador.tiempo_turno == 45
    assert temporizador.segundos_restantes == 45
    assert not temporizador.activo
    assert temporizador.tarea is None
    assert temporizador.id is None


def test_iniciar_poner_el_reloj_en_marcha_y_genera_id(sala_simulada, sio_simulado):
    tiempo_inicial_para_test = 10
    temporizador = Temporizador(sala_simulada, tiempo_turno=tiempo_inicial_para_test)
    original_id = temporizador.id

    temporizador.iniciar(sio_simulado)

    assert temporizador.activo
    assert temporizador.segundos_restantes == tiempo_inicial_para_test
    assert temporizador.id is not None
    assert temporizador.id != original_id
    sio_simulado.start_background_task.assert_called_once()
    assert callable(temporizador.tarea)


def test_detener_apaga_el_reloj(sala_simulada, sio_simulado):
    temporizador = Temporizador(sala_simulada, tiempo_turno=7)
    temporizador.iniciar(sio_simulado)

    temporizador.detener()

    assert not temporizador.activo
    assert temporizador.tarea is None
    assert temporizador.id is None


@patch('eventlet.sleep', return_value=None)
def test_la_cuenta_regresiva_envia_actualizaciones_y_maneja_el_tiempo_agotado(
        mock_sleep_simulado, sala_simulada, sio_simulado):
    tiempo_de_prueba = 3

    temporizador = Temporizador(sala_simulada, tiempo_turno=tiempo_de_prueba)
    temporizador.iniciar(sio_simulado)

    temporizador.tarea(temporizador.id)

    assert sio_simulado.emit.call_count == tiempo_de_prueba
    sio_simulado.emit.assert_called_with('cronometro_actualizado', {
        'sala_id': sala_simulada.sala_id,
        'tiempo_restante': 0
    }, room=sala_simulada.sala_id)

    sala_simulada.manejar_tiempo_agotado.assert_called_once_with(sio_simulado)


@patch('eventlet.sleep', return_value=None)
def test_la_cuenta_regresiva_se_detiene_al_apagar_el_reloj(mock_sleep_simulado, sala_simulada, sio_simulado):
    tiempo_inicial_para_test = 10
    temporizador = Temporizador(sala_simulada, tiempo_turno=tiempo_inicial_para_test)
    temporizador.iniciar(sio_simulado)

    if temporizador.activo and temporizador.segundos_restantes > 0:
        temporizador.segundos_restantes -= 1
        sio_simulado.emit('cronometro_actualizado', {
            'sala_id': sala_simulada.sala_id,
            'tiempo_restante': temporizador.segundos_restantes
        }, room=sala_simulada.sala_id)

    temporizador.detener()

    sala_simulada.manejar_tiempo_agotado.assert_not_called()

    assert sio_simulado.emit.call_count == 1
    assert sio_simulado.emit.call_args[0][1]['tiempo_restante'] == tiempo_inicial_para_test - 1