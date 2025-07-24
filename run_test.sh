#!/bin/bash
echo "🧪 Ejecutando testcliente..."
docker compose run --rm testcliente
docker compose down
