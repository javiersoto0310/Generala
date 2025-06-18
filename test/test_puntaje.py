from modelos.modelo_juego.puntaje import Puntaje

class TestPuntaje:
    def test_inicializacion(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])
        assert isinstance(puntaje, Puntaje)
        assert len(puntaje.obtener_puntajes()) == 2

    def test_registrar_puntos(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "1", 5)
        assert puntaje.obtener_puntajes()["Jugador1"]["1"] == 5
        assert puntaje.obtener_puntaje_total("Jugador1") == 5


    def test_marcar_doble_generala_sin_tener_generala_el_valor_del_puntaje_debe_ser_0_puntos(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "Doble Generala", 100)

        assert puntaje.obtener_puntajes()["Jugador1"]["Doble Generala"] == 0
        assert puntaje.obtener_puntaje_total("Jugador1") == 0
        assert "Doble Generala" in puntaje._categorias_usadas["Jugador1"]

    def test_marcar_doble_generala_con_generala_el_valor_del_puntaje_debe_ser_100_puntos(self):
        puntaje = Puntaje(["Jugador1"])

        puntaje.registrar_puntos("Jugador1", "Generala", 50)
        puntaje.registrar_puntos("Jugador1", "Doble Generala", 100)

        assert puntaje.obtener_puntajes()["Jugador1"]["Generala"] == 50
        assert puntaje.obtener_puntajes()["Jugador1"]["Doble Generala"] == 100
        assert puntaje.obtener_puntaje_total("Jugador1") == 150

    def test_marcar_generala_normal(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "Generala", 50)

        assert puntaje.obtener_puntajes()["Jugador1"]["Generala"] == 50
        assert puntaje.obtener_puntaje_total("Jugador1") == 50
        assert "Generala" in puntaje._categorias_usadas["Jugador1"]

    def test_categorias_disponibles(self):
        puntaje = Puntaje(["Jugador1"])
        assert len(puntaje.obtener_categorias_disponibles("Jugador1")) == 11
        puntaje.registrar_puntos("Jugador1", "1", 5)
        assert len(puntaje.obtener_categorias_disponibles("Jugador1")) == 10

    def test_verificar_resultado_final_del_juego_determinar_ganador(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])
        puntaje.registrar_puntos("Jugador1", "6", 12)
        puntaje.registrar_puntos("Jugador2", "6", 18)
        assert puntaje.determinar_ganador_o_empate() == ("Jugador2", False)

    def test_determinar_empate(self):
        puntaje = Puntaje(["Jugador1", "Jugador2"])

        puntaje.registrar_puntos("Jugador1", "6", 12)
        puntaje.registrar_puntos("Jugador2", "6", 12)

        resultado = puntaje.determinar_ganador_o_empate()

        assert resultado == (None, True)

    def test_registrar_puntos_poker(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "Póker", 40)
        assert puntaje.obtener_puntajes()["Jugador1"]["Póker"] == 40
        assert puntaje.obtener_puntaje_total("Jugador1") == 40

    def test_registrar_puntos_full(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "Full", 30)
        assert puntaje.obtener_puntajes()["Jugador1"]["Full"] == 30
        assert puntaje.obtener_puntaje_total("Jugador1") == 30

    def test_registrar_puntos_escalera(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "Escalera", 20)
        assert puntaje.obtener_puntajes()["Jugador1"]["Escalera"] == 20
        assert puntaje.obtener_puntaje_total("Jugador1") == 20

    def test_registrar_puntos_categoria_numerica(self):
        puntaje = Puntaje(["Jugador1"])
        puntaje.registrar_puntos("Jugador1", "2", 4)
        assert puntaje.obtener_puntajes()["Jugador1"]["2"] == 4
        assert puntaje.obtener_puntaje_total("Jugador1") == 4
