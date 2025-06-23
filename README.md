# Final computación 2
 Aplicación cliente-servidor para la gestión de pedidos
### Alumno: Emiliano Massolin
# 📦 Sistema de Gestión de Pedidos

## 🧾 Descripción

Aplicación cliente-servidor escrita en Python para la gestión concurrente de pedidos, utilizando sockets TCP/IP, `asyncio`, multiprocessing y SQLite.
Permite que múltiples clientes se conecten simultáneamente para enviar pedidos, los cuales son encolados y procesados en paralelo por un conjunto de workers.

---

## 🧰 Tecnologías utilizadas

- Python 3.10+
- Sockets TCP/IP
- Async I/O (`asyncio`)
- Concurrencia y paralelismo (`multiprocessing`)
- SQLite (persistencia de pedidos)
- Comunicación IPC mediante `multiprocessing.Queue`
- Parseo de argumentos (`argparse`)


---

## 🧱 Arquitectura

### 🔁 Cliente

- Se conecta al servidor por TCP/IP.
- Envía un pedido en formato JSON que contiene:
  - Nombre del cliente
  - Lista de productos
  - Dirección de entrega

### 🧠 Servidor (asyncio)

- Acepta múltiples conexiones concurrentes usando `asyncio`.
- Por cada pedido recibido:
  - Lo valida y lo transforma en objeto Python.
  - Lo encola en una cola compartida (`multiprocessing.Queue`).

### 🔨 Workers

- Procesos independientes.
- Consumen pedidos desde la cola.
- Simulan procesamiento (tiempo de espera).
- Persisten el pedido en una base de datos SQLite (`db/pedidos.db`).

---

## Ejecutar el servidor
```bash
python servidor.py --host :: --port 8888 --workers 2

```
---
## Usar cliente
```bash
python cliente.py

```
---
## Probar con cliente manual (telnet )
```bash
telnet localhost 8888
pega el siguiente json
 {
  "cliente": "Juan Pérez",
  "productos": ["pan", "agua"],
  "direccion": "Av. Siempre Viva 742"
}

```

