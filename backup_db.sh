#!/bin/bash

if [ -f .env ]; then
  set -a 
  source .env
  set +a
else
  echo ".env file not found. Please create one with your DB credentials."
  exit 1
fi

BACKUP_DIR="db_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"

mkdir -p "$BACKUP_DIR"
echo "Backup directory is: '$BACKUP_DIR/'"

echo "Starting backup of database '$POSTGRES_DB'..."

if docker-compose exec -T db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > "$FILENAME"; then
  echo "Backup successful!"
  echo "File saved to: $FILENAME"
else
  echo "Error: Backup failed."
  rm -f "$FILENAME"
  exit 1
fi

echo "Backup process finished."