#!/bin/bash
echo "📦 Usando configuración local (.env.local)"
cp .env.local .env

echo "🚀 Ejecutando servidor local..."
python servidor.py
