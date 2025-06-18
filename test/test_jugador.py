from modelos.modelo_juego.jugador import Jugador

def test_obtener_nombre():
    jugador = Jugador("Javier")
    assert jugador.obtener_nombre() == "Javier", "El nombre del jugador no coincide con el esperado"

def test_obtener_puntaje_inicial():
    jugador = Jugador("Javier")
    assert jugador.obtener_puntaje() == 0, "El puntaje inicial del jugador debería ser 0"

def test_actualizar_puntaje():
    jugador = Jugador("Javier")
    jugador.actualizar_puntaje(10)
    jugador.actualizar_puntaje(5)
    assert jugador.obtener_puntaje() == 15, "El puntaje acumulativo debería ser 15"
