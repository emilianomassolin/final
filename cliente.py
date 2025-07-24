import socket
import argparse
from dotenv import load_dotenv
import os
import json

def main():
    parser = argparse.ArgumentParser(description="Cliente de pedidos")
    parser.add_argument('--host', type=str, default='localhost', help='IP del servidor (IPv4 o IPv6)')
    parser.add_argument('--port', type=int, default=8888, help='Puerto del servidor')
    load_dotenv()
    host_env = os.getenv('SERVER_HOST', 'localhost')
    port_env = int(os.getenv('SERVER_PORT', 8888))
    args = parser.parse_args()
    args.host = args.host or host_env
    args.port = args.port or port_env

    print("=== Cliente de pedidos ===")
    nombre = input("Nombre del cliente: ")
    productos = input("Productos (separados por coma): ")
    direccion = input("Dirección de entrega: ")

    pedido = {
        "cliente": nombre,
        "productos": [p.strip() for p in productos.split(',')],
        "direccion": direccion
    }

    try:
        # getaddrinfo busca automáticamente IPv6 e IPv4 según el host
        infos = socket.getaddrinfo(args.host, args.port, proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM)

        for af, socktype, proto, canonname, sa in infos:
            try:
                with socket.socket(af, socktype, proto) as s:
                    s.connect(sa)
                    print(f"Conectado a {sa} usando {'IPv6' if af == socket.AF_INET6 else 'IPv4'}")

                    mensaje = json.dumps(pedido).encode()
                    s.sendall(mensaje)

                    respuesta = s.recv(1024).decode()
                    print(f"Respuesta del servidor: {respuesta}")
                    break
            except OSError as err:
                print(f"No se pudo conectar con {sa}: {err}")
                continue
        else:
            print("❌ No se pudo establecer conexión con ninguna dirección (IPv4/IPv6).")
    except Exception as e:
        print(f"⚠️ Error general al procesar el pedido: {e}")

if __name__ == '__main__':
    main()