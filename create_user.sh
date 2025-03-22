#!/bin/sh

KEYCLOAK_URL="http://localhost:8080"
REALM_NAME="myMRM"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"

# Ждем доступности Keycloak
until $(curl --output /dev/null --silent --head --fail $KEYCLOAK_URL); do
  echo "Ждем запуска Keycloak..."
  sleep 5
done

# Получаем токен администратора
ADMIN_TOKEN=$(curl -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  --data "grant_type=password&client_id=admin-cli&username=$ADMIN_USER&password=$ADMIN_PASSWORD" \
  | jq -r .access_token)

# Создаем пользователя
curl -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "123",
	"firstName": "Ivan",
	"lastName": "Fedorov",
	"email": "qwer@gmail.com",
	"emailVerified": true,
    "enabled": true,
    "credentials": [{
      "type": "password",
      "value": "123",
      "temporary": false
    }]
  }'