#!/bin/sh

# Wait for database to be ready
echo "⌛ Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME; do
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Initialize database if needed
python3 /app/api/init_db.py

# Start Nginx and API server
echo "🚀 Starting AURA Dashboard with Database Support..."
nginx -g "daemon off;" &
python3 /app/api/app.py