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

    
if __name__ == "__main__":
    main()
