#!/bin/bash
# Setup script for openclaw-browser-login
# Run this once after installing the skill

echo "Configuring OpenClaw browser..."

openclaw config set browser.enabled true
openclaw config set tools.profile '"full"'

echo ""
echo "✅ Browser enabled."
echo ""
echo "Next steps:"
echo "1. Start your gateway (if not already running)"
echo "2. In TG, tell your agent: '打开 x.com' (or any site)"
echo "3. Log in to your accounts in the Chrome window that appears"
echo "4. Done! Your agent can now operate those platforms."
