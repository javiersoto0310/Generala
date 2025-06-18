import logging
from uuid import uuid4
from eventlet import wsgi, sleep
import socketio

from modelos.modelo_juego.jugador import Jugador
from modelos.modelo_juego.puntaje import Puntaje
from modelos.modelo_sala.sala import Sala

logging.basicConfig(level=logging.INFO)

sio = socketio.Server(cors_allowed_origins='*')
salas = {}
clientes_con_sala_creada = {}
clientes = {}

@sio.event
def connect(sid, environ):
    nombre = "Desconocido"
    clientes[sid] = nombre
    logging.info(f"Cliente conectado: {sid} - Nombre: {nombre}")

@sio.event
def disconnect(sid):
    nombre = clientes.get(sid, "Desconocido")
    logging.info(f"Cliente desconectado: {sid} ({nombre})")
    clientes.pop(sid, None)

    for sala_id, sala in list(salas.items()):
        if sid in sala.sids:
            try:
                jugador = sala.obtener_jugador_por_sid(sid)
                nombre = jugador.obtener_nombre() if jugador else "Jugador"

                sala.eliminar_jugador_por_sid(sid)

                if sala.creador_sid == sid:
                    sala.creador_sid = None

                if sid in clientes_con_sala_creada:
                    del clientes_con_sala_creada[sid]

                if sala.esta_vacia():
                    del salas[sala_id]
                else:
                    oponente_sid = sala.obtener_oponente_sid(sid)
                    if oponente_sid:
                        sio.emit('jugador_desconectado', {
                            'mensaje': f"Fin del juego: {nombre} ha abandonado la partida."
                        }, room=oponente_sid)

                        sala.temporizador.detener()

                        if sala.creador_sid and sala.creador_sid in clientes_con_sala_creada:
                            del clientes_con_sala_creada[sala.creador_sid]

                        if oponente_sid in clientes_con_sala_creada:
                            del clientes_con_sala_creada[oponente_sid]

                        del salas[sala_id]

                logging.info(f"{nombre} desconectado y sala {sala_id} limpiada.")

            except Exception as e:
                logging.error(f"Error al limpiar estado en disconnect: {e}")
            break

@sio.event
def crear_sala(sid, data):
    nombre = data.get('nombre', 'Anónimo')
    clientes[sid] = nombre
    logging.info(f"Cliente {sid} asignado como {nombre}")

    if sid in clientes_con_sala_creada:
        sala_id = clientes_con_sala_creada[sid]
        if sala_id not in salas:
            del clientes_con_sala_creada[sid]
        else:
            sio.emit('error', {'mensaje': 'Ya tienes una sala creada.'}, room=sid)
            return

    sala_id = f"sala_{uuid4().hex[:8]}"
    jugador = Jugador(nombre)
    nueva_sala = Sala(sala_id, sid, jugador)
    salas[sala_id] = nueva_sala
    clientes_con_sala_creada[sid] = sala_id

    sio.enter_room(sid, sala_id)
    sio.emit('sala_creada', {'sala_id': sala_id}, room=sid)

    sio.start_background_task(cerrar_sala_por_inactividad, sala_id)

    logging.info(f"Estado actual - Salas: {salas}")
    logging.info(f"Clientes con sala creada: {clientes_con_sala_creada}")
    logging.info(f"Clientes conectados: {clientes}")

@sio.event
def listar_salas(sid):
    if sid in clientes_con_sala_creada:
        sala_id = clientes_con_sala_creada[sid]
        if sala_id not in salas:
            del clientes_con_sala_creada[sid]
        else:
            sio.emit('ya_tiene_sala', {'mensaje': 'Ya tienes una sala creada, debes esperar a que se un oponente...'}, room=sid)
            return

    lista_salas = []
    for sala_id, sala in salas.items():
        if sala.creador_sid != sid and not sala.esta_llena():
            lista_salas.append({
                "sala_id": sala_id,
                "jugadores": sala.nombres_de_jugadores()
            })
    sio.emit('lista_salas', lista_salas, room=sid)

    #logging.info(f"Estado actual - Salas: {salas}")
    #logging.info(f"Clientes con sala creada: {clientes_con_sala_creada}")
    #logging.info(f"Clientes conectados: {clientes}")


@sio.event
def unirse_a_sala(sid, data):
    sala_id = data.get('sala_id')
    nombre = data.get('nombre', 'Anónimo')
    clientes[sid] = nombre
    logging.info(f"Cliente {sid} asignado como {nombre}")

    if sala_id not in salas:
        sio.emit('error', {'mensaje': 'La sala no existe'}, room=sid)
        return

    sala = salas[sala_id]

    if sala.esta_llena():
        sio.emit('error', {'mensaje': 'La sala está llena'}, room=sid)
        return

    jugador = Jugador(nombre)
    sala.agregar_jugador_y_sid(sid, jugador)
    sio.enter_room(sid, sala_id)

    if sala.esta_llena():
        nombres_en_sala = sala.nombres_de_jugadores()
        primer_jugador = nombres_en_sala[0]

        sala.puntaje = Puntaje(nombres_en_sala)
        sala.jugador_actual = primer_jugador

        sio.emit('iniciar_juego', {
            'sala_id': sala_id,
            'jugadores': nombres_en_sala,
            'primer_jugador': primer_jugador
        }, room=sala_id)

        sala.temporizador.iniciar(sio)

    sio.emit('sala_unida', {'sala_id': sala_id}, room=sid)

    #logging.info(f"Estado actual - Salas: {salas}")
    #logging.info(f"Clientes con sala creada: {clientes_con_sala_creada}")
    #logging.info(f"Clientes conectados: {clientes}")


