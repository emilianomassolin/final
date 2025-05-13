# 🛠️ INSTALL.md - Instrucciones de instalación y despliegue

Este documento describe cómo clonar, instalar y lanzar la aplicación del **Sistema de Gestión de Pedidos**, una app concurrente cliente-servidor basada en Python, sockets, multiprocessing y SQLite.

---

## 📦 Requisitos

- Python 3.10 o superior  
- `pip` (gestor de paquetes de Python)  
- Git  


---

## 📥 Clonar el repositorio
```bash
git clone git@github.com:emilianomassolin/final.git
cd doc
```
---
## Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate 
```
---
##  Ejecutar el servidor
```bash
python main.py --host :: --port 8888 --workers 2

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