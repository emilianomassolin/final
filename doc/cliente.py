import socket
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Cliente de pedidos")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='IP del servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor')
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
        with socket.create_connection((args.host, args.port)) as sock:
            mensaje = json.dumps(pedido).encode()
            sock.sendall(mensaje)
            print("Pedido enviado correctamente.")
    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")


if __name__ == '__main__':
    main()
