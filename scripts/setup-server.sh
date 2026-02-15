#!/bin/bash
set -euo pipefail

# ============================================================
# Setup script for Oracle Cloud Free Tier VM (Ubuntu)
# Run once: scp this file to the VM and execute it
#   scp scripts/setup-server.sh ubuntu@143.47.45.225:~
#   ssh ubuntu@143.47.45.225 'chmod +x setup-server.sh && ./setup-server.sh'
# ============================================================

REPO_URL="https://github.com/manolito99/CellarStudio.git"
APP_DIR="/home/ubuntu/CellarStudio"

echo "==> Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# --- Install Docker ---
echo "==> Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ubuntu user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker ubuntu

# --- Open firewall ports (Oracle Cloud iptables) ---
echo "==> Opening firewall ports 80 and 443..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save

# --- Clone repository ---
echo "==> Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "Directory $APP_DIR already exists, pulling latest..."
    cd "$APP_DIR" && git pull
else
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# --- Create .env from example ---
if [ ! -f "$APP_DIR/.env" ]; then
    echo "==> Creating .env from .env.example..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo ""
    echo "!!! IMPORTANT: Edit $APP_DIR/.env with production values !!!"
    echo "    nano $APP_DIR/.env"
    echo ""
fi

# --- First deploy ---
echo "==> Building and starting services..."
cd "$APP_DIR"
# newgrp docker is needed because the group change hasn't taken effect yet
sudo docker compose -f docker-compose.prod.yml up --build -d

echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with production values:"
echo "     nano $APP_DIR/.env"
echo "  2. Open port 80 in Oracle Cloud Security List (web console)"
echo "  3. Configure GitHub Secrets (SSH_HOST, SSH_USER, SSH_KEY)"
echo "  4. Restart after .env changes:"
echo "     cd $APP_DIR && docker compose -f docker-compose.prod.yml up --build -d"
echo ""
echo "Check status: docker compose -f docker-compose.prod.yml ps"
echo "View logs:    docker compose -f docker-compose.prod.yml logs -f"
echo ""
