import logging
from collections import defaultdict
import socketio
import uuid
from eventlet import wsgi, sleep
from modelo.jugador import Jugador
from modelo.puntaje import Puntaje

sio = socketio.Server(cors_allowed_origins='*')
salas = defaultdict(lambda: {'creador_sid': None, 'jugadores': [], 'sids': [], 'listo': []})
clientes_con_sala_creada = {}
puntajes_por_sala = {}
tiempo_de_espera_conexion_oponente = 30


@sio.event
def connect(sid, environ):
    logging.info(f"Cliente conectado: {sid}")

@sio.event
def disconnect(sid):
    for sala_id, datos in list(salas.items()):
        if sid in datos['sids']:
            try:
                index = datos['sids'].index(sid)
                nombre = datos['jugadores'][index].obtener_nombre()

                datos['sids'].pop(index)
                datos['jugadores'].pop(index)
                if sid in datos['listo']:
                    datos['listo'].remove(sid)

                if datos['creador_sid'] == sid:
                    datos['creador_sid'] = None

                if sid in clientes_con_sala_creada:
                    del clientes_con_sala_creada[sid]

                if datos['sids']:
                    oponente_sid = datos['sids'][0]
                    sio.emit('jugador_desconectado', {
                        'mensaje': f"Fin del juego: {nombre} ha abandonado la partida."
                    }, room=oponente_sid)

                    del salas[sala_id]
                    if sala_id in puntajes_por_sala:
                        del puntajes_por_sala[sala_id]
                    if oponente_sid in clientes_con_sala_creada:
                        del clientes_con_sala_creada[oponente_sid]

                else:
                    del salas[sala_id]
                    if sala_id in puntajes_por_sala:
                        del puntajes_por_sala[sala_id]

                logging.info(f"{nombre} desconectado y sala {sala_id} limpiada.")

            except Exception as e:
                logging.error(f"Error al limpiar estado en disconnect: {e}")
            break


@sio.event
def crear_sala(sid, data):
    nombre = data.get('nombre', 'Anónimo')

    if sid in clientes_con_sala_creada:
        sala_id = clientes_con_sala_creada[sid]
        if sala_id not in salas:
            del clientes_con_sala_creada[sid]
        else:
            sio.emit('error', {'mensaje': 'Ya tienes una sala creada.'}, room=sid)
            return

    sala_id = f"sala_{uuid.uuid4().hex[:8]}"
    jugador = Jugador(nombre)
    salas[sala_id]['creador_sid'] = sid
    salas[sala_id]['jugadores'].append(jugador)
    salas[sala_id]['sids'].append(sid)
    clientes_con_sala_creada[sid] = sala_id
    sio.enter_room(sid, sala_id)
    sio.emit('sala_creada', {'sala_id': sala_id}, room=sid)
    sio.start_background_task(cerrar_sala_por_inactividad, sala_id)

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
    for sala_id, data in salas.items():
        if data['creador_sid'] != sid and len(data['jugadores']) < 2:
            lista_salas.append({
                "sala_id": sala_id,
                "jugadores": [jug.obtener_nombre() for jug in data["jugadores"]]
            })
    sio.emit('lista_salas', lista_salas, room=sid)


@sio.event
def unirse_a_sala(sid, data):
    sala_id = data.get('sala_id')
    nombre = data.get('nombre', 'Anónimo')

    if sala_id not in salas:
        sio.emit('error', {'mensaje': 'La sala no existe'}, room=sid)
        return

    if len(salas[sala_id]['jugadores']) >= 2:
        sio.emit('error', {'mensaje': 'La sala está llena'}, room=sid)
        return

    jugador = Jugador(nombre)
    salas[sala_id]['jugadores'].append(jugador)
    salas[sala_id]['sids'].append(sid)
    sio.enter_room(sid, sala_id)

    if len(salas[sala_id]['jugadores']) == 2:
        nombres_en_sala = [jug.obtener_nombre() for jug in salas[sala_id]['jugadores']]
        primer_jugador = nombres_en_sala[0]

        puntajes_por_sala[sala_id] = Puntaje(nombres_en_sala)

        sio.emit('iniciar_juego', {
            'sala_id': sala_id,
            'jugadores': nombres_en_sala,
            'primer_jugador': primer_jugador
        }, room=sala_id)

    sio.emit('sala_unida', {'sala_id': sala_id}, room=sid)


