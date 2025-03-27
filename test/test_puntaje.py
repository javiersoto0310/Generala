from src.modelo.puntaje import Puntaje

def test_registrar_puntos():
    puntaje = Puntaje(["Javier"])
    puntaje.registrar_puntos("Javier", 50, "Generala")
    assert puntaje.obtener_puntaje_jugador("Javier") == 50

def test_determinar_ganador():
    puntaje = Puntaje(["Javier", "María"])
    puntaje.registrar_puntos("Javier", 50, "Generala")
    puntaje.registrar_puntos("María", 30, "Escalera")
    assert puntaje.determinar_ganador() == "Javier", "El ganador no es el correcto"







