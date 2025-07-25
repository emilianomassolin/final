# 📦 Sistema de Gestión de Pedidos

## 📝 Descripción

Aplicación cliente-servidor desarrollada en Python para la gestión eficiente y concurrente de pedidos.  
Los clientes se conectan mediante sockets TCP (tanto IPv4 como IPv6) y envían pedidos en formato JSON. El servidor recibe esos pedidos, los encola y los procesa en paralelo utilizando **multiprocessing**, almacenando la información en una base de datos **SQLite**.

---

## 🧰 Tecnologías utilizadas

- **Python 3**
- **asyncio** — Manejo asincrónico de múltiples clientes concurrentes
- **multiprocessing** — Procesamiento paralelo mediante procesos separados (workers)
- **sqlite3** — Persistencia de pedidos en base de datos
- **Sockets TCP** — Con soporte dual para IPv4 e IPv6
- **argparse** — Configuración del servidor por línea de comandos
- **Semaphore** — Controla la cantidad máxima de pedidos encolados simultáneamente

---

## 🧱 Arquitectura del sistema

### 👨‍💻 Cliente
- Se conecta al servidor vía TCP (IPv4 o IPv6).
- Envía un pedido en formato JSON con los campos:
  - `cliente` (nombre)
  - `productos` (lista de productos)
  - `dirección` (entrega)
- Se pueden ejecutar múltiples clientes en paralelo para simular concurrencia.
- Configurable con argumentos `--host` y `--port`.

### 🧠 Servidor
- Escucha en simultáneo por sockets separados IPv4 e IPv6.
- Maneja múltiples conexiones concurrentes con `asyncio`.
- Valida y encola los pedidos en una `multiprocessing.Queue`.
- Limita la cantidad de pedidos simultáneos en cola mediante un **Semaphore** configurable (por defecto, 6).
- Lanza varios **workers** para procesar los pedidos en paralelo.
- Protege el acceso a la base de datos con `Lock` para evitar condiciones de carrera.

### 🔒 Control de concurrencia con Semáforo

El sistema utiliza un **`multiprocessing.Semaphore`** para limitar la cantidad de pedidos que pueden estar en proceso al mismo tiempo.  
Esto evita sobrecargar al servidor cuando se reciben muchos pedidos en simultáneo.

- Si el semáforo alcanza su límite, el servidor rechaza el pedido con un mensaje:
  ```
  ❌ Límite de pedidos alcanzado. Intente más tarde.
  ```

- Cuando un pedido termina de procesarse, el semáforo se libera automáticamente.

Este mecanismo es esencial para proteger recursos limitados y garantizar un comportamiento controlado bajo alta concurrencia.

---

### 🔧 Workers
- Simulan procesamiento de pedidos (mediante `time.sleep`).
- Guardan los datos en la base de datos con:
  - `fecha_inicio` al comenzar
  - `estado='en proceso'`
- Luego actualizan:
  - `fecha_fin` al finalizar
  - `estado='listo'`
- Permiten medir la **duración total** del procesamiento de cada pedido.

---

## 📊 Métricas de procesamiento

Cada pedido registrado en la base de datos incluye:

- `fecha_inicio`: hora de inicio del procesamiento
- `fecha_fin`: hora de finalización
- `duración`: diferencia en segundos entre ambas

Esto permite verificar que los pedidos se están procesando **en paralelo**, observando fechas de inicio simultáneas o duraciones similares.

---

## 🚀 Flujo de uso

1. El cliente envía un pedido que contiene:
   - Nombre del cliente
   - Lista de productos
   - Dirección de entrega

2. El servidor:
   - Recibe y valida el pedido.
   - Verifica si hay lugar en el semáforo.
   - Si hay lugar, lo encola para su procesamiento.
   - Un **worker** lo toma, lo procesa y lo guarda en la base de datos.

3. Al finalizar, el servidor muestra estadísticas de duración y procesamiento.
