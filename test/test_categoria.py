from modelos.modelo_juego.categoria import Categoria

def test_verificar_escalera_baja():
    categoria = Categoria()
    dados = [1, 2, 3, 4, 5]
    assert categoria.verificar_escalera(dados) == True

def test_verificar_escalera_alta():
    categoria = Categoria()
    dados = [2, 3, 4, 5, 6]
    assert categoria.verificar_escalera(dados) == True

def test_calcular_puntos_categoria_numerica():
    categoria = Categoria()
    dados = [1, 2, 2, 3, 2]
    puntos = categoria.calcular_puntos_categoria_numerica(dados, 2)
    assert puntos == 6

def test_verificar_escalera():
    categoria = Categoria()
    dados = [1, 2, 3, 4, 5]
    puntos = categoria.evaluar_puntos_categoria_especial(dados, "Escalera")
    assert puntos == 20

def test_verificar_convinacion_de_dados_full():
    categoria = Categoria()
    dados = [2, 2, 3, 3, 3]
    puntos = categoria.evaluar_puntos_categoria_especial(dados, "Full")
    assert puntos == 30

def test_verificar_convinacion_de_dados_poker():
    categoria = Categoria()
    dados = [4, 4, 4, 4, 5]
    puntos = categoria.evaluar_puntos_categoria_especial(dados, "Póker")
    assert puntos == 40

def test_verificar_generala():
    categoria = Categoria()
    dados = [6, 6, 6, 6, 6]
    puntos = categoria.evaluar_puntos_categoria_especial(dados, "Generala")
    assert puntos == 50

def test_verificar_doble_generala():
    categoria = Categoria()
    dados = [5, 5, 5, 5, 5]
    puntos = categoria.evaluar_puntos_categoria_especial(dados, "Doble Generala", ha_marcado_generala=True)
    assert puntos == 100


