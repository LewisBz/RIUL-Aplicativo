#!/bin/sh
# Arranque del contenedor `app`: migra el esquema, siembra datos y lanza Gunicorn.
#
#   SEED_DEMO=1 (por defecto)  -> `flask seed-demo`: REEMPLAZA usuarios y datos de
#                                 negocio con el dataset demo (idempotente).
#   SEED_DEMO=0                -> solo `flask seed-db` (catálogos); conserva los datos.
set -eu

UPLOAD_DIR="${UPLOAD_FOLDER:-/app/uploads}"
mkdir -p "$UPLOAD_DIR/posts" "$UPLOAD_DIR/evidences"

# Los volúmenes nombrados pueden venir con dueño root: se corrige antes de bajar privilegios.
if [ "$(id -u)" = "0" ]; then
  chown -R riul:riul "$UPLOAD_DIR"
  RUN="setpriv --reuid=riul --regid=riul --init-groups"
else
  RUN=""
fi

echo "[riul] Aplicando migraciones..."
$RUN flask db upgrade

if [ "${SEED_DEMO:-1}" = "1" ]; then
  echo "[riul] Sembrando dataset demo (SEED_DEMO=1)..."
  $RUN flask seed-demo
else
  echo "[riul] SEED_DEMO=0: se siembran solo los catálogos."
  $RUN flask seed-db
fi

echo "[riul] Iniciando Gunicorn..."
exec $RUN gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  run:app
