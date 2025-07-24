import asyncio
import json
from multiprocessing import Queue, Process, Lock, Semaphore
import argparse
from dotenv import load_dotenv
import time
import socket
import os
import sqlite3
from datetime import datetime

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "db/pedidos.db")
MAX_PEDIDOS_EN_COLA = int(os.getenv("MAX_PEDIDOS_EN_COLA", "5"))

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
            fecha_inicio TEXT,
            fecha_fin TEXT,
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
            "INSERT INTO pedidos (cliente, productos, direccion, fecha_inicio, estado) VALUES (?, ?, ?, datetime('now'), ?)",
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
                fecha_fin = datetime('now')
            WHERE cliente = ? AND direccion = ? AND productos = ?
            ''',
            (
                pedido.get("cliente", "desconocido"),
                pedido.get("direccion", ""),
                ", ".join(pedido.get("productos", []))
            )
        )
        if cursor.rowcount == 0:
            print(f"[DB] ⚠️ No se encontró el pedido para marcar como 'listo': {pedido}")
        else:
            print(f"[DB] Pedido marcado como 'listo': {pedido}")
        conn.commit()
    except Exception as e:
        print(f"[DB] Error al marcar como listo: {e}")
    finally:
        conn.close()

def worker(cola_pedidos, db_lock, semaforo):
    pid = os.getpid()
    while True:
        pedido = cola_pedidos.get()
        if pedido is None:
            print(f"[WORKER {pid}] Finalizando.")
            break

        t = datetime.now().strftime('%H:%M:%S')
        print(f"[WORKER {pid}] Procesando {pedido} a las {t}")
        with db_lock:
            guardar_en_db(pedido)
        time.sleep(2)
        with db_lock:
            marcar_como_listo(pedido)
        print(f"[WORKER {pid}] Pedido procesado y guardado.")
        semaforo.release()

def mostrar_estadisticas():
    print("\n=== Estadísticas de Procesamiento ===")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cliente, fecha_inicio, fecha_fin,
                   ROUND((JULIANDAY(fecha_fin) - JULIANDAY(fecha_inicio)) * 86400, 2) AS duracion_segundos
            FROM pedidos
            ORDER BY fecha_inicio
        ''')
        filas = cursor.fetchall()
        for cliente, inicio, fin, duracion in filas:
            print(f"🧾 {cliente} | Inicio: {inicio} | Fin: {fin} | Duración: {duracion} s")
    except Exception as e:
        print(f"[DB] Error al mostrar estadísticas: {e}")
    finally:
        conn.close()

async def iniciar_servidores_dinamicos(hostname, port, cola_pedidos, semaforo):
    async def manejar_cliente(reader, writer):
        try:
            if not semaforo.acquire(block=False):
                writer.write("❌ Límite de pedidos alcanzado. Intente más tarde.\n".encode("utf-8"))
                await writer.drain()
                await asyncio.sleep(0.1)  # Permite que el cliente lea el mensaje antes de cerrar
                writer.close()
                await writer.wait_closed()
                return

            writer.write('📩 Bienvenido al Servidor de Pedidos\n'
                         'Por favor envíe un JSON válido del tipo \n'
                         '{"cliente": "nombre","productos": ["producto1", "producto2"],"direccion": "direccion"}\n'.encode("utf-8"))
            await writer.drain()

            data = await reader.read(1024)
            pedido = data.decode().strip()
            print(f"[SERVER] Pedido recibido: {pedido}")

            try:
                pedido_data = json.loads(pedido)
                cola_pedidos.put(pedido_data)
                print(f"[SERVER] Pedido encolado: {pedido_data}")
                writer.write("✅ Pedido encolado\n".encode("utf-8"))
            except json.JSONDecodeError:
                writer.write("❌ JSON inválido\n".encode("utf-8"))
                print("[SERVER] ❌ JSON inválido recibido.")
                semaforo.release()
            await writer.drain()

        except Exception as e:
            print(f"[SERVER] ⚠️ Error manejando cliente: {e}")
            try:
                writer.write("⚠️ Error interno del servidor\n".encode("utf-8"))
                await writer.drain()
            except:
                pass
        finally:
            writer.close()
            await writer.wait_closed()

    sockets = []
    try:
        infos = socket.getaddrinfo(
            hostname,
            port,
            family=socket.AF_UNSPEC,
            proto=socket.IPPROTO_TCP,
            type=socket.SOCK_STREAM
        )
        print("=== Direcciones devueltas por getaddrinfo ===")
        for af, socktype, proto, canonname, sa in infos:
            print(f"{'IPv6' if af == socket.AF_INET6 else 'IPv4'} → {sa}")

        for af, socktype, proto, canonname, sa in infos:
            try:
                sock = socket.socket(af, socktype, proto)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(sa)
                sock.listen(100)
                sock.setblocking(False)
                sockets.append((sock, af))
            except Exception as e:
                print(f"[SERVER] ⚠️ No se pudo abrir socket en {sa}: {e}")
    except Exception as e:
        print(f"[SERVER] ❌ Error en getaddrinfo: {e}")
        return

    servidores = []
    for sock, af in sockets:
        server = await asyncio.start_server(manejar_cliente, sock=sock)
        servidores.append(server)
        ipver = "IPv6" if af == socket.AF_INET6 else "IPv4"
        print(f"[SERVER] Escuchando en {ipver} {sock.getsockname()}")

    await asyncio.gather(*(s.serve_forever() for s in servidores))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("SERVER_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("SERVER_PORT", 8888)))
    parser.add_argument("--workers", type=int, default=int(os.getenv("WORKER_COUNT", 3)))
    args = parser.parse_args()

    inicializar_db()

    cola_pedidos = Queue()
    db_lock = Lock()
    semaforo = Semaphore(MAX_PEDIDOS_EN_COLA)

    procesos = []
    for _ in range(args.workers):
        p = Process(target=worker, args=(cola_pedidos, db_lock, semaforo))
        p.start()
        procesos.append(p)

    try:
        asyncio.run(iniciar_servidores_dinamicos(args.host, args.port, cola_pedidos, semaforo))
    except KeyboardInterrupt:
        print("\n[SERVER] Cerrando servidor...")
    finally:
        for _ in procesos:
            cola_pedidos.put(None)
        for p in procesos:
            p.join()

        print("[SERVER] Servidor finalizado.")
        mostrar_estadisticas()

if __name__ == "__main__":
    main()
