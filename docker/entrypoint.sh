#!/usr/bin/env sh
set -e

echo "⏳ Waiting for PostgreSQL at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
python - <<'PY'
import os, socket, time

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("PostgreSQL is not reachable")
print("✅ PostgreSQL is up")
PY

echo "🔄 Applying database migrations..."
alembic upgrade head

echo "🚀 Starting bot..."
exec python -m bot.bot
