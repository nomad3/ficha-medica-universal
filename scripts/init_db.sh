#!/bin/bash
set -e

# Esperar a que el backend esté disponible (que a su vez espera a la base de datos)
echo "Esperando a que el backend esté disponible..."
until curl -s http://backend:8000/health > /dev/null; do
  echo "Backend no disponible, esperando..."
  sleep 5
done

echo "Backend disponible, esperando 5 segundos adicionales para asegurar que esté completamente inicializado..."
sleep 5

# Ejecutar el script de generación de datos
echo "Generando datos de prueba..."
python /app/scripts/generate_test_data.py

# Importar los datos a través de la API
echo "Importando datos a la base de datos..."
curl -X POST http://backend:8000/fhir/import -H "Content-Type: application/json" -d @datos_prueba.json

echo "Inicialización completada." 