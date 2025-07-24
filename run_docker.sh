#!/bin/bash
echo "🐳 Ejecutando con Docker Compose usando .env.docker"
docker compose --env-file .env.docker up --build
