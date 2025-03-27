import socketio

cliente = socketio.Client()

@cliente.event
def connect():
    print("Conectado al servidor")
    print("¿Quieres crear una sala (C) o unirte a una existente (U)?")
    opcion = input("Elige una opción: ").strip().lower()
    if opcion == 'c':
        cliente.emit('crear_sala')
    elif opcion == 'u':
        cliente.emit('listar_salas')
    else:
        print("Opción no válida. Desconectando...")
        cliente.disconnect()

@cliente.event
def disconnect():
    print("Desconectado del servidor")

@cliente.event
def servidor_conectado(data):
    print(data['mensaje'])

@cliente.event
def sala_creada(data):
    print(f"Sala creada: {data['sala_id']}")

@cliente.event
def sala_actualizada(data):
    print(f"Sala actualizada: {data}")

@cliente.event
def partida_iniciada(data):
    print(f"Partida iniciada en la sala: {data['sala_id']}")

@cliente.event
def salas_disponibles(data):
    if not data['salas']:
        print("No hay salas disponibles. Puedes crear una.")
        return
    print("Salas disponibles:")
    for sala_id, info in data['salas'].items():
        print(f"- {sala_id}: {len(info['jugadores'])} jugadores")
    sala_id = input("Ingresa el ID de la sala a la que quieres unirte: ").strip()
    cliente.emit('unirse_a_sala', {'sala_id': sala_id})

@cliente.event
def error(data):
    print(f"Error: {data['mensaje']}")
    if "No se pudo unir a la sala" in data['mensaje']:
        print("Intenta listar salas nuevamente o crear una nueva sala.")

try:
    cliente.connect('http://localhost:5000')
    cliente.wait()  # Espera eventos de manera pasiva
except Exception as e:
    print(f"Error al conectar: {e}")