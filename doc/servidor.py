import asyncio
import multiprocessing
from multiprocessing import Queue, Process
import argparse
import time

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
    data = await reader.read(1024)
    pedido = data.decode()
    print(f"[SERVER] Pedido recibido: {pedido}")
    cola_pedidos.put(pedido)
    writer.write("Pedido recibido y encolado".encode())
    await writer.drain()
    writer.close()

# --- Main Async para servidor ---
async def iniciar_servidor(host, puerto):
    server = await asyncio.start_server(manejar_cliente, host, puerto)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[SERVER] Escuchando en {addrs}")
    async with server:
        await server.serve_forever()

# --- Main principal con argumentos y procesos ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
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
        asyncio.run(iniciar_servidor(args.host, args.port))
    except KeyboardInterrupt:
        print("\n[SERVER] Cerrando servidor...")
    finally:
        # Detener los workers
        for _ in procesos:
            cola_pedidos.put(None)
        for p in procesos:
            p.join()
        print("[SERVER] Servidor finalizado.")

if __name__ == "__main__":
    main()
