#!/bin/sh
/app/db_operation.sh
/app/get_public_key.sh
exec "$@"