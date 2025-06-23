import asyncio
import json
import multiprocessing
from multiprocessing import Queue, Process
import argparse
import time
import socket
import os
import sqlite3
from datetime import datetime




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
            timestamp TEXT,
                   estado TEXT 
        )
    ''')
    conn.commit()
    conn.close()
def guardar_en_db(pedido):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pedidos (cliente, productos, direccion, timestamp, estado) VALUES (?, ?, ?, datetime('now'),?)",
            (
                pedido.get("cliente", "desconocido"),
                ", ".join(pedido.get("productos", [])),
                pedido.get("direccion", ""),
                "en proceso"
            )
        )
        conn.commit()
        print(f"[DB] Pedido guardado con estado en proceso: {pedido}")
    except Exception as e:
        print(f"[DB] Error al guardar el pedido: {e}")
    finally:
        conn.close()

# --- Proceso dedicado para manejar la base de datos ---
def proceso_db(cola_db):
    inicializar_db()  # Asegúrate de que la base de datos esté inicializada
    while True:
        pedido = cola_db.get()
        if pedido is None:  # Señal para terminar el proceso
            break
        print(f"[DB] Guardando pedido en la base de datos: {pedido}")
        guardar_en_db(pedido)

# --- Worker que procesa pedidos ---
def worker(cola_pedidos, cola_db):
    pid=os.getpid()
    while True:
        pedido = cola_pedidos.get()
        if pedido is None:  # Señal para terminar el worker
            print(f"[WORKER {pid}] Finalizando.")
            break
        t = datetime.now().strftime('%H:%M:%S')
        print(f"[WORKER {pid}] Procesando {pedido} a las {t}")
        time.sleep(2)  # Simula el procesamiento del pedido
        marcar_como_listo(pedido)
        print(f"[WORKER] Pedido enviado a la base de datos: {pedido}")

async def iniciar_servidores_ipv4_ipv6(host_ipv6, host_ipv4, port, cola_pedidos, cola_db):
    async def manejar_cliente(reader, writer):
        try:
            writer.write('Bienvenido al Servidor de Pedidos\nPor favor envíe un JSON válido del tipo \n'
                         '{"cliente": "nombre","productos": ["producto1", "producto2"],"direccion": "direccion"}\n'.encode("utf-8"))
            await writer.drain()

            data = await reader.read(1024)
            pedido = data.decode()
            print(f"[SERVER] Pedido recibido: {pedido}")

            try:
                pedido_data = json.loads(pedido)
                cola_db.put(pedido_data)
                cola_pedidos.put(pedido_data)
                print(f"[SERVER] Pedido encolado: {pedido_data}")
                writer.write("Pedido encolado\n".encode("utf-8"))
            except json.JSONDecodeError:
                writer.write("JSON inválido\n".encode("utf-8"))

            await writer.drain()
        except Exception as e:
            print(f"[SERVER] Error manejando cliente: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    # Socket IPv6 puro
    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)  # IPv6 only
    sock6.bind((host_ipv6, port))
    sock6.listen(100)
    sock6.setblocking(False)

    # Socket IPv4 puro
    sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock4.bind((host_ipv4, port))
    sock4.listen(100)
    sock4.setblocking(False)

    server_ipv6 = await asyncio.start_server(manejar_cliente, sock=sock6)
    server_ipv4 = await asyncio.start_server(manejar_cliente, sock=sock4)

    print(f"[SERVER] Escuchando en IPv6 {host_ipv6}:{port}")
    print(f"[SERVER] Escuchando en IPv4 {host_ipv4}:{port}")

    async with server_ipv6, server_ipv4:
        await asyncio.gather(
            server_ipv6.serve_forever(),
            server_ipv4.serve_forever()
        )

# --- Funciones para marcar pedidos como listos ---
def marcar_como_listo(pedido):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE pedidos
            SET estado = 'listo',
                timestamp = datetime('now')
            WHERE cliente = ? AND direccion = ? AND productos = ?
            ''',
            (
                pedido.get("cliente", "desconocido"),
                pedido.get("direccion", ""),
                ", ".join(pedido.get("productos", []))
            )
)
        conn.commit()
        print(f"[DB] Pedido marcado como 'listo': {pedido}")
    except Exception as e:
        print(f"[DB] Error al marcar como listo: {e}")
    finally:
        conn.close()

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
        asyncio.run(iniciar_servidores_ipv4_ipv6("::1", "127.0.0.1", args.port, cola_pedidos, cola_db))
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
