# 🔧 Fix Ubuntu 24.10 (Plucky) - Playwright Dependencies

## Problèmes Courants

### 1. Erreur `libicu74` manquant

Ubuntu 24.10 n'est pas officiellement supporté par Playwright, et le package `libicu74` n'existe pas sur cette version.

### 2. Erreur `ImportError: playwright_stealth`

Le package `playwright-stealth` peut avoir des problèmes de compatibilité. **Bonne nouvelle** : il n'est plus requis ! Le bot utilise maintenant une configuration stealth native si ce package n'est pas disponible.

## ✅ Solution Rapide

### Option 1 : Installation manuelle des dépendances (Recommandé)

```bash
# 1. Télécharger le script de fix
cd ~/SpyBot

# 2. Rendre le script exécutable
chmod +x fix_ubuntu_deps.sh

# 3. Exécuter avec sudo
sudo bash fix_ubuntu_deps.sh
```

### Option 2 : Installation manuelle étape par étape

```bash
# Installer toutes les dépendances disponibles
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

# Vérifier quelle version de libicu est disponible
apt-cache search libicu | grep "^libicu"

# Installer la version disponible (probablement libicu75 ou libicu76)
sudo apt-get install -y libicu75  # Ou libicu76, selon ce qui est disponible

# Créer des liens symboliques pour libicu74 (si nécessaire)
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicuuc.so.75 /usr/lib/x86_64-linux-gnu/libicuuc.so.74
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicui18n.so.75 /usr/lib/x86_64-linux-gnu/libicui18n.so.74
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicudata.so.75 /usr/lib/x86_64-linux-gnu/libicudata.so.74
```

### Option 3 : Ignorer l'erreur et tester quand même

Dans la plupart des cas, **Chromium fonctionnera quand même** même si `playwright install-deps` échoue. Essayez simplement de lancer le bot :

```bash
python main.py
```

Si ça fonctionne, vous n'avez rien d'autre à faire !

## 🧪 Tester l'installation

```bash
# Test simple
python test_scraper.py
```

Si le navigateur se lance et vous voyez des deals, c'est que ça fonctionne !

## 🐛 Erreurs possibles

### "libicuuc.so.74: cannot open shared object file"

**Solution :** Créer les liens symboliques manuellement

```bash
# Trouver la version installée
ls /usr/lib/x86_64-linux-gnu/libicuuc.so.*

# Créer le lien (remplacer 75 par votre version)
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicuuc.so.75 /usr/lib/x86_64-linux-gnu/libicuuc.so.74
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicui18n.so.75 /usr/lib/x86_64-linux-gnu/libicui18n.so.74
sudo ln -sf /usr/lib/x86_64-linux-gnu/libicudata.so.75 /usr/lib/x86_64-linux-gnu/libicudata.so.74

# Mettre à jour le cache
sudo ldconfig
```

### "Browser closed unexpectedly"

**Solution :** Vérifier la mémoire disponible

```bash
# Vérifier la RAM
free -h

# Si < 500MB, créer un swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### "Failed to launch the browser"

**Solution :** Installer les dépendances manquantes

```bash
# Lancer Chromium manuellement pour voir l'erreur exacte
~/.cache/ms-playwright/chromium-1194/chrome-linux/chrome --version

# Installer ce qui manque selon l'erreur
```

## 📦 Alternative : Docker (Si tout échoue)

Si les dépendances ne fonctionnent vraiment pas, utilisez Docker :

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium || true

COPY . .
CMD ["python", "main.py"]
```

## ✅ Vérification finale

```bash
# 1. Python fonctionne
python --version

# 2. Playwright installé
python -c "from playwright.sync_api import sync_playwright; print('OK')"

# 3. Chromium téléchargé
ls ~/.cache/ms-playwright/chromium-*/

# 4. Test complet
python test_scraper.py
```

## 📞 Besoin d'aide ?

Si rien ne fonctionne, collectez ces informations et ouvrez une issue :

```bash
# Version Ubuntu
lsb_release -a

# Version Python
python --version

# Versions installées
pip list | grep playwright

# Dépendances système
dpkg -l | grep libicu

# Test manuel Chromium
~/.cache/ms-playwright/chromium-*/chrome-linux/chrome --version 2>&1
```

---

**TL;DR :** Dans 90% des cas, ignorez juste l'erreur `libicu74` et lancez `python main.py`. Ça marchera quand même ! 🎉
