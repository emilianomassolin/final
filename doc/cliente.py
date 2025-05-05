import socket
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Cliente de pedidos")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='IP del servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor')
    args = parser.parse_args()




if __name__ == '__main__':
    main()
