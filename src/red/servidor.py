from collections import defaultdict
import socketio
from eventlet import wsgi

servidor = socketio.Server()
salas = defaultdict(dict)
nombres_jugadores = {}

@servidor.event
def connect(sid, environ):
    print(f"Cliente conectado: {sid}")
    servidor.emit('servidor_conectado', {"mensaje": "Conectado al servidor"}, room=sid)

#Eventos relacionados con la conexión

@servidor.event
def disconnect(sid):
    nombre = nombres_jugadores.get(sid)
    for sala_id, info in salas.items():
        if sid in info["jugadores"]:
            info["jugadores"].remove(sid)
            if len(info["jugadores"]) == 0:
                del salas[sala_id]
                print(f"Sala {sala_id} eliminada porque no tiene jugadores.")
            else:
                servidor.emit('jugador_desconectado', {"sala_id": sala_id, "jugador": nombre}, room=sala_id)
            break
    if sid in nombres_jugadores:
        del nombres_jugadores[sid]

# Eventos relacionados con las salas
@servidor.event
def crear_sala(sid, data):
    nombre = data.get('nombre')
    if nombre:
        nombres_jugadores[sid] = nombre
    sala_id = f"sala_{len(salas) + 1}"
    salas[sala_id] = {"jugadores": [sid], "estado": "esperando jugadores"}
    servidor.enter_room(sid, sala_id)
    servidor.emit('sala_creada', {"sala_id": sala_id, "mensaje": f"Sala creada. Esperando oponente..."}, room=sid)

@servidor.event
def unirse_a_sala(sid, data):
    sala_id = data.get('sala_id')
    nombre = data.get('nombre')
    if nombre:
        nombres_jugadores[sid] = nombre
    if sala_id in salas and len(salas[sala_id]["jugadores"]) < 2:
        salas[sala_id]["jugadores"].append(sid)
        servidor.enter_room(sid, sala_id)
        # Notificar al jugador que se unió
        servidor.emit('sala_actualizada', {"sala_id": sala_id, "mensaje": f"Te has unido a la sala {sala_id}."}, room=sid)
        # Notificar al jugador que creó la sala
        servidor.emit('sala_actualizada', {"sala_id": sala_id, "mensaje": f"El jugador {nombre} se ha unido a la sala."}, room=salas[sala_id]["jugadores"][0])
        if len(salas[sala_id]["jugadores"]) == 2:
            salas[sala_id]["estado"] = "en partida"
            servidor.emit('partida_iniciada', {"sala_id": sala_id})
    else:
        servidor.emit('error', {"mensaje": "No se pudo unir a la sala"}, room=sid)

@servidor.event
def listar_salas(sid):
    salas_disponibles = {sala_id: info for sala_id, info in salas.items() if len(info["jugadores"]) < 2}
    servidor.emit('salas_disponibles', {"salas": salas_disponibles}, room=sid)

if __name__ == "__main__":
    from socketio import WSGIApp
    import eventlet

    app = WSGIApp(servidor)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)


