class Categoria:
    def __init__(self):
        pass

    def verificar_escalera(self, dados: list) -> bool:
        escalera_baja = [1, 2, 3, 4, 5]
        escalera_alta = [2, 3, 4, 5, 6]
        return sorted(dados) == escalera_baja or sorted(dados) == escalera_alta

    def calcular_puntos_categoria_numerica(self, dados: list, numero: int) -> int:
        return dados.count(numero) * numero

    def calcular_puntos_categoria_especial(self, dados: list, categoria: str, ha_marcado_generala: bool = False) -> int:
        conteos = {numero: dados.count(numero) for numero in range(1, 7)}
        valores = sorted(conteos.values(), reverse=True)

        if categoria == "Escalera":
            return 20 if self.verificar_escalera(dados) else 0
        elif categoria == "Full":
            return 30 if 3 in valores and 2 in valores else 0
        elif categoria == "Póker":
            return 40 if 4 in valores else 0
        elif categoria == "Generala":
            return 50 if 5 in valores else 0
        elif categoria == "Doble Generala":
            if 5 in valores and ha_marcado_generala:
                return 100
            else:
                return 0  # Asignar 0 si no ha marcado Generala previamente
        else:
            raise ValueError(f"Categoría desconocida: {categoria}")

    def calcular_puntos(self, dados: list, categoria: str, ha_marcado_generala: bool = False) -> int:
        if categoria.isdigit():
            return self.calcular_puntos_categoria_numerica(dados, int(categoria))
        else:
            return self.calcular_puntos_categoria_especial(dados, categoria, ha_marcado_generala)