@sio.event
def iniciar_juego(sid, data):
    sala_id = data.get('sala_id')
    sio.emit('esperar_inicio', {'sala_id': sala_id}, room=sala_id)


@sio.event
def cliente_listo(sid, data):
    sala_id = data.get('sala_id')
    if sid not in salas[sala_id]['listo']:
        salas[sala_id]['listo'].append(sid)
    if len(salas[sala_id]['jugadores']) == 2 and len(salas[sala_id]['listo']) == 2:
        sio.emit('juego_listo', {'sala_id': sala_id}, room=sala_id)


@sio.event
def lanzar_dados(sid, data):
    sala_id = data.get('sala_id')
    resultados = data.get('resultados')
    tiradas_restantes = data.get('tiradas_restantes')

    jugador_nombre = None
    for i, jugador_sid in enumerate(salas[sala_id]['sids']):
        if sid == jugador_sid:
            jugador_nombre = salas[sala_id]['jugadores'][i].obtener_nombre()
            break

    categorias_disponibles = []
    if jugador_nombre and sala_id in puntajes_por_sala:
        puntaje = puntajes_por_sala[sala_id]
        categorias_disponibles = puntaje.obtener_categorias_disponibles(jugador_nombre)

    sio.emit('resultados_lanzamiento', {
        'jugador_sid': sid,
        'resultados': resultados,
        'tiradas_restantes': tiradas_restantes,
        'categorias_disponibles': categorias_disponibles
    }, room=sala_id)


@sio.event
def actualizar_puntajes(sid, data):
    sala_id = data.get('sala_id')
    puntaje_jugador = data.get('puntaje_jugador')

    if not sala_id or not puntaje_jugador:
        return

    controlador_puntaje = puntajes_por_sala.get(sala_id)
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

    cambiar_turno(sid, sala_id)

@sio.event
def verificar_fin_juego(sid, data):
    sala_id = data.get('sala_id')
    if sala_id not in puntajes_por_sala:
        return

    puntaje_obj = puntajes_por_sala[sala_id]
    if puntaje_obj.juego_finalizado():
        ganador = puntaje_obj.determinar_ganador()
        puntajes = puntaje_obj.obtener_puntajes()
        puntajes_totales = {
            jugador: puntaje_obj.obtener_puntaje_total(jugador)
            for jugador in puntajes
        }
        sio.emit('juego_finalizado', {
            'ganador': ganador,
            'puntajes': puntajes_totales
        }, room=sala_id)


def cambiar_turno(sid, sala_id):
    sala = salas[sala_id]
    try:
        indice_actual = sala['sids'].index(sid)
        indice_siguiente = (indice_actual + 1) % len(sala['sids'])
        siguiente_jugador_sid = sala['sids'][indice_siguiente]
        siguiente_jugador_nombre = sala['jugadores'][indice_siguiente].obtener_nombre()

        sio.emit('cambio_de_turno', {
            'sala_id': sala_id,
            'jugador_actual': siguiente_jugador_sid,
            'jugador_actual_nombre': siguiente_jugador_nombre,
            'es_tu_turno': False
        }, room=sala_id)

    except ValueError:
        logging.error(f"SID {sid} no encontrado en la sala {sala_id} al cambiar turno.")

def cerrar_sala_por_inactividad(sala_id):
    sleep(tiempo_de_espera_conexion_oponente)
    if sala_id in salas and not salas[sala_id]['jugadores'][1:]:
        creador_sid = salas[sala_id]['creador_sid']
        if creador_sid in clientes_con_sala_creada and clientes_con_sala_creada[creador_sid] == sala_id:
            del clientes_con_sala_creada[creador_sid]
        sio.emit('sala_cerrada_inactividad', {'mensaje': 'Sala cerrada, no se unió ningún oponente.'}, room=creador_sid)
        del salas[sala_id]


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
