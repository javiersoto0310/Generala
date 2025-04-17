from typing import Optional
from modelo.jugador import Jugador

class Puntaje:

    categorias_ordenadas = [
        "Doble Generala", "Generala", "Póker", "Full", "Escalera", "6", "5", "4", "3", "2", "1"
    ]

    def __init__(self, nombres_jugadores: list, cliente):
        self.__jugadores = [Jugador(nombre) for nombre in nombres_jugadores]
        self.__puntajes_por_categoria = {jugador.obtener_nombre(): {} for jugador in self.__jugadores}
        self.__categorias_usadas = {jugador.obtener_nombre(): set() for jugador in self.__jugadores}
        self.cliente = cliente

    def registrar_puntos(self, nombre_jugador: str, puntos: int, categoria: str):
        jugador = self._obtener_jugador_por_nombre(nombre_jugador)

        if categoria not in self.__categorias_usadas[nombre_jugador]:
            if categoria == "Doble Generala" and "Generala" not in self.__categorias_usadas[nombre_jugador]:
                if puntos != 0:
                    raise ValueError("Debes marcar Generala antes de marcar Doble Generala")
            self.__categorias_usadas[nombre_jugador].add(categoria)
            jugador.actualizar_puntaje(puntos)
            self.__puntajes_por_categoria[nombre_jugador][categoria] = puntos
            self.cliente.emit('actualizar_puntajes', {'puntajes': self.obtener_puntajes()})
        else:
            raise ValueError(f"Categoría {categoria} ya utilizada por {nombre_jugador}")

    def obtener_puntaje_jugador(self, nombre_jugador: str) -> int:
        jugador = self._obtener_jugador_por_nombre(nombre_jugador)
        return jugador.obtener_puntaje()

    def obtener_categorias_usadas(self, nombre_jugador: str) -> set:
        return self.__categorias_usadas.get(nombre_jugador, set())

    def obtener_puntaje_categoria(self, nombre_jugador: str, categoria: str) -> int:
        return self.__puntajes_por_categoria[nombre_jugador].get(categoria, 0)

    def determinar_ganador(self) -> str:
        return max(self.__jugadores, key=lambda jugador: jugador.obtener_puntaje()).obtener_nombre()

    def encontrar_primer_categoria_no_completada(self, nombre_jugador: str) -> Optional[str]:
        for categoria in self.categorias_ordenadas:
            if categoria not in self.__categorias_usadas[nombre_jugador]:
                return categoria
        return None

    def _obtener_jugador_por_nombre(self, nombre: str) -> Jugador:
        for jugador in self.__jugadores:
            if jugador.obtener_nombre() == nombre:
                return jugador
        raise ValueError(f"Jugador {nombre} no existe")

    def cargar_desde_dict(self, datos):
        self.__puntajes_por_categoria = datos
        self.__jugadores = []
        self.__categorias_usadas = {}
        for nombre_jugador, puntajes_categoria in datos.items():
            self.__jugadores.append(Jugador(nombre_jugador, sum(puntajes_categoria.values())))
            self.__categorias_usadas[nombre_jugador] = set(puntajes_categoria.keys())

    def obtener_puntajes(self):
        return self.__puntajes_por_categoria