from src.modelo.turno import Turno

def test_obtener_turno_jugador_actual():
    turno = Turno("Javier")
    assert turno.obtener_jugador_actual() == "Javier"

def test_disminuir_tiradas_restantes():
    turno = Turno("Javier")
    assert turno.obtener_tiradas_restantes() == 3
    turno.disminuir_tiradas_restantes()
    assert turno.obtener_tiradas_restantes() == 2
    turno.disminuir_tiradas_restantes()
    assert turno.obtener_tiradas_restantes() == 1

def test_reiniciar_tiradas_restantes():
    turno = Turno("Javier")
    turno.disminuir_tiradas_restantes()
    turno.reiniciar_tiradas_restantes()
    assert turno.obtener_tiradas_restantes() == 3

def test_reiniciar_turno():
    turno = Turno("Javier")
    turno.disminuir_tiradas_restantes()
    turno.reiniciar_turno("María")
    assert turno.obtener_jugador_actual() == "María"
    assert turno.obtener_tiradas_restantes() == 3
