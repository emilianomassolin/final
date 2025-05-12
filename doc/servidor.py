import asyncio
import json
import multiprocessing
from multiprocessing import Queue, Process
import argparse
import time
import socket


# Cola compartida entre procesos
cola_pedidos = Queue()

# --- Worker que procesa pedidos ---
def worker(cola):
    while True:
        pedido = cola.get()
        if pedido is None:
            break
        print(f"[WORKER] Procesando pedido: {pedido}")
        time.sleep(2)
        print(f"[WORKER] Pedido completado: {pedido}")

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

        # Intentar procesar el JSON
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

# --- Main principal con argumentos y procesos ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="::")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    # Crear procesos worker
    procesos = []
    for _ in range(args.workers):
        p = Process(target=worker, args=(cola_pedidos,))
        p.start()
        procesos.append(p)

    try:
        asyncio.run(iniciar_servidor_dualstack(args.host, args.port))
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
