#!/bin/bash
set -e

echo "🚀 Starting Medical Report Simplifier..."

# Get the port from environment variable, default to 8000
PORT=${PORT:-8000}
echo "📡 Using port: $PORT"

# Validate that PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ Error: PORT must be a number, got: $PORT"
    echo "🔧 Falling back to port 8000"
    PORT=8000
fi

echo "🧪 Running startup validation..."
python startup_test.py

echo "🎯 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info --access-log
