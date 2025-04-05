curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token -d "grant_type=password&client_id=admin-cli&username=admin&password=admin" >> log.txt

for /f "delims=" %%i in ('curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token -d "grant_type=password&client_id=admin-cli&username=admin&password=admin" ^| jq -r ".access_token"' ) do set ADMIN_TOKEN=%%i

curl -X GET http://localhost:8080/admin/realms/myMRM/users ^
  -H "Authorization: Bearer %ADMIN_TOKEN%" ^
  -H "Content-Type: application/json" ^
  > users_list.json

sleep 5