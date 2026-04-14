#!/bin/bash
# update-tunnel-url.sh
# Called when the Cloudflare tunnel URL changes
# Updates vercel.json and redeploys the frontend

set -e

FRONTEND_DIR="/home/claw/.openclaw/workspace/projects/contentforge-ai/src/frontend"
TUNNEL_URL_FILE="/home/claw/.cloudflared/tunnel-url"
VERCEL_JSON="$FRONTEND_DIR/vercel.json"

if [ ! -f "$TUNNEL_URL_FILE" ]; then
    echo "No tunnel URL file found"
    exit 1
fi

TUNNEL_URL=$(cat "$TUNNEL_URL_FILE")

# Update vercel.json
cat > "$VERCEL_JSON" << EOF
{
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "${TUNNEL_URL}/api/v1/:path*"
    }
  ]
}
EOF

echo "Updated vercel.json with tunnel URL: $TUNNEL_URL"

# Update CORS on backend
BACKEND_ENV="/home/claw/.openclaw/workspace/projects/contentforge-ai/src/backend/.env.staging"
# Extract the domain from the tunnel URL
TUNNEL_DOMAIN=$(echo "$TUNNEL_URL" | sed 's|https://||' | cut -d'/' -f1)

# Update CORS_ORIGINS in .env.staging
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=[\"http://localhost:3000\",\"https://frontend-theta-seven-65.vercel.app\",\"https://${TUNNEL_DOMAIN}\"]|" "$BACKEND_ENV"

# Restart backend with new CORS
systemctl --user restart contentforge-backend

# Git commit and push
cd "/home/claw/.openclaw/workspace/projects/contentforge-ai"
git add -A
git commit -m "chore: update tunnel URL to $TUNNEL_URL" || true
git push origin main

# Redeploy frontend
cd "$FRONTEND_DIR"
vercel --prod --yes

echo "Frontend redeployed with new tunnel URL"