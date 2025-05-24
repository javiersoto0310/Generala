import logging
from collections import defaultdict

import socketio
import uuid
from uuid import uuid4
from eventlet import wsgi, sleep
from modelo.jugador import Jugador
from modelo.puntaje import Puntaje

sio = socketio.Server(cors_allowed_origins='*')
salas = defaultdict(lambda: {
    'creador_sid': None,
    'jugadores': [],
    'sids': [],
    'listo': [],
    'tarea_temporizador': None,
    'segundos_restantes': 30
})
clientes_con_sala_creada = {}
puntajes_por_sala = {}
tiempo_de_espera_conexion_oponente = 30
tiempo_turno = 30


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

                    detener_temporizador(sala_id)
                    del salas[sala_id]
                    if sala_id in puntajes_por_sala:
                        del puntajes_por_sala[sala_id]
                    if oponente_sid in clientes_con_sala_creada:
                        del clientes_con_sala_creada[oponente_sid]
                else:
                    detener_temporizador(sala_id)
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
        iniciar_temporizador(sala_id)

    sio.emit('sala_unida', {'sala_id': sala_id}, room=sid)

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
        'jugador_sid': jugador_nombre,
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

    controlador_puntaje = puntajes_por_sala[sala_id]
    if controlador_puntaje.juego_finalizado():
        ganador = controlador_puntaje.determinar_ganador()
        puntajes = controlador_puntaje.obtener_puntajes()
        puntajes_totales = {
            jugador: controlador_puntaje.obtener_puntaje_total(jugador)
            for jugador in puntajes
        }
        sio.emit('juego_finalizado', {
            'ganador': ganador,
            'puntajes': puntajes_totales
        }, room=sala_id)


def cambiar_turno(sid, sala_id):
    sala = salas[sala_id]
    try:
        if salas[sala_id].get('tarea_temporizador'):
            detener_temporizador(sala_id)

        indice_actual = sala['sids'].index(sid)
        indice_siguiente = (indice_actual + 1) % len(sala['sids'])
        siguiente_jugador_sid = sala['sids'][indice_siguiente]
        siguiente_jugador_nombre = sala['jugadores'][indice_siguiente].obtener_nombre()

        salas[sala_id]['jugador_actual'] = siguiente_jugador_nombre

        sio.emit('cambio_de_turno', {
            'sala_id': sala_id,
            'jugador_actual': siguiente_jugador_sid,
            'jugador_actual_nombre': siguiente_jugador_nombre,
            'es_tu_turno': False
        }, room=sala_id)

        sio.emit('limpiar_interfaz', {'sala_id': sala_id}, room=sala_id)

        iniciar_temporizador(sala_id)

    except ValueError as e:
        logging.error(f"Error en cambiar_turno: {e}")


def cerrar_sala_por_inactividad(sala_id):
    sleep(tiempo_de_espera_conexion_oponente)
    if sala_id in salas and not salas[sala_id]['jugadores'][1:]:
        creador_sid = salas[sala_id]['creador_sid']
        if creador_sid in clientes_con_sala_creada and clientes_con_sala_creada[creador_sid] == sala_id:
            del clientes_con_sala_creada[creador_sid]
        sio.emit('sala_cerrada_inactividad', {'mensaje': 'Sala cerrada, no se unió ningún oponente.'}, room=creador_sid)
        del salas[sala_id]


def iniciar_temporizador(sala_id):
    if sala_id not in salas:
        return

    detener_temporizador(sala_id)

    salas[sala_id]['segundos_restantes'] = tiempo_turno
    salas[sala_id]['temporizador_activo'] = True

    temp_id = uuid4().hex
    salas[sala_id]['temporizador_id'] = temp_id

    def cuenta_regresiva(temp_id):
        try:
            while (
                salas[sala_id]['segundos_restantes'] > 0 and
                salas[sala_id].get('temporizador_activo', False) and
                salas[sala_id].get('temporizador_id') == temp_id
            ):
                sleep(1)
                salas[sala_id]['segundos_restantes'] -= 1
                sio.emit('cronometro_actualizado', {
                    'sala_id': sala_id,
                    'tiempo_restante': salas[sala_id]['segundos_restantes']
                }, room=sala_id)

            if (
                salas[sala_id].get('temporizador_activo', False) and
                salas[sala_id].get('temporizador_id') == temp_id
            ):
                manejar_tiempo_agotado(sala_id)

        except Exception as e:
            logging.error(f"Error en cuenta_regresiva: {e}")
            detener_temporizador(sala_id)

    salas[sala_id]['tarea_temporizador'] = sio.start_background_task(
        cuenta_regresiva,
        temp_id
    )

def manejar_tiempo_agotado(sala_id):
    sio.emit('turno_agotado', {'sala_id': sala_id}, room=sala_id)

    if sala_id in salas:
        jugador_actual_idx = next((i for i, jugador in enumerate(salas[sala_id]['jugadores'])
                                   if jugador.obtener_nombre() == salas[sala_id]['jugador_actual']), None)

        if jugador_actual_idx is not None:
            cambiar_turno(salas[sala_id]['sids'][jugador_actual_idx], sala_id)


def detener_temporizador(sala_id):
    if sala_id in salas:
        salas[sala_id]['temporizador_activo'] = False
        salas[sala_id]['tarea_temporizador'] = None
        salas[sala_id]['temporizador_id'] = None


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)