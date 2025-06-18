import pytest
from unittest.mock import Mock
from modelos.modelo_juego.temporizador import Temporizador

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
    temporizador = Temporizador(sala_simulada, tiempo_inicial=45)
    assert temporizador.sala == sala_simulada
    assert temporizador.obtener_tiempo_turno() == 45
    assert temporizador.obtener_tiempo_restante() == 45
    assert not temporizador._temporizador_en_marcha
    assert temporizador._proceso_temporizador is None
    assert temporizador.obtener_id_temporizador() is None

def test_iniciar_poner_el_reloj_en_marcha_y_genera_id(sala_simulada, sio_simulado):
    tiempo_inicial_para_test = 10
    temporizador = Temporizador(sala_simulada, tiempo_inicial=tiempo_inicial_para_test)
    original_id = temporizador.obtener_id_temporizador()

    temporizador.iniciar(sio_simulado)

    assert temporizador._temporizador_en_marcha
    assert temporizador.obtener_tiempo_restante() == tiempo_inicial_para_test
    assert temporizador.obtener_id_temporizador() is not None
    assert temporizador.obtener_id_temporizador() != original_id
    sio_simulado.start_background_task.assert_called_once()
    assert callable(temporizador._proceso_temporizador)

def test_detener_apaga_el_reloj(sala_simulada, sio_simulado):
    temporizador = Temporizador(sala_simulada, tiempo_inicial=7)
    temporizador.iniciar(sio_simulado)

    temporizador.detener()

    assert not temporizador._temporizador_en_marcha
    assert temporizador._proceso_temporizador is None
    assert temporizador.obtener_id_temporizador() is None

def test_reiniciar_el_temporizador(sala_simulada, sio_simulado):
    tiempo_inicial = 15
    temporizador = Temporizador(sala_simulada, tiempo_inicial=tiempo_inicial)

    temporizador.iniciar(sio_simulado)
    primer_id = temporizador.obtener_id_temporizador()
    primer_proceso = temporizador._proceso_temporizador

    temporizador.iniciar(sio_simulado)

    assert temporizador._temporizador_en_marcha
    assert temporizador.obtener_tiempo_restante() == tiempo_inicial
    assert temporizador.obtener_id_temporizador() is not None
    assert temporizador.obtener_id_temporizador() != primer_id
    assert temporizador._proceso_temporizador is not None
    assert temporizador._proceso_temporizador != primer_proceso
    assert sio_simulado.start_background_task.call_count == 2
