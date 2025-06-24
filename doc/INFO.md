
# 📦 Sistema de Gestión de Pedidos

## Descripción

Aplicación cliente-servidor asincrónica y multiproceso para gestionar pedidos de forma eficiente y concurrente.
Los clientes se conectan vía TCP (IPv4/IPv6) y envían pedidos en formato JSON. El servidor los encola, los procesa en paralelo mediante **multiprocessing**, y finalmente los persiste en una **base de datos SQLite** usando un proceso separado.

## Tecnologías utilizadas

- `Python 3`
- `asyncio` (manejo de múltiples clientes concurrentes)
- `multiprocessing` (procesos workers y de base de datos)
- `sqlite3` (almacenamiento persistente)
- `sockets TCP` con soporte  (IPv4/IPv6)
- `argparse` para configuración por línea de comandos

## Arquitectura

- **Cliente:**  
  - Se conecta al servidor TCP (IPv4 o IPv6).
  - Envía un pedido en JSON con: `cliente`, `productos`, `dirección`.
  - Puede ejecutarse múltiples veces en paralelo para simular concurrencia.
  - Configurable mediante argumentos (`--host`, `--port`).

- **Servidor:**  
  - Escucha en paralelo por sockets separados IPv4 e IPv6.
  - Acepta múltiples conexiones simultáneas usando `asyncio`.
  - Encola pedidos en `multiprocessing.Queue`.
  - Lanza múltiples workers para procesar pedidos en paralelo.
  - Protege el acceso a la base de datos con `multiprocessing.Lock`.

- **Workers:**  
  - Simulan procesamiento de cada pedido (`time.sleep(...)`).
  - Guardan en SQLite con `fecha_inicio` y `estado='en proceso'`.
  - Luego actualizan a `estado='listo'` y registran `fecha_fin`.
  - Permiten medir la duración de cada pedido procesado.

## Métricas y Tiempos

Cada pedido almacena:

- `fecha_inicio`: cuándo se comenzó a procesar.
- `fecha_fin`: cuándo se finalizó el pedido.
- `duración`: calculada automáticamente en segundos.

Esto permite verificar fácilmente si los pedidos se procesaron en paralelo (duraciones similares o `fecha_inicio` iguales).




## Uso

- Los clientes envían pedidos que incluyen:
  - Nombre del cliente
  - Productos solicitados
  - Dirección de entrega

- El servidor recibe los pedidos, los encola y los procesa de forma paralela.
- El procesamiento simula la preparación y entrega de los pedidos.



