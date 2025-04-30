import pytest
from modelo.puntaje import Puntaje

class TestPuntaje:
    def test_inicializacion(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])
        assert isinstance(puntaje, Puntaje)
        assert len(puntaje.obtener_puntajes()) == 2

    def test_registrar_puntos(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "1", 5)
        assert puntaje.obtener_puntaje_categoria("Jugador1", "1") == 5
        assert puntaje.obtener_puntaje_total("Jugador1") == 5

    def test_registrar_puntos_jugador_invalido(self):
        puntaje = Puntaje(["Jugador1"])
        with pytest.raises(ValueError, match="Jugador Jugador2 no existe"):
            puntaje.registrar_puntos("Jugador2", "1", 5)

    def test_categoria_repetida(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "1", 5)
        with pytest.raises(ValueError, match="Categoría 1 ya fue utilizada por Jugador1"):
            puntaje.registrar_puntos("Jugador1", "1", 3)

    def test_doble_generala_sin_generala(self):
        puntaje = Puntaje(["Jugador1"])
        with pytest.raises(ValueError, match="Debes marcar Generala antes de marcar Doble Generala"):
            puntaje.registrar_puntos("Jugador1", "Doble Generala", 100)

    def test_categorias_disponibles(self):
        puntaje = Puntaje(["Jugador1"])
        assert len(puntaje.obtener_categorias_disponibles("Jugador1")) == 11
        puntaje.registrar_puntos("Jugador1", "1", 5)
        assert len(puntaje.obtener_categorias_disponibles("Jugador1")) == 10

    def test_determinar_ganador(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])
        puntaje.registrar_puntos("Jugador1", "1", 5)
        puntaje.registrar_puntos("Jugador2", "1", 10)
        assert puntaje.determinar_ganador() == "Jugador2"

    def test_cargar_estado(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])
        estado = {
            "Jugador1": {"1": 5, "2": 10},
            "Jugador2": {"1": 3, "3": 15}
        }
        puntaje.cargar_estado(estado)
        assert puntaje.obtener_puntaje_categoria("Jugador1", "1") == 5
        assert puntaje.obtener_puntaje_total("Jugador2") == 18

