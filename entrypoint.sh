#!/bin/sh

# Ждем доступности PostgreSQL
until psql postgres://postgres:password@postgres:5432/MRM -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Выполнение SQL-скрипта для инициализации базы данных
psql postgres://postgres:password@postgres:5432/MRM -f /docker-entrypoint-initdb.d/local_user.sql

# Далее запуск приложения
exec "$@"