from collections import defaultdict
import socketio
from eventlet import wsgi
from modelo.jugador import Jugador

sio = socketio.Server(cors_allowed_origins='*')
salas = defaultdict(dict)


@sio.event
def connect(sid, environ):
    print(f"\nCliente conectado: {sid}\n")

@sio.event
def crear_sala(sid, data):
    nombre = data.get('nombre', 'Anónimo')
    sala_id = f"sala_{len(salas) + 1}"
    jugador = Jugador(nombre)
    salas[sala_id] = {'jugadores': [jugador], 'sids': [sid], 'listo': []}
    sio.enter_room(sid, sala_id)
    print(f"\nSala creada: {sala_id}, Jugador: {nombre}\n")
    sio.emit('sala_creada', {'sala_id': sala_id}, room=sid)


@sio.event
def listar_salas(sid):
    lista_salas = [
        {"sala_id": sala_id, "jugadores": [jug.obtener_nombre() for jug in data["jugadores"]]}
        for sala_id, data in salas.items()
        if len(data["jugadores"]) < 2
    ]
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
    if 'sids' not in salas[sala_id]:
        salas[sala_id]['sids'] = [salas[sala_id]['jugadores'][0].__dict__.get('_Jugador__nombre') == salas[sala_id]['jugadores'][0].obtener_nombre()]
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
    print(f"\nEl jugador {sid} en la sala {sala_id} ha lanzado los dados: {resultados}\n")
    sio.emit('resultados_lanzamiento', {'jugador_sid': sid, 'resultados': resultados}, room=sala_id)

@sio.event
def disconnect(sid):
    print(f"Cliente desconectado: {sid}")
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

    print("\nServidor iniciado en http://127.0.0.1:5000\n")
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)