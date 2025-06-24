# Final computación 2
 Aplicación cliente-servidor para la gestión de pedidos
### Alumno: Emiliano Massolin
# 📦 Sistema de Gestión de Pedidos

## 🧾 Descripción

Aplicación cliente-servidor escrita en Python para la gestión concurrente de pedidos, utilizando sockets TCP/IP, `asyncio`, `multiprocessing` y `sqlite3`.  
Permite que múltiples clientes se conecten simultáneamente para enviar pedidos, los cuales son procesados en paralelo por varios **workers**.  
Cada pedido es almacenado en una base de datos SQLite con información de inicio y fin del procesamiento.

---

## 🧰 Tecnologías utilizadas

- Python 3.10+
- Sockets TCP/IP (IPv4 e IPv6 en sockets separados)
- Async I/O (`asyncio`) para manejar múltiples clientes concurrentes
- Procesamiento paralelo con `multiprocessing.Process`
- Comunicación IPC mediante `multiprocessing.Queue`
- Exclusión mutua con `multiprocessing.Lock`
- Base de datos SQLite (`sqlite3`)
- Línea de comandos (`argparse`)

---
## 🧱 Arquitectura

### 🧍 Cliente

- Se conecta al servidor por TCP (puede ser IPv4 o IPv6).
- Envía un pedido en formato JSON con los siguientes datos:
  - Nombre del cliente
  - Lista de productos
  - Dirección de entrega
- Configurable mediante argumentos: `--host`, `--port`.

### 🧠 Servidor

- Escucha en paralelo por IPv4 (`127.0.0.1`) e IPv6 (`::1`).
- Acepta múltiples conexiones concurrentes con `asyncio`.
- Por cada pedido recibido:
  - Lo valida (JSON).
  - Lo encola en `multiprocessing.Queue`.

### 🔨 Workers

- Procesos independientes.
- Consumen pedidos desde la cola.
- Simulan procesamiento (`time.sleep`).
- Guardan en la base de datos:
  - `fecha_inicio`: cuando comienza el procesamiento.
  - `fecha_fin`: cuando termina.
  - `estado`: `"en proceso"` → `"listo"`.
- Protegen el acceso a la base con un `Lock` para evitar condiciones de carrera.

---

## Ejecutar el servidor
```bash
python3 servidor.py --host :: --port 8888 --workers 2

```
---
## Usar cliente
```bash
python3 cliente.py

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

