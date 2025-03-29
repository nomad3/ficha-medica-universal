#!/bin/bash
set -e

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos esté disponible..."
sleep 5

# Iniciar la aplicación
exec "$@" 