import socket
import time
import threading

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

if __name__ == "__main__":
    main()
