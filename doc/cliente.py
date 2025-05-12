import socket
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Cliente de pedidos")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='IP del servidor')
    parser.add_argument('--port', type=int, default=8888, help='Puerto del servidor')
    args = parser.parse_args()

    print("=== Cliente de pedidos ===")
    nombre = input("Nombre del cliente: ")
    productos = input("Productos (separados por coma): ")
    direccion = input("Dirección de entrega: ")

    pedido = {
        "cliente": nombre,
        "productos": productos.split(','),
        "direccion": direccion
    }

    try:
        infos = socket.getaddrinfo(args.host, args.port, type=socket.SOCK_STREAM)
        for info in infos:
            af, socktype, proto, canonname, sa = info
            try:
                with socket.socket(af, socktype, proto) as s:
                    s.connect(sa)
                    mensaje = json.dumps(pedido).encode()
                    s.sendall(mensaje)
                    print("Pedido enviado correctamente.")

                    # Esperar la respuesta del servidor
                    respuesta = s.recv(1024).decode()
                    print(f"Respuesta del servidor: {respuesta}")
                    break
            except OSError:
                continue
        else:
            print("No se pudo conectar al servidor.")
    except Exception as e:
        print(f"Error al procesar el pedido: {e}")


if __name__ == '__main__':
    main()
