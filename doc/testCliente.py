import asyncio
import json
import random

HOST = 'localhost'
PORT = 8888

productos_disponibles = ['pizza', 'empanadas', 'hamburguesa', 'pastas', 'ensalada']
calles = ['Calle Falsa 123', 'Av. Siempre Viva 742', 'San Martín 1000', 'Belgrano 555']

async def cliente(pedido_id):
    reader, writer = await asyncio.open_connection(HOST, PORT)

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

async def main():
    tareas = [cliente(i + 1) for i in range(10)]  # 10 clientes simultáneos
    await asyncio.gather(*tareas)

if __name__ == "__main__":
    asyncio.run(main())
