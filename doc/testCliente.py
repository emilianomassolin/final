import asyncio
import json
import random
import socket

HOST = 'localhost'
PORT = 8888

productos_disponibles = ['pizza', 'empanadas', 'hamburguesa', 'pastas', 'ensalada']
calles = ['Calle Falsa 123', 'Av. Siempre Viva 742', 'San Martín 1000', 'Belgrano 555']

async def abrir_conexion_dualstack(host, port):
    """Intenta abrir conexión con IPv6 y luego con IPv4."""
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM)
        for af, socktype, proto, canonname, sa in infos:
            try:
                sock = socket.socket(af, socktype, proto)
                sock.setblocking(False)
                await asyncio.get_event_loop().sock_connect(sock, sa)
                reader, writer = await asyncio.open_connection(sock=sock)
                print(f"[TEST] Conectado a {sa} usando {'IPv6' if af == socket.AF_INET6 else 'IPv4'}")
                return reader, writer
            except Exception as e:
                print(f"[TEST] Falló conexión con {sa}: {e}")
                continue
        raise ConnectionError("No se pudo conectar con IPv4 ni IPv6")
    except socket.gaierror as e:
        raise ConnectionError(f"Error de resolución de DNS: {e}")

async def cliente(pedido_id):
    try:
        reader, writer = await abrir_conexion_dualstack(HOST, PORT)

        pedido = {
            "cliente": f"cliente_{pedido_id}",
            "productos": random.sample(productos_disponibles, k=random.randint(1, 3)),
            "direccion": random.choice(calles)
        }

        mensaje = json.dumps(pedido).encode()
        print(f"[TEST] Enviando pedido {pedido_id}: {pedido}")

        writer.write(mensaje)
        await writer.drain()

        respuesta = await reader.read(1024)
        print(f"[TEST] Respuesta del servidor: {respuesta.decode().strip()}")

        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"[TEST] Error al enviar pedido {pedido_id}: {e}")

async def main():
    tareas = [cliente(i + 1) for i in range(10)]  # 10 clientes simultáneos
    await asyncio.gather(*tareas)

if __name__ == "__main__":
    asyncio.run(main())
