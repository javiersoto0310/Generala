import logging
from collections import defaultdict
import socketio
from eventlet import wsgi, sleep
from modelo.jugador import Jugador

sio = socketio.Server(cors_allowed_origins='*')
salas = defaultdict(lambda: {'creador_sid': None, 'jugadores': [], 'sids': [], 'listo': []})
clientes_con_sala_creada = {}
tiempo_de_espera_conexion_oponente = 20


def cerrar_sala_por_inactividad(sala_id):
    sleep(tiempo_de_espera_conexion_oponente)
    if sala_id in salas and not salas[sala_id]['jugadores'][1:]:
        creador_sid = salas[sala_id]['creador_sid']
        if creador_sid in clientes_con_sala_creada and clientes_con_sala_creada[creador_sid] == sala_id:
            del clientes_con_sala_creada[creador_sid]
        logging.info(f"Cerrando sala {sala_id} por inactividad.")
        sio.emit('sala_cerrada_inactividad', {'mensaje': 'Sala cerrada, no se unió ningún oponente.'}, room=creador_sid)
        del salas[sala_id]
    elif sala_id in salas:
        logging.info(f"Sala {sala_id} no cerrada, se unieron otros jugadores.")


@sio.event
def connect(sid, environ):
    print(f"\nCliente conectado: {sid}\n")

@sio.event
def crear_sala(sid, data):
    nombre = data.get('nombre', 'Anónimo')
    if sid in clientes_con_sala_creada:
        sio.emit('error', {'mensaje': 'Ya tienes una sala creada.'}, room=sid)
        return
    sala_id = f"sala_{len(salas) + 1}"
    jugador = Jugador(nombre)
    salas[sala_id]['creador_sid'] = sid
    salas[sala_id]['jugadores'].append(jugador)
    salas[sala_id]['sids'].append(sid)
    clientes_con_sala_creada[sid] = sala_id
    sio.enter_room(sid, sala_id)
    print(f"\nSala creada: {sala_id} por {nombre}\n")
    sio.emit('sala_creada', {'sala_id': sala_id}, room=sid)
    sio.start_background_task(cerrar_sala_por_inactividad, sala_id)


@sio.event
def listar_salas(sid):
    if sid in clientes_con_sala_creada:
        sio.emit('ya_tiene_sala', {'mensaje': 'Ya tienes una sala creada, debes esperar a que se una un oponente...'}, room=sid)
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
    print(f"\nJugador {nombre} unido a la sala {sala_id}")
    print(f"Jugadores en la sala: {[jug.obtener_nombre() for jug in salas[sala_id]['jugadores']]}")

    if len(salas[sala_id]['jugadores']) == 2:
        nombres_en_sala = [jug.obtener_nombre() for jug in salas[sala_id]['jugadores']]
        primer_jugador = nombres_en_sala[0]
        print(f"Emitiendo 'iniciar_juego' para la sala {sala_id} con jugadores: {nombres_en_sala}, primer jugador: {primer_jugador}")
        sio.emit('iniciar_juego', {'sala_id': sala_id, 'jugadores': nombres_en_sala, 'primer_jugador': primer_jugador}, room=sala_id)

    sio.emit('sala_unida', {'sala_id': sala_id}, room=sid)

@sio.event
def iniciar_juego(sid, data):
    sala_id = data.get('sala_id')
    sio.emit('esperar_inicio', {'sala_id': sala_id}, room=sala_id)

@sio.event
def cliente_listo(sid, data):
    sala_id = data.get('sala_id')
    print(f"Cliente {sid} listo en la sala {sala_id}")
    if sid not in salas[sala_id]['listo']:
        salas[sala_id]['listo'].append(sid)
    if len(salas[sala_id]['jugadores']) == 2 and len(salas[sala_id]['listo']) == 2:
        sio.emit('juego_listo', {'sala_id': sala_id}, room=sala_id)

@sio.event
def lanzar_dados(sid, data):
    sala_id = data.get('sala_id')
    resultados = data.get('resultados')
    tiradas_restantes = data.get('tiradas_restantes')

    print(f"\nEl jugador {sid} en la sala {sala_id} ha lanzado los dados: {resultados} (quedan {tiradas_restantes} tiradas)\n")
    sio.emit('resultados_lanzamiento', {
        'jugador_sid': sid,
        'resultados': resultados,
        'tiradas_restantes': tiradas_restantes
    }, room=sala_id)

@sio.event
def disconnect(sid):
    print(f"Cliente desconectado: {sid}")
    if sid in clientes_con_sala_creada:
        sala_id_creada = clientes_con_sala_creada.pop(sid)
        if sala_id_creada in salas:
            print(f"El creador de la sala {sala_id_creada} ({sid}) se desconectó.")
            del salas[sala_id_creada]
            sio.emit('sala_cerrada_inactividad', {'mensaje': 'El creador de la sala se desconectó.'}, room=sala_id_creada)
    for sala_id, data in list(salas.items()):
        if sid in data['sids']:
            print(f"El cliente {sid} se desconectó de la sala {sala_id}")
            data['jugadores'] = [jug for i, jug in enumerate(data['jugadores']) if data['sids'][i] != sid]
            data['sids'].remove(sid)
            data['listo'] = [s for s in data['listo'] if s != sid]
            if not data['jugadores']:
                del salas[sala_id]
                print(f"Sala {sala_id} eliminada por falta de jugadores.")
            else:
                sio.emit('jugador_desconectado', {'sid': sid}, room=sala_id)
            break


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    import eventlet

    print(f"\nServidor iniciado en http://127.0.0.1:5000 (Tiempo de espera para salas: {tiempo_de_espera_conexion_oponente} segundos)\n")
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)