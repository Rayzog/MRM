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
JWKS_RESPONSE=$(curl -s http://keycloak:8080/realms/myMRM/protocol/openid-connect/certs)
echo $JWKS_RESPONSE
# Извлекаем параметры RSA ключа
x5c=$(echo "$JWKS_RESPONSE" | jq -r '.keys[0].x5c')
echo $x5c
# Генерируем PEM-формат
PEM_KEY=$(echo $x5c | tr -d '\n' | sed -n 's/.*MBAxDjAMBgNVBAMMBW15TVJN\(.*\)MA0GCSqGSIb3DQEBCwUAA4IBAQ.*/\1/p')
echo $PEM_KEY

echo -n "KEYCLOAK_PUBLIC_KEY=$PEM_KEY" >> ".env"