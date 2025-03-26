#!/bin/sh

wait_for_keycloak() {
    echo "Waiting for Keycloak to start..."
    until nc -zv keycloak 8080
    do
        echo "Keycloak is unavailable - sleeping"
        sleep 5
    done
    echo "Keycloak is up and running"
}

# Ожидаем запуск Keycloak
wait_for_keycloak

# Получаем JWKS
JWKS_RESPONSE=$(curl -s http://keycloak:8080/realms/myMRM)
echo $JWKS_RESPONSE
# Извлекаем параметры RSA ключа
public_key=$(echo "$JWKS_RESPONSE" | jq -r '.public_key')
echo $public_key

# Экранируем слеши для корректной работы с sed
escaped_public_key=$(echo "$public_key" | sed 's/\//\\\//g')

# Обновляем или добавляем параметр KEYCLOAK_PUBLIC_KEY
if grep -q "^KEYCLOAK_PUBLIC_KEY=" .env; then
    # Если параметр существует, заменяем его значение
    sed -i "s/^KEYCLOAK_PUBLIC_KEY=.*/KEYCLOAK_PUBLIC_KEY=$escaped_public_key/" .env
else
    # Если параметра нет, добавляем его в конец файла
    echo "KEYCLOAK_PUBLIC_KEY=$public_key" >> .env
fi