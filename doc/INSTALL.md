# 🛠️ INSTALL.md - Instrucciones de Instalación y Despliegue

Este documento detalla cómo clonar, instalar y lanzar la aplicación del **Sistema de Gestión de Pedidos**, una app concurrente cliente-servidor basada en Python, `sockets`, `multiprocessing` y `SQLite`.

---

## 📦 Requisitos

- Python 3.10 o superior  
- `pip` (gestor de paquetes de Python)  
- `git`  
- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/)

---

## 📥 Clonar el repositorio

```bash
git clone git@github.com:emilianomassolin/final.git
cd final
```

---

## 🐍 Instalación local (modo desarrollo)

### Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar el servidor

```bash
python servidor.py --host :: --port 8888 --workers 2
```

### Usar cliente

```bash
python cliente.py
```

---

## 🧪 Probar con cliente manual (telnet)

```bash
telnet localhost 8888
```

Luego, pegar un JSON como este:

```json
{
  "cliente": "Juan Pérez",
  "productos": ["pan", "agua"],
  "direccion": "Av. Siempre Viva 742"
}
```

---

## 🐳 Uso con Docker

### Build de los contenedores

```bash
docker compose build
```

### Ejecutar servidor y cliente de prueba

```bash
./run_test.sh
```

### Ejecutar solo el servidor

```bash
./run_servidor.sh
```

### Ejecutar solo el cliente

```bash
./run_cliente.sh
```

### Ejecutar servidor en entorno local (usando `.env.local`)

```bash
./run_local.sh
```

---

## 📁 Estructura del Proyecto

```
final/
│
├── servidor.py           # Código principal del servidor
├── cliente.py            # Código del cliente
├── testCliente.py        # Pruebas automáticas
├── Dockerfile            # Instrucciones para imagen Docker
├── docker-compose.yml    # Definición de servicios Docker
├── requirements.txt      # Dependencias Python
├── .env.docker           # Variables de entorno para Docker
├── .env.local            # Variables para uso local
├── run_test.sh           # Ejecuta testCliente en Docker
├── run_servidor.sh       # Ejecuta solo el servidor en Docker
├── run_cliente.sh        # Ejecuta solo cliente en Docker
├── run_local.sh          # Ejecuta servidor local sin Docker
└── README.md             # Descripción general del proyecto
```

---

## ✅ ¡Listo para usar!

La aplicación quedará escuchando en el puerto `8888`, y los pedidos se procesarán concurrentemente y se almacenarán en una base SQLite con marca temporal de inicio y fin.

---