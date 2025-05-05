
# 📦 Sistema de Gestión de Pedidos

## Descripción

Aplicación cliente-servidor para la gestión de pedidos, utilizando sockets TCP/IP y mecanismos de concurrencia.  
Permite que múltiples clientes envíen pedidos al servidor de manera concurrente, los cuales son encolados y procesados de forma paralela.

## Tecnologías utilizadas

- Sockets TCP/IP
- Async I/O
- IPC (Inter-Process Communication)
- Concurrencia y paralelismo
- Parseo de argumentos por línea de comandos
- (Opcional) Docker para despliegue
- (Opcional) Base de datos (SQLite)

## Arquitectura

- **Cliente:**  
  - Se conecta al servidor mediante TCP/IP.
  - Envía datos de un pedido (cliente, productos, dirección).
  - Puede configurarse mediante argumentos por consola (IP, puerto).

- **Servidor:**  
  - Escucha múltiples clientes de forma concurrente usando async I/O.
  - Recibe y encola pedidos utilizando mecanismos IPC (`multiprocessing.Queue`).
  - Procesa los pedidos en paralelo mediante un pool de workers (hilos o procesos).

- **Workers:**  
  - Consumen pedidos de la cola.
  - Simulan el procesamiento y entrega del pedido.



## Uso

- Los clientes envían pedidos que incluyen:
  - Nombre del cliente
  - Productos solicitados
  - Dirección de entrega

- El servidor recibe los pedidos, los encola y los procesa de forma paralela.
- El procesamiento simula la preparación y entrega de los pedidos.

## Extras futuros

- Desplegar con Docker.
- Persistir pedidos en una base de datos (SQLite).
- Crear una pequeña interfaz web o de escritorio para realizar pedidos.

