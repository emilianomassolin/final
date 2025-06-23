import asyncio
import json
import multiprocessing
from multiprocessing import Queue, Process, Lock
import argparse
import time
import socket
import os
import sqlite3
from datetime import datetime

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

# --- Worker que procesa pedidos y guarda directamente en SQLite ---
def worker(cola_pedidos, db_lock):
    pid = os.getpid()
    while True:
        pedido = cola_pedidos.get()
        if pedido is None:
            print(f"[WORKER {pid}] Finalizando.")
            break
        t = datetime.now().strftime('%H:%M:%S')
        print(f"[WORKER {pid}] Procesando {pedido} a las {t}")
        time.sleep(5)  # Simula procesamiento

        with db_lock:
            guardar_en_db(pedido)
            marcar_como_listo(pedido)
        print(f"[WORKER {pid}] Pedido procesado y guardado.")

# --- Servidor con sockets IPv4 e IPv6 separados ---
async def iniciar_servidores_ipv4_ipv6(host_ipv6, host_ipv4, port, cola_pedidos):
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

    # Socket IPv6
    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    sock6.bind((host_ipv6, port))
    sock6.listen(100)
    sock6.setblocking(False)

    # Socket IPv4
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

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="::")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    inicializar_db()

    cola_pedidos = Queue()
    db_lock = Lock()  # 🔐 Lock para sincronizar acceso a SQLite

    procesos = []
    for _ in range(args.workers):
        p = Process(target=worker, args=(cola_pedidos, db_lock))
        p.start()
        procesos.append(p)

    try:
        asyncio.run(iniciar_servidores_ipv4_ipv6("::1", "127.0.0.1", args.port, cola_pedidos))
    except KeyboardInterrupt:
        print("\n[SERVER] Cerrando servidor...")
    finally:
        for _ in procesos:
            cola_pedidos.put(None)
        for p in procesos:
            p.join()

        print("[SERVER] Servidor finalizado.")

if __name__ == "__main__":
    main()
