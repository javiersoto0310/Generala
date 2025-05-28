from modelo.sala import Sala
from modelo.jugador import Jugador


def test_crear_sala():
    jugador = Jugador("Ana")
    sala = Sala("sala1", "sid_ana", jugador)

    assert sala.sala_id == "sala1"
    assert len(sala.jugadores) == 1
    assert sala.jugadores[0].obtener_nombre() == "Ana"


def test_agregar_y_eliminar_jugador():
    jugador1 = Jugador("Carlos")
    sala = Sala("sala1", "sid_carlos", jugador1)

    jugador2 = Jugador("Luisa")
    sala.agregar_jugador("sid_luisa", jugador2)

    assert len(sala.jugadores) == 2
    assert sala.jugadores[1].obtener_nombre() == "Luisa"

    sala.eliminar_jugador("sid_luisa")
    assert len(sala.jugadores) == 1
    assert sala.jugadores[0].obtener_nombre() == "Carlos"


def test_obtener_oponente():
    jugador1 = Jugador("Pedro")
    jugador2 = Jugador("Maria")
    sala = Sala("sala1", "sid_pedro", jugador1)
    sala.agregar_jugador("sid_maria", jugador2)

    oponente = sala.obtener_oponente_sid("sid_pedro")
    assert oponente == "sid_maria"

    oponente = sala.obtener_oponente_sid("sid_maria")
    assert oponente == "sid_pedro"


def test_sala_llena_y_vacia():
    jugador = Jugador("Solo")
    sala = Sala("sala1", "sid_solo", jugador)

    assert sala.esta_llena() == False
    assert sala.esta_vacia() == False

    jugador2 = Jugador("Oponente")
    sala.agregar_jugador("sid_oponente", jugador2)

    assert sala.esta_llena() == True

    sala.eliminar_jugador("sid_solo")
    sala.eliminar_jugador("sid_oponente")

    assert sala.esta_vacia() == True


def test_nombres_jugadores():
    sala = Sala("sala1", "sid1", Jugador("Juan"))
    sala.agregar_jugador("sid2", Jugador("Laura"))

    nombres = sala.nombres_de_jugadores()
    assert "Juan" in nombres
    assert "Laura" in nombres
    assert len(nombres) == 2