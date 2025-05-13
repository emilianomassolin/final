
# 📦 Sistema de Gestión de Pedidos

## Descripción

Aplicación cliente-servidor asincrónica y multiproceso para gestionar pedidos de forma eficiente y concurrente.
Los clientes se conectan vía TCP (IPv4/IPv6) y envían pedidos en formato JSON. El servidor los encola, los procesa en paralelo mediante **multiprocessing**, y finalmente los persiste en una **base de datos SQLite** usando un proceso separado.

## Tecnologías utilizadas

- `Python 3`
- `asyncio` (manejo de múltiples clientes concurrentes)
- `multiprocessing` (procesos workers y de base de datos)
- `sqlite3` (almacenamiento persistente)
- `sockets TCP` con soporte **dual-stack** (IPv4/IPv6)
- `argparse` para configuración por línea de comandos

## Arquitectura

- **Cliente:**  
  - Se conecta al servidor mediante TCP/IP (ipv4 o ipv6 "dual stack").
  - Envía datos de un pedido (cliente, productos, dirección).
  - Puede configurarse mediante argumentos por consola (IP, puerto).

- **Servidor:**  
  - Escucha múltiples clientes de forma concurrente usando async I/O.
  - Recibe y encola pedidos utilizando mecanismos IPC (`multiprocessing.Queue`).
  - Procesa los pedidos en paralelo mediante multiprocessing.process.

- **Workers:**  
  - Consumen pedidos de la cola.
  - Simulan el procesamiento y entrega del pedido.
  - Envian a la cola de la base de datos para que sean guardados y actualizados



## Uso

- Los clientes envían pedidos que incluyen:
  - Nombre del cliente
  - Productos solicitados
  - Dirección de entrega

- El servidor recibe los pedidos, los encola y los procesa de forma paralela.
- El procesamiento simula la preparación y entrega de los pedidos.



