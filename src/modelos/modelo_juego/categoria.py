class Categoria:
    def __init__(self):
        pass

    def verificar_escalera(self, dados: list) -> bool:
        dados_unicos = sorted(set(dados))
        escalera_baja = [1, 2, 3, 4, 5]
        escalera_alta = [2, 3, 4, 5, 6]
        return dados_unicos == escalera_baja or dados_unicos == escalera_alta

    def calcular_puntos_categoria_numerica(self, dados: list, numero: int) -> int:
        return dados.count(numero) * numero

    def _es_full(self, conteos: dict) -> bool:
        valores = sorted(conteos.values(), reverse=True)
        return 3 in valores and 2 in valores

    def _es_poker(self, conteos: dict) -> bool:
        return 4 in conteos.values()

    def _es_generala(self, conteos: dict) -> bool:
        return 5 in conteos.values()

    def evaluar_puntos_categoria_especial(self, dados: list, categoria: str, ha_marcado_generala: bool = False) -> int:
        conteo_numerico_de_cada_dado = {numero: dados.count(numero) for numero in range(1, 7)}

        if categoria == "Escalera":
            return 20 if self.verificar_escalera(dados) else 0
        elif categoria == "Full":
            return 30 if self._es_full(conteo_numerico_de_cada_dado) else 0
        elif categoria == "Póker":
            return 40 if self._es_poker(conteo_numerico_de_cada_dado) else 0
        elif categoria == "Generala":
            return 50 if self._es_generala(conteo_numerico_de_cada_dado) else 0
        elif categoria == "Doble Generala":
            return 100 if self._es_generala(conteo_numerico_de_cada_dado) and ha_marcado_generala else 0
        else:
            raise ValueError(f"Categoría no válida: {categoria}")

    def determinar_puntuacion_para_una_categoria_especial_o_numerica(self, dados: list, categoria: str, ha_marcado_generala: bool = False) -> int:
        if categoria.isdigit():
            return self.calcular_puntos_categoria_numerica(dados, int(categoria))
        else:
            return self.evaluar_puntos_categoria_especial(dados, categoria, ha_marcado_generala)