#!/usr/bin/env bash
# Despliegue de la API de QualityOps dentro del contenedor 200 (T31).
# Ejecutar en el nodo Proxmox:   pct exec 200 -- bash -s < desplegar_api.sh
#   (o pegarlo dentro de:  pct enter 200)
# Variable opcional: RAMA (por defecto main).
set -euo pipefail
RAMA="${RAMA:-main}"

apt-get update && apt-get install -y python3-venv git curl openssl

# Usuario de servicio sin privilegios (la API no corre como root).
id qualityops >/dev/null 2>&1 || useradd --system --home /opt/qualityops --shell /usr/sbin/nologin qualityops

# Código: solo lectura para el usuario del servicio.
rm -rf /opt/qualityops
git clone --depth 1 --branch "$RAMA" https://github.com/TaikoVC/qualityops-ai.git /opt/qualityops
python3 -m venv /opt/qualityops/.venv
/opt/qualityops/.venv/bin/pip install --quiet fastapi==0.163.0 uvicorn==0.54.0

# Token de la API: se genera aquí, queda en un archivo legible solo por root.
install -d -m 700 /etc/qualityops
[ -f /etc/qualityops/api.env ] || echo "QUALITYOPS_API_TOKEN=$(openssl rand -hex 24)" > /etc/qualityops/api.env
chmod 600 /etc/qualityops/api.env

cat > /etc/systemd/system/qualityops-api.service <<'SERVICIO'
[Unit]
Description=QualityOps AI - API REST
After=network-online.target
Wants=network-online.target

[Service]
User=qualityops
WorkingDirectory=/opt/qualityops
EnvironmentFile=/etc/qualityops/api.env
ExecStart=/opt/qualityops/.venv/bin/uvicorn qualityops.api:app --host 0.0.0.0 --port 8000
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICIO

systemctl daemon-reload
systemctl enable --now qualityops-api
sleep 3
systemctl --no-pager status qualityops-api | head -5
curl -s http://127.0.0.1:8000/salud; echo
