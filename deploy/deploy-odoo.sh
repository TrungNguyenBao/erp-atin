#!/bin/bash
# Deploy Odoo 18 with Docker on VPS
# Usage: ./deploy-odoo.sh

set -euo pipefail

# --- VPS Configuration ---
VPS_IP="192.168.1.199"
VPS_USER="baotrung"
REMOTE_DIR="/home/baotrung/odoo-deploy"

echo "=== Odoo Docker Deployment ==="
echo "Target: ${VPS_USER}@${VPS_IP}"
echo ""

# --- Step 1: Install Docker on VPS ---
echo "[1/4] Installing Docker on VPS..."
ssh "${VPS_USER}@${VPS_IP}" bash -s << 'INSTALL_DOCKER'
set -euo pipefail

if command -v docker &>/dev/null; then
    echo "Docker already installed: $(docker --version)"
else
    echo "Installing Docker..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$USER"
    echo "Docker installed successfully."
fi
INSTALL_DOCKER

# --- Step 2: Upload deployment files ---
echo ""
echo "[2/4] Uploading deployment files..."
ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${REMOTE_DIR}/config ${REMOTE_DIR}/addons"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

scp "${SCRIPT_DIR}/docker-compose.yml" "${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/"
scp "${SCRIPT_DIR}/.env" "${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/"
scp "${SCRIPT_DIR}/config/odoo.conf" "${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/config/"

# Sync custom addons (excludes pyc/cache)
echo "Syncing custom addons..."
rsync -az --delete \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    "${REPO_ROOT}/addons/" "${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/addons/"
echo "Files uploaded."

# --- Step 3: Start Odoo ---
echo ""
echo "[3/4] Starting Odoo containers..."
: "${SUDO_PASS:?Set SUDO_PASS env var with VPS sudo password before running}"
ssh "${VPS_USER}@${VPS_IP}" "SUDO_PASS='${SUDO_PASS}' bash -s" << 'REMOTE_START'
set -euo pipefail
cd /home/baotrung/odoo-deploy
SUDO() { echo "$SUDO_PASS" | sudo -S -p '' "$@"; }
SUDO docker compose pull
SUDO docker compose up -d
echo "Waiting for Odoo to start..."
sleep 10
SUDO docker compose ps

# Upgrade project_scrum if database exists
if SUDO docker compose exec -T db psql -U odoo -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw odoo_erp; then
    echo "Upgrading project_scrum module on odoo_erp..."
    SUDO docker compose exec -T odoo odoo -d odoo_erp -u project_scrum --stop-after-init --no-http || true
    SUDO docker compose restart odoo
fi
REMOTE_START

# --- Step 4: Verify ---
echo ""
echo "[4/4] Verifying deployment..."
ssh "${VPS_USER}@${VPS_IP}" bash -s << VERIFY
set -euo pipefail
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 | grep -q "200\|303"; then
    echo "Odoo is running at http://${VPS_IP}:8069"
else
    echo "Odoo may still be starting. Check: docker compose -f ${REMOTE_DIR}/docker-compose.yml logs -f odoo"
fi
VERIFY

echo ""
echo "=== Deployment Complete ==="
echo "Access Odoo: http://${VPS_IP}:8069"
echo "SSH into VPS: ssh ${VPS_USER}@${VPS_IP}"
echo "View logs: ssh ${VPS_USER}@${VPS_IP} 'cd ${REMOTE_DIR} && docker compose logs -f'"
