from typing import Dict, List
from modelos.modelo_juego.jugador import Jugador
import logging

logging.basicConfig(level=logging.INFO)

class Puntaje:
    categorias_ordenadas = [
        "1", "2", "3", "4", "5", "6",
        "Escalera", "Full", "Póker", "Generala", "Doble Generala"
    ]

    def __init__(self, nombres_jugadores: List[str]):
        self._jugadores = {nombre: Jugador(nombre) for nombre in nombres_jugadores}
        self._puntajes = {nombre: {} for nombre in nombres_jugadores}
        self._categorias_usadas = {nombre: set() for nombre in nombres_jugadores}


    def __validar_registro_puntos(self, nombre_jugador: str, categoria: str) -> None:
        if nombre_jugador not in self._jugadores:
            raise ValueError(f"Jugador {nombre_jugador} no existe")
        if categoria in self._categorias_usadas[nombre_jugador]:
            raise ValueError(f"Categoría {categoria} ya fue utilizada por {nombre_jugador}")

    def registrar_puntos(self, nombre_jugador: str, categoria: str, puntos: int) -> None:
        self.__validar_registro_puntos(nombre_jugador, categoria)

        if categoria == "Doble Generala" and "Generala" not in self._categorias_usadas[nombre_jugador]:
            puntos = 0

        self._puntajes[nombre_jugador][categoria] = puntos
        self._categorias_usadas[nombre_jugador].add(categoria)
        self._jugadores[nombre_jugador].actualizar_puntaje(puntos)

    def obtener_puntajes(self) -> Dict[str, Dict[str, int]]:
        return self._puntajes.copy()

    def obtener_puntaje_total(self, nombre_jugador: str) -> int:
        return self._jugadores[nombre_jugador].obtener_puntaje()

    def ha_usado_categoria(self, nombre_jugador: str, categoria: str) -> bool:
        return categoria in self._categorias_usadas[nombre_jugador]

    def obtener_categorias_disponibles(self, nombre_jugador: str) -> List[str]:
        return [categoria for categoria in self.categorias_ordenadas if not self.ha_usado_categoria(nombre_jugador, categoria)]

    def determinar_ganador_o_empate(self) -> tuple:
        jugadores = list(self._jugadores.values())
        if not jugadores:
            return None, False

        max_puntaje = max(j.obtener_puntaje() for j in jugadores)
        ganadores = [jugador for jugador in jugadores if jugador.obtener_puntaje() == max_puntaje]

        if len(ganadores) > 1:
            return None, True
        else:
            return ganadores[0].obtener_nombre(), False

    def juego_finalizado(self) -> bool:
        return all(len(categorias_usadas_por_jugador) == len(self.categorias_ordenadas)
                   for categorias_usadas_por_jugador in self._categorias_usadas.values())


