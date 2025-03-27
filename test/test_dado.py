from src.modelo.dado import Dado

def test_lanzar_dado():
    dado = Dado()
    valor = dado.lanzar()
    assert 1 <= valor <= 6

def test_obtener_valor_despues_de_lanzar():
    dado = Dado()
    valor_lanzado = dado.lanzar()
    valor_obtenido = dado.obtener_valor()
    assert valor_lanzado == valor_obtenido

def test_reiniciar_dado():
    dado = Dado()
    dado.lanzar()
    dado.reiniciar()
    assert dado.obtener_valor() is None

