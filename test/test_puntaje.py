from src.modelo.puntaje import Puntaje
from modelo.jugador import Jugador
import pytest

class DummyCliente:
    def emit(self, evento, data):
        pass

def test_registrar_puntos():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Javier"], cliente_dummy)
    puntaje.registrar_puntos("Javier", 50, "Generala")
    assert puntaje.obtener_puntaje_jugador("Javier") == 50
    assert puntaje.obtener_puntaje_categoria("Javier", "Generala") == 50
    assert "Generala" in puntaje.obtener_categorias_usadas("Javier")

def test_registrar_puntos_categoria_ya_usada():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Javier"], cliente_dummy)
    puntaje.registrar_puntos("Javier", 25, "Escalera")
    with pytest.raises(ValueError, match="Categoría Escalera ya utilizada por Javier"):
        puntaje.registrar_puntos("Javier", 30, "Escalera")

def test_registrar_doble_generala_sin_generala():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Javier"], cliente_dummy)
    with pytest.raises(ValueError, match="Debes marcar Generala antes de marcar Doble Generala"):
        puntaje.registrar_puntos("Javier", 50, "Doble Generala")

def test_registrar_doble_generala_con_generala():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Javier"], cliente_dummy)
    puntaje.registrar_puntos("Javier", 50, "Generala")
    puntaje.registrar_puntos("Javier", 100, "Doble Generala")
    assert puntaje.obtener_puntaje_jugador("Javier") == 150
    assert puntaje.obtener_puntaje_categoria("Javier", "Generala") == 50
    assert puntaje.obtener_puntaje_categoria("Javier", "Doble Generala") == 100
    assert "Generala" in puntaje.obtener_categorias_usadas("Javier")
    assert "Doble Generala" in puntaje.obtener_categorias_usadas("Javier")

def test_obtener_puntaje_jugador():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["María"], cliente_dummy)
    puntaje.registrar_puntos("María", 30, "Póker")
    assert puntaje.obtener_puntaje_jugador("María") == 30

def test_obtener_categorias_usadas():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Carlos"], cliente_dummy)
    puntaje.registrar_puntos("Carlos", 15, "3")
    assert puntaje.obtener_categorias_usadas("Carlos") == {"3"}

def test_obtener_puntaje_categoria():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Elena"], cliente_dummy)
    puntaje.registrar_puntos("Elena", 40, "Full")
    assert puntaje.obtener_puntaje_categoria("Elena", "Full") == 40
    assert puntaje.obtener_puntaje_categoria("Elena", "Escalera") == 0

def test_determinar_ganador():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Javier", "María"], cliente_dummy)
    puntaje.registrar_puntos("Javier", 50, "Generala")
    puntaje.registrar_puntos("María", 30, "Escalera")
    assert puntaje.determinar_ganador() == "Javier"


def test_obtener_jugador_por_nombre_existe():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Ricardo"], cliente_dummy)
    jugador = puntaje._obtener_jugador_por_nombre("Ricardo")
    assert isinstance(jugador, Jugador)
    assert jugador.obtener_nombre() == "Ricardo"

def test_obtener_jugador_por_nombre_no_existe():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Ricardo"], cliente_dummy)
    with pytest.raises(ValueError, match="Jugador Luis no existe"):
        puntaje._obtener_jugador_por_nombre("Luis")


def test_obtener_puntajes():
    cliente_dummy = DummyCliente()
    puntaje = Puntaje(["Inés", "Martín"], cliente_dummy)
    puntaje.registrar_puntos("Inés", 20, "2")
    puntaje.registrar_puntos("Martín", 40, "4")
    expected_puntajes = {"Inés": {"2": 20}, "Martín": {"4": 40}}
    assert puntaje.obtener_puntajes() == expected_puntajes







