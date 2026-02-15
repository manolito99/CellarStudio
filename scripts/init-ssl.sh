#!/bin/bash
set -euo pipefail

# ============================================================
# SSL initialization script for Let's Encrypt + Docker
# Run once after first deploy to obtain certificates
# ============================================================

DOMAIN="cellarbarberstudio.com"
EMAIL="admin@cellarbarberstudio.com"
COMPOSE_FILE="/home/ubuntu/CellarStudio/docker-compose.prod.yml"

cd /home/ubuntu/CellarStudio

echo "==> Step 1: Creating dummy certificate so nginx can start..."
docker compose -f "$COMPOSE_FILE" run --rm --entrypoint "" certbot sh -c "
  mkdir -p /etc/letsencrypt/live/$DOMAIN
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj '/CN=localhost'
"

echo "==> Step 2: Starting nginx with dummy certificate..."
docker compose -f "$COMPOSE_FILE" up -d nginx

echo "==> Step 3: Waiting for nginx to be ready..."
sleep 5

echo "==> Step 4: Removing dummy certificate..."
docker compose -f "$COMPOSE_FILE" run --rm --entrypoint "" certbot sh -c "
  rm -rf /etc/letsencrypt/live/$DOMAIN
  rm -rf /etc/letsencrypt/archive/$DOMAIN
  rm -f /etc/letsencrypt/renewal/$DOMAIN.conf
"

echo "==> Step 5: Requesting real certificate from Let's Encrypt..."
docker compose -f "$COMPOSE_FILE" run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN"

echo "==> Step 6: Reloading nginx with real certificate..."
docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload

echo ""
echo "============================================"
echo "  SSL setup complete!"
echo "  https://$DOMAIN should now work"
echo "============================================"
echo ""
echo "To auto-renew, add this cron job:"
echo "  0 3 * * * cd /home/ubuntu/CellarStudio && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload"
echo ""
