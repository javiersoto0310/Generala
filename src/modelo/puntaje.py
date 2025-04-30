from typing import Optional, Dict, List
from modelo.jugador import Jugador
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
        self.cliente = None

    def set_cliente(self, cliente):
        self.cliente = cliente

    def registrar_puntos(self, nombre_jugador: str, categoria: str, puntos: int) -> None:
        if nombre_jugador not in self._jugadores:
            raise ValueError(f"Jugador {nombre_jugador} no existe")

        if categoria in self._categorias_usadas[nombre_jugador]:
            raise ValueError(f"Categoría {categoria} ya fue utilizada por {nombre_jugador}")

        if categoria == "Doble Generala" and "Generala" not in self._categorias_usadas[nombre_jugador]:
            raise ValueError("Debes marcar Generala antes de marcar Doble Generala")

        self._puntajes[nombre_jugador][categoria] = puntos
        self._categorias_usadas[nombre_jugador].add(categoria)
        self._jugadores[nombre_jugador].actualizar_puntaje(puntos)

        logging.info(f"Puntos registrados - Jugador: {nombre_jugador}, Categoría: {categoria}, Puntos: {puntos}")

    def obtener_puntaje_total(self, nombre_jugador: str) -> int:
        return self._jugadores[nombre_jugador].obtener_puntaje()

    def obtener_puntaje_categoria(self, nombre_jugador: str, categoria: str) -> Optional[int]:
        return self._puntajes[nombre_jugador].get(categoria)

    def ha_usado_categoria(self, nombre_jugador: str, categoria: str) -> bool:
        return categoria in self._categorias_usadas[nombre_jugador]

    def obtener_categorias_disponibles(self, nombre_jugador: str) -> List[str]:
        return [cat for cat in self.categorias_ordenadas if cat not in self._categorias_usadas[nombre_jugador]]

    def obtener_primer_categoria_disponible(self, nombre_jugador: str) -> Optional[str]:
        for categoria in self.categorias_ordenadas:
            if not self.ha_usado_categoria(nombre_jugador, categoria):
                return categoria
        return None

    def determinar_ganador(self) -> str:
        return max(self._jugadores.values(), key=lambda j: j.obtener_puntaje()).obtener_nombre()

    def obtener_puntajes(self) -> Dict[str, Dict[str, int]]:
        return self._puntajes.copy()

    def cargar_estado(self, estado: Dict[str, Dict[str, int]]) -> None:
        self._puntajes = estado
        self._categorias_usadas = {
            jugador: set(puntajes.keys())
            for jugador, puntajes in estado.items()
        }

        for nombre, jugador in self._jugadores.items():
            jugador.actualizar_puntaje(-jugador.obtener_puntaje())  # Resetear
            for puntos in estado[nombre].values():
                jugador.actualizar_puntaje(puntos)