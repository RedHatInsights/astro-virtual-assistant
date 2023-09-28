#!/bin/sh

if [ -z "$1" ]; then
  echo "Usage: $0 <type>"
  exit 1
fi

type="$1"

if [[ ! -z "${ACG_CONFIG}" ]]; then
  export DB_HOST=$(jq -r '.database.hostname' ${ACG_CONFIG})
  export DB_PORT=$(jq -r '.database.port' ${ACG_CONFIG})
  export DB_USER=$(jq -r '.database.username' ${ACG_CONFIG})
  export DB_PASSWORD=$(jq -r '.database.password' ${ACG_CONFIG})
  export DB_NAME=$(jq -r '.database.name' ${ACG_CONFIG})

  export DATABASE_SSLMODE=$(jq -r '.database.sslMode' ${ACG_CONFIG})
  if [[ $DATABASE_SSLMODE = "null" ]]; then
    unset DATABASE_SSLMODE
  fi

fi

if [ "$type" = "api" ]; then
  python app.py run --endpoints endpoints.yml
elif [ "$type" = "actions" ]; then
  python run_actions.py --actions actions
else
  echo "Unknown type: $type"
  exit 1
fi
