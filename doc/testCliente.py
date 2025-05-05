import socket
import unittest

HOST = "127.0.0.1"
PORT = 65432

class TestCliente(unittest.TestCase):

    def test_envio_pedido(self):
        pedido = "Cliente: Emiliano; Productos: pizza, gaseosa; Dirección: Calle Falsa 123"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(pedido.encode())
            data = s.recv(1024)
        self.assertIn("Pedido recibido", data.decode())

    def test_envio_pedido_vacio(self):
        pedido = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(pedido.encode())
            data = s.recv(1024)
        self.assertIn("Pedido recibido", data.decode())

    def test_multiples_pedidos(self):
        for i in range(5):
            pedido = f"Cliente {i}; Productos: producto{i}; Dirección: calle {i}"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(pedido.encode())
                data = s.recv(1024)
            self.assertIn("Pedido recibido", data.decode())

if __name__ == "__main__":
    unittest.main()
