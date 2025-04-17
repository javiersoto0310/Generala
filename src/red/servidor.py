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
    salas[sala_id] = {'jugadores': [jugador], 'sids': [sid]}
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
        print(f"Emitiendo 'iniciar_juego' para la sala {sala_id} con jugadores: {nombres_en_sala}")
        sio.emit('iniciar_juego', {'sala_id': sala_id, 'jugadores': nombres_en_sala}, room=sala_id)

    sio.emit('sala_unida', {'sala_id': sala_id}, room=sid)

@sio.event
def iniciar_juego(sid, data):
    sala_id = data.get('sala_id')
    sio.emit('esperar_inicio', {'sala_id': sala_id}, room=sala_id)

@sio.event
def cliente_listo(sid, data):
    sala_id = data.get('sala_id')
    print(f"Cliente {sid} listo en la sala {sala_id}")
    if len(salas[sala_id]['jugadores']) == 2:
        sio.emit('juego_listo', {'sala_id': sala_id}, room=sala_id)



if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    import eventlet

    print("\nServidor iniciado en http://127.0.0.1:5000\n")
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)