from src.modelo.tiempo import Tiempo

def test_tiempo_inicial_por_defecto():
    tiempo = Tiempo()
    assert tiempo.obtener_tiempo_restante() == 45

def test_disminuir_tiempo():
    tiempo = Tiempo(10)
    tiempo.disminuir_tiempo()
    assert tiempo.obtener_tiempo_restante() == 9

def test_disminuir_tiempo_a_cero():
    tiempo = Tiempo(1)
    tiempo.disminuir_tiempo()
    assert tiempo.obtener_tiempo_restante() == 0, "El tiempo restante debe llegar a 0 correctamente"
    tiempo.disminuir_tiempo()
    assert tiempo.obtener_tiempo_restante() == 0, "El tiempo no debe ser negativo"

def test_reiniciar_tiempo_por_defecto():
    tiempo = Tiempo(10)
    tiempo.reiniciar_tiempo()
    assert tiempo.obtener_tiempo_restante() == 45, "El tiempo debe reiniciarse al valor por defecto (45)"

def test_tiempo_agotado():
    tiempo = Tiempo(0)
    assert tiempo.tiempo_agotado()
