#!/bin/bash
# Fix Playwright dependencies on Ubuntu 24.10 (Plucky)
# Run with: sudo bash fix_ubuntu_deps.sh

echo "=========================================="
echo "Playwright Dependencies Fix for Ubuntu 24.10+"
echo "=========================================="
echo ""

# Check Ubuntu version
echo "[*] Checking Ubuntu version..."
lsb_release -a
echo ""

# Install available dependencies manually
echo "[*] Installing available system dependencies..."
sudo apt-get update

sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    xdg-utils

echo ""
echo "[*] Checking for libicu..."
apt-cache search libicu | grep "^libicu"

# Try to find and link the available libicu version
ICU_VERSION=$(apt-cache search "^libicu[0-9]+" | grep -oP 'libicu\K[0-9]+' | sort -n | tail -1)

if [ -n "$ICU_VERSION" ]; then
    echo "[*] Found libicu$ICU_VERSION, installing..."
    sudo apt-get install -y libicu$ICU_VERSION

    # Create symbolic link if libicu74 is not found
    if [ ! -f "/usr/lib/x86_64-linux-gnu/libicuuc.so.74" ]; then
        echo "[*] Creating symbolic links for libicu74..."
        sudo ln -sf /usr/lib/x86_64-linux-gnu/libicuuc.so.$ICU_VERSION /usr/lib/x86_64-linux-gnu/libicuuc.so.74 2>/dev/null || true
        sudo ln -sf /usr/lib/x86_64-linux-gnu/libicui18n.so.$ICU_VERSION /usr/lib/x86_64-linux-gnu/libicui18n.so.74 2>/dev/null || true
        sudo ln -sf /usr/lib/x86_64-linux-gnu/libicudata.so.$ICU_VERSION /usr/lib/x86_64-linux-gnu/libicudata.so.74 2>/dev/null || true
    fi
else
    echo "[!] No libicu version found, Chromium might still work without it"
fi

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Try running: python main.py"
echo "2. If you still get errors, try: PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 pip install playwright"
echo ""
