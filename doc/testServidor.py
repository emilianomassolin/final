import socket
import time
import threading
import json
import unittest
import argparse

HOST = '127.0.0.1'
PORT = 65432
NUM_CLIENTS = 10  # cantidad de clientes simulados

def simulate_client(client_id):
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            pedido = f"Cliente{client_id}|ProductoX,ProductoY|Calle Falsa 123"
            sock.sendall(pedido.encode('utf-8'))
            print(f"[CLIENTE {client_id}] Pedido enviado")
    except Exception as e:
        print(f"[CLIENTE {client_id}] Error: {e}")

def main():
    threads = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=simulate_client, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.1)  # leve retardo entre lanzamientos

    for t in threads:
        t.join()

    print("\n Test completado.")

class TestClienteIPv4IPv6(unittest.TestCase):

    def enviar_pedido(self, mensaje):
        infos = socket.getaddrinfo(HOST, PORT, type=socket.SOCK_STREAM)
        for info in infos:
            af, socktype, proto, canonname, sa = info
            try:
                with socket.socket(af, socktype, proto) as s:
                    s.connect(sa)
                    s.sendall(mensaje.encode())
                    respuesta = s.recv(1024).decode()
                    return respuesta
            except Exception as e:
                continue
        return None
def test_pedido_ipv4_ipv6(self):

        pedido = {
            "cliente": "Test IPv4/IPv6",
            "productos": ["pizza", "gaseosa"],
            "direccion": "Calle IPvX 456"
        }
        mensaje = json.dumps(pedido)
        respuesta = self.enviar_pedido(mensaje)
        self.assertIsNotNone(respuesta)
        self.assertIn("Pedido recibido", respuesta)


if __name__ == "__main__":
    main()
