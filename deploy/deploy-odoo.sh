#!/bin/bash
# Deploy latest Odoo custom addons to existing production stack on VPS
# Usage: SUDO_PASS='xxx' ./deploy-odoo.sh
#
# Assumes production stack already running:
#   - Container:  atin-odoo-app, atin-odoo-db
#   - Compose dir: /root/odoo-deploy/deploy (owned by root)
#   - Addons mount: /root/odoo-deploy/deploy/addons
#   - Database: atin_erp

set -euo pipefail

# --- VPS Configuration ---
VPS_IP="192.168.1.199"
VPS_USER="baotrung"
REMOTE_DIR="/root/odoo-deploy/deploy"
DB_NAME="erp_atin"
MODULE="project_scrum"

: "${SUDO_PASS:?Set SUDO_PASS env var with VPS sudo password before running}"

echo "=== Odoo Code Update ==="
echo "Target: ${VPS_USER}@${VPS_IP} → ${REMOTE_DIR}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Step 1: Sync addons (2-step: rsync to tmp, then sudo move) ---
TMP_DIR="/home/${VPS_USER}/odoo-addons-staging"
echo "[1/3] Staging addons to ${TMP_DIR}..."
ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${TMP_DIR}"
rsync -az --delete \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    "${REPO_ROOT}/addons/" "${VPS_USER}@${VPS_IP}:${TMP_DIR}/"

echo "Syncing staging → ${REMOTE_DIR}/addons with sudo..."
ssh "${VPS_USER}@${VPS_IP}" "SUDO_PASS='${SUDO_PASS}' bash -s" << REMOTE_SYNC
set -euo pipefail
SUDO() { echo "\$SUDO_PASS" | sudo -S -p '' "\$@"; }
SUDO rsync -a --delete ${TMP_DIR}/ ${REMOTE_DIR}/addons/
SUDO chown -R root:root ${REMOTE_DIR}/addons
REMOTE_SYNC
echo "Addons synced."

# --- Step 2: Upgrade module on atin_erp database ---
echo ""
echo "[2/3] Upgrading ${MODULE} on ${DB_NAME}..."
ssh "${VPS_USER}@${VPS_IP}" "SUDO_PASS='${SUDO_PASS}' bash -s" << REMOTE_UPGRADE
set -euo pipefail
SUDO() { echo "\$SUDO_PASS" | sudo -S -p '' "\$@"; }

# Verify DB exists before upgrading
if SUDO docker exec atin-odoo-db psql -U odoo -lqt 2>/dev/null | cut -d \\| -f 1 | grep -qw ${DB_NAME}; then
    echo "Database ${DB_NAME} found. Running module upgrade..."
    SUDO docker exec atin-odoo-app odoo -d ${DB_NAME} -u ${MODULE} --stop-after-init --no-http || {
        echo "WARN: module upgrade returned non-zero (check logs)"
    }
    echo "Restarting atin-odoo-app..."
    SUDO docker restart atin-odoo-app
else
    echo "ERROR: Database ${DB_NAME} not found on atin-odoo-db"
    exit 1
fi
REMOTE_UPGRADE

# --- Step 3: Verify ---
echo ""
echo "[3/3] Verifying deployment..."
sleep 5
ssh "${VPS_USER}@${VPS_IP}" bash -s << VERIFY
set -euo pipefail
code=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 || true)
echo "HTTP status: \$code"
if [[ "\$code" =~ ^(200|303)$ ]]; then
    echo "Odoo is running at http://${VPS_IP}:8069"
else
    echo "Odoo may still be starting. Check: docker logs -f atin-odoo-app"
fi
VERIFY

echo ""
echo "=== Deployment Complete ==="
echo "Access Odoo: http://${VPS_IP}:8069"
echo "View logs: ssh ${VPS_USER}@${VPS_IP} 'sudo docker logs -f atin-odoo-app'"