@sio.event
def abandonar_sala_por_abandono_o_juego_finalizado(sid, data):
    sala_id = data.get("sala_id")
    if not sala_id or sala_id not in salas:
        return

    sala = salas[sala_id]
    sala.eliminar_jugador_por_sid(sid)

    if sala.creador_sid == sid:
        sala.creador_sid = None

    if sid in clientes_con_sala_creada:
        del clientes_con_sala_creada[sid]

    oponente_sid = sala.obtener_oponente_sid(sid)
    if oponente_sid and oponente_sid in clientes_con_sala_creada:
        del clientes_con_sala_creada[oponente_sid]

    if sala.esta_vacia():
        del salas[sala_id]

    logging.info(f"Jugador abandonó/finalizó la sala {sala_id}.")

@sio.event
def lanzar_dados(sid, data):
    sala_id = data.get('sala_id')
    resultados = data.get('resultados')
    tiradas_restantes = data.get('tiradas_restantes')

    if sala_id not in salas:
        return

    sala = salas[sala_id]
    jugador = sala.obtener_jugador_por_sid(sid)
    jugador_nombre = jugador.obtener_nombre() if jugador else None

    categorias_disponibles = []
    if jugador_nombre and sala.puntaje:
        categorias_disponibles = sala.puntaje.obtener_categorias_disponibles(jugador_nombre)

    sio.emit('resultados_lanzamiento', {
        'jugador_sid': jugador_nombre,
        'resultados': resultados,
        'tiradas_restantes': tiradas_restantes,
        'categorias_disponibles': categorias_disponibles
    }, room=sala_id)


@sio.event
def actualizar_puntajes(sid, data):
    sala_id = data.get('sala_id')
    puntaje_jugador = data.get('puntaje_jugador')

    if not sala_id or not puntaje_jugador or sala_id not in salas:
        return

    sala = salas[sala_id]
    controlador_puntaje = sala.puntaje

    if not controlador_puntaje:
        return

    for nombre, categorias in puntaje_jugador.items():
        for categoria, puntos in categorias.items():
            try:
                controlador_puntaje.registrar_puntos(nombre, categoria, puntos)
            except ValueError as e:
                logging.warning(f"Registro inválido de puntaje: {e}")
                return

    sio.emit('limpiar_interfaz', {'sala_id': sala_id}, room=sala_id)
    sio.emit('actualizar_puntajes', {
        'sala_id': sala_id,
        'puntajes': controlador_puntaje.obtener_puntajes()
    }, room=sala_id)

    sala.cambiar_turno(sio)


@sio.event
def verificar_fin_juego(sid, data):
    sala_id = data.get('sala_id')
    if sala_id not in salas:
        return

    sala = salas[sala_id]
    controlador_puntaje = sala.puntaje

    if controlador_puntaje and controlador_puntaje.juego_finalizado():
        ganador, es_empate = controlador_puntaje.determinar_ganador_o_empate()
        puntajes = controlador_puntaje.obtener_puntajes()
        puntajes_totales = {
            jugador: controlador_puntaje.obtener_puntaje_total(jugador)
            for jugador in puntajes
        }

        if es_empate:
            max_puntos = max(puntajes_totales.values())
            motivo = f"¡Partida empatada con {max_puntos} puntos!\n\nResultado final:\n"
            for jugador, puntos in puntajes_totales.items():
                motivo += f"{jugador}: {puntos} puntos\n"
        else:
            motivo = f"¡Ganador: {ganador}!\n\nResultado final:\n"
            for jugador, puntos in puntajes_totales.items():
                motivo += f"{jugador}: {puntos} puntos\n"

        sio.emit('juego_finalizado', {
            'ganador': ganador,
            'puntajes': puntajes_totales,
            'motivo': motivo
        }, room=sala_id)
        sala.temporizador.detener()

def cerrar_sala_por_inactividad(sala_id):
    sleep(30)
    if sala_id in salas:
        sala = salas[sala_id]
        if not sala.esta_llena():
            creador_sid = sala.creador_sid
            if creador_sid in clientes_con_sala_creada:
                del clientes_con_sala_creada[creador_sid]
            sio.emit('sala_cerrada_inactividad', {'mensaje': 'Sala cerrada, no se unió ningún oponente.'}, room=creador_sid)
            del salas[sala_id]


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)

