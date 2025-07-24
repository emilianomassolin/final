# 📦 Final Computación 2 - Sistema de Gestión de Pedidos

### 👨‍🎓 Alumno: Emiliano Massolin

---

## 🧾 Descripción

Aplicación cliente-servidor escrita en Python para la gestión **concurrente** de pedidos, utilizando:
- Sockets TCP/IP
- Async I/O (`asyncio`)
- Procesos paralelos (`multiprocessing`)
- Base de datos (`sqlite3`)

Permite que múltiples clientes se conecten de forma simultánea y envíen pedidos, los cuales son procesados en paralelo por varios **workers**.  
Cada pedido es almacenado en una base de datos con información de inicio, fin y estado del procesamiento.

---

## 🧰 Tecnologías utilizadas

- Python 3.10+
- Sockets TCP/IP (IPv4 e IPv6)
- `asyncio` para concurrencia asíncrona
- `multiprocessing.Process` para procesamiento paralelo
- `multiprocessing.Queue` para comunicación entre procesos
- `multiprocessing.Lock` para exclusión mutua
- SQLite3 para persistencia
- `argparse` para línea de comandos
- `.env` con `python-dotenv` para variables de entorno
- Docker y Docker Compose

---

## 🧱 Arquitectura

### 🧍 Cliente

- Se conecta al servidor por TCP (IPv4 o IPv6).
- Envía un pedido en formato JSON con:
  - `cliente`: nombre del cliente
  - `productos`: lista de productos
  - `direccion`: dirección de entrega
- Configurable por argumentos `--host`, `--port` o variables de entorno.

---

### 🧠 Servidor

- Escucha en paralelo conexiones IPv4 (`0.0.0.0`) e IPv6 (`::`).
- Acepta múltiples conexiones simultáneas con `asyncio`.
- Por cada pedido:
  - Valida que sea JSON válido.
  - Encola el pedido en una `Queue`.
  - Responde según disponibilidad (límite de cola configurable).

---

### 🔨 Workers

- Procesos independientes que:
  - Toman pedidos de la cola.
  - Simulan procesamiento (con `time.sleep`).
  - Guardan los datos en SQLite:
    - `fecha_inicio`
    - `fecha_fin`
    - `estado` (`"en proceso"` → `"listo"`)
- Protegen acceso concurrente a la base con un `Lock`.

---

## 🚀 Ejecución sin Docker (modo local)

### Ejecutar el servidor:
```bash
python3 servidor.py --host :: --port 8888 --workers 3
```

### Ejecutar el cliente:
```bash
python3 cliente.py
```

---

## 🧪 Probar con Telnet (cliente manual)

```bash
telnet localhost 8888
```

Y luego pegar:
```json
{
  "cliente": "Juan Pérez",
  "productos": ["pan", "agua"],
  "direccion": "Av. Siempre Viva 742"
}
```

---

## 🐳 Ejecución con Docker y Docker Compose

Este proyecto incluye configuración para levantar los servicios en contenedores:

- `servidor`: ejecuta el servidor con workers
- `cliente`: cliente automático
- `testcliente`: ejecuta pruebas de concurrencia

### 🔧 Archivos importantes:

- `Dockerfile`: define cómo se construyen las imágenes.
- `docker-compose.yml`: orquesta múltiples contenedores.
- `.env.docker`: variables de entorno para Docker.
- `.env.local`: configuración para uso sin Docker.

### ▶️ Comandos útiles

#### Construir imágenes y levantar todo:
```bash
docker compose up --build
```

#### Ejecutar solo el servidor:
```bash
./run_servidor.sh
```

#### Ejecutar solo el cliente automático:
```bash
./run_cliente.sh
```

#### Ejecutar pruebas con múltiples clientes:
```bash
./run_test.sh
```

#### Ejecutar localmente sin Docker:
```bash
./run_local.sh
```

#### Ver logs de los contenedores:
```bash
docker compose logs -f
```

#### Detener y eliminar contenedores:
```bash
docker compose down
```

---

## 📂 Estructura de archivos

```
.
├── cliente.py
├── servidor.py
├── testCliente.py
├── Dockerfile
├── docker-compose.yml
├── .env.local
├── .env.docker
├── run_servidor.sh
├── run_cliente.sh
├── run_test.sh
├── run_local.sh
└── README.md
```

---

## ✅ Observaciones

- El sistema detecta automáticamente si la cola está llena y responde con un mensaje de rechazo al cliente.
- El proyecto utiliza separación de entornos `.env.local` (modo local) y `.env.docker` (modo Docker).
- Los clientes pueden conectarse tanto por IPv4 como por IPv6.

---