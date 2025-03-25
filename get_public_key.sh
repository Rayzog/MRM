#!/bin/sh

# Получаем JWKS
echo "aaaa"
JWKS_RESPONSE=$(curl -s http://keycloak:8080/realms/myMRM/protocol/openid-connect/certs)
echo $JWKS_RESPONSE
echo "bbbb"
# Извлекаем параметры RSA ключа
x5c=$(echo "$JWKS_RESPONSE" | jq -r '.keys[0].x5c')
echo $x5c
echo "cccc"
# Генерируем PEM-формат
PEM_KEY=$(echo $x5c | tr -d '\n' | sed -n 's/.*MBAxDjAMBgNVBAMMBW15TVJN\(.*\)MA0GCSqGSIb3DQEBCwUAA4IBAQ.*/\1/p')
echo $PEM_KEY
echo "dddd"

echo -n "KEYCLOAK_PUBLIC_KEY=$PEM_KEY" >> ".env"

exec "$@"