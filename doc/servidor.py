import asyncio
import json
import multiprocessing
from multiprocessing import Queue, Process
import argparse
import time
import socket
import os
import sqlite3


# Cola compartida entre procesos
cola_pedidos = Queue()

# Inicializar base de datos SQLite
DB_PATH = "db/pedidos.db"

def inicializar_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            productos TEXT,
            direccion TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
def guardar_en_db(pedido):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pedidos (cliente, productos, direccion, timestamp) VALUES (?, ?, ?, datetime('now'))",
        (
            pedido.get("cliente", "desconocido"),
            ", ".join(pedido.get("productos", [])),
            pedido.get("direccion", "")
        )
    )
    conn.commit()
    conn.close()

# --- Proceso dedicado para manejar la base de datos ---
def proceso_db(cola_db):
    inicializar_db()  # Asegúrate de que la base de datos esté inicializada
    while True:
        pedido = cola_db.get()
        if pedido is None:  # Señal para terminar el proceso
            break
        guardar_en_db(pedido)

# --- Worker que procesa pedidos ---
def worker(cola_pedidos, cola_db):
    while True:
        pedido = cola_pedidos.get()
        if pedido is None:  # Señal para terminar el worker
            break
        print(f"[WORKER] Procesando pedido: {pedido}")
        time.sleep(2)  # Simula el procesamiento del pedido
        cola_db.put(pedido)  # Envía el pedido a la cola de la base de datos
        print(f"[WORKER] Pedido enviado a la base de datos: {pedido}")

# --- Función para manejar clientes ---
async def manejar_cliente(reader, writer):
    try:
        # Enviar mensaje de bienvenida
        writer.write('Bienvenido al Servidor de Pedidos\nPor favor envíe un JSON válido del tipo \n'
                     '{"cliente": "nombre",'
                     '"productos": ["productos"],'
                     '"direccion": "direccion"}\n'
                     .encode("utf-8"))
        await writer.drain()

        # Leer datos del cliente
        data = await reader.read(1024)
        pedido = data.decode()
        print(f"[SERVER] Pedido recibido: {pedido}")

        # Pedido en formato JSON
        try:
            pedido_data = json.loads(pedido)
            cola_pedidos.put(pedido_data)
            writer.write("Pedido recibido y encolado\n".encode("utf-8"))
        except json.JSONDecodeError:
            writer.write("Error: El mensaje no es un JSON válido.\n".encode("utf-8"))

        await writer.drain()
    except Exception as e:
        print(f"[SERVER] Error manejando cliente: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# --- Servidor dual-stack (IPv4 + IPv6) ---
async def iniciar_servidor_dualstack(host, port):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)  # Dual-stack habilitado
    sock.bind((host, port))
    sock.listen(100)
    sock.setblocking(False)

    server = await asyncio.start_server(manejar_cliente, sock=sock)
    print(f"[SERVER] Escuchando en modo dual-stack en {host}:{port}")
    async with server:
        await server.serve_forever()

# --- Main principal ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="::")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    # Crear colas
    cola_db = Queue()  # Cola para la base de datos
    cola_pedidos = Queue()  # Cola para los pedidos

    # Crear proceso para la base de datos
    proceso_base_datos = Process(target=proceso_db, args=(cola_db,))
    proceso_base_datos.start()

    # Crear procesos worker
    procesos = []
    for _ in range(args.workers):
        p = Process(target=worker, args=(cola_pedidos, cola_db))
        p.start()
        procesos.append(p)

    try:
        asyncio.run(iniciar_servidor_dualstack(args.host, args.port))
    except KeyboardInterrupt:
        print("\n[SERVER] Cerrando servidor...")
    finally:
        # Finalizar workers
        for _ in procesos:
            cola_pedidos.put(None)
        for p in procesos:
            p.join()

        # Finalizar proceso de base de datos
        cola_db.put(None)
        proceso_base_datos.join()

        print("[SERVER] Servidor finalizado.")

if __name__ == "__main__":
    main()
