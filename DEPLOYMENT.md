# 🚀 Guide de Déploiement en Production

Guide complet pour déployer le bot Amazon Price Monitor sur un serveur Linux 24/7.

## 🎯 Prérequis

- VPS/Serveur Linux (Ubuntu 20.04/22.04 ou Debian 11+ recommandé)
- Accès SSH au serveur
- 1 GB RAM minimum
- 10 GB espace disque
- Python 3.10+

> ⚠️ **IMPORTANT - Ubuntu 24.10+** : Si vous utilisez Ubuntu 24.10 (Plucky) ou une version plus récente, vous rencontrerez des problèmes avec `playwright install-deps`. Consultez [UBUNTU_FIX.md](UBUNTU_FIX.md) pour les solutions. Dans la plupart des cas, vous pouvez **ignorer l'erreur et le bot fonctionnera quand même**.

## 📦 Fournisseurs VPS Recommandés

- **OVH** : À partir de 3.50€/mois (VPS Starter)
- **Scaleway** : À partir de 0.01€/heure (DEV1-S)
- **DigitalOcean** : À partir de 4$/mois (Droplet Basic)
- **Hetzner** : À partir de 4.15€/mois (CX11)

## 🔧 Installation sur Ubuntu/Debian

### 1. Connexion au serveur

```bash
ssh user@your-server-ip
```

### 2. Mise à jour du système

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Installation de Python et dépendances

```bash
# Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# Dépendances système pour Playwright
sudo apt install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

### 4. Création d'un utilisateur dédié (Recommandé)

```bash
# Créer utilisateur
sudo useradd -m -s /bin/bash pricebot

# Passer à l'utilisateur
sudo su - pricebot
```

### 5. Cloner le projet

```bash
cd ~
git clone https://github.com/your-repo/MeetTheSpy.git
cd MeetTheSpy
```

Ou si vous uploadez manuellement :

```bash
# Sur votre PC local
scp -r MeetTheSpy/ user@server-ip:~/

# Sur le serveur
cd ~/MeetTheSpy
```

### 6. Installation Python

```bash
# Créer environnement virtuel
python3 -m venv venv

# Activer
source venv/bin/activate

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Installer Playwright
playwright install chromium
playwright install-deps
# Note: Si 'install-deps' échoue sur Ubuntu 24.10+, c'est normal - voir ci-dessous
```

#### 🔧 Fix pour Ubuntu 24.10+ (Si install-deps échoue)

Si vous obtenez l'erreur `Unable to locate package libicu74`, ne paniquez pas ! Deux options :

**Option A - Ignorer l'erreur (Recommandé)**

Le bot fonctionnera probablement quand même. Passez directement à l'étape suivante et testez.

**Option B - Installer manuellement**

```bash
# Exécuter le script de fix
chmod +x fix_ubuntu_deps.sh
sudo bash fix_ubuntu_deps.sh
```

Consultez [UBUNTU_FIX.md](UBUNTU_FIX.md) pour plus de détails.

### 7. Configuration

```bash
# Copier le fichier de config
cp .env.example .env

# Éditer la configuration
nano .env
```

Remplir au minimum :
```env
DISCORD_TOKEN=your_actual_token
DISCORD_CHANNEL_ID=your_channel_id
HEADLESS_MODE=true
```

### 8. Test de fonctionnement

```bash
# Test rapide
python test_scraper.py
```

Si tout fonctionne, passez à la configuration systemd.

## 🔄 Configuration Systemd (Démarrage automatique)

### 1. Créer le fichier service

```bash
sudo nano /etc/systemd/system/price-monitor.service
```

Contenu (ajuster les chemins) :

```ini
[Unit]
Description=Amazon Price Monitor Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pricebot
Group=pricebot
WorkingDirectory=/home/pricebot/MeetTheSpy
Environment="PATH=/home/pricebot/MeetTheSpy/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pricebot/MeetTheSpy/venv/bin/python main.py

Restart=always
RestartSec=10
StartLimitInterval=5min
StartLimitBurst=4

StandardOutput=journal
StandardError=journal
SyslogIdentifier=price-monitor

[Install]
WantedBy=multi-user.target
```

### 2. Activer et démarrer le service

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer au démarrage
sudo systemctl enable price-monitor

# Démarrer le service
sudo systemctl start price-monitor

# Vérifier le statut
sudo systemctl status price-monitor
```

### 3. Commandes de gestion

```bash
# Démarrer
sudo systemctl start price-monitor

# Arrêter
sudo systemctl stop price-monitor

# Redémarrer
sudo systemctl restart price-monitor

# Voir les logs
sudo journalctl -u price-monitor -f

# Voir les dernières 100 lignes
sudo journalctl -u price-monitor -n 100

# Logs depuis aujourd'hui
sudo journalctl -u price-monitor --since today
```

## 📊 Monitoring et Logs

### Logs en temps réel

```bash
# Avec journalctl
sudo journalctl -u price-monitor -f

# Ou le fichier log local
tail -f /home/pricebot/MeetTheSpy/price_monitor.log
```

### Vérifier que le bot tourne

```bash
# Statut du service
sudo systemctl status price-monitor

# Processus Python
ps aux | grep main.py

# Processus Chromium
ps aux | grep chromium
```

## 🔒 Sécurité

### Firewall UFW

```bash
# Installer UFW
sudo apt install ufw

# Autoriser SSH
sudo ufw allow 22/tcp

# Activer le firewall
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

### Mises à jour automatiques

```bash
# Installer unattended-upgrades
sudo apt install unattended-upgrades

# Activer
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Fail2Ban (Protection SSH)

```bash
# Installer
sudo apt install fail2ban

# Activer
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🔄 Mise à jour du bot

### Méthode 1 : Git Pull

```bash
# Se connecter au serveur
ssh pricebot@server-ip

# Aller dans le dossier
cd ~/MeetTheSpy

# Pull les changements
git pull

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Redémarrer le service
sudo systemctl restart price-monitor

# Vérifier les logs
sudo journalctl -u price-monitor -f
```

### Méthode 2 : Upload manuel

```bash
# Sur votre PC
scp main.py pricebot@server-ip:~/MeetTheSpy/
scp scraper.py pricebot@server-ip:~/MeetTheSpy/
scp bot.py pricebot@server-ip:~/MeetTheSpy/

# Sur le serveur
sudo systemctl restart price-monitor
```

## 🍪 Cookies Cloudflare sur serveur

Si vous devez extraire les cookies sur un serveur sans interface graphique :

### Option 1 : Extraire en local puis uploader

```bash
# Sur votre PC local
python extract_cookies.py
# Résoudre le CAPTCHA

# Uploader vers le serveur
scp cookies.json pricebot@server-ip:~/MeetTheSpy/
```

### Option 2 : X11 Forwarding (Avancé)

```bash
# Se connecter avec X11
ssh -X pricebot@server-ip

# Lancer l'extraction
cd ~/MeetTheSpy
source venv/bin/activate
python extract_cookies.py
# Une fenêtre s'ouvrira sur votre PC
```

### Option 3 : Copier depuis le navigateur

1. Installer l'extension Cookie-Editor
2. Visiter Keepa.com et résoudre le CAPTCHA
3. Exporter les cookies en JSON
4. Créer le fichier sur le serveur :

```bash
nano ~/MeetTheSpy/cookies.json
# Coller le contenu JSON
```

Puis activer dans `.env` :
```env
USE_COOKIES=true
```

## 📈 Optimisation des performances

### Réduire l'utilisation mémoire

Dans `.env` :
```env
HEADLESS_MODE=true  # Important !
SCRAPER_INTERVAL=600  # Augmenter l'intervalle
```

### Limitation des ressources systemd

Dans `/etc/systemd/system/price-monitor.service`, ajouter :

```ini
[Service]
MemoryMax=500M
CPUQuota=50%
```

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Voir les erreurs
sudo journalctl -u price-monitor -n 50

# Vérifier les permissions
ls -la /home/pricebot/MeetTheSpy/

# Tester manuellement
sudo su - pricebot
cd ~/MeetTheSpy
source venv/bin/activate
python main.py
```

### Chromium crash

Vérifier la mémoire disponible :
```bash
free -h
```

Si < 500MB libre, augmenter le swap :

```bash
# Créer un fichier swap de 2GB
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendre permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### "Permission denied"

```bash
# Ajuster les permissions
sudo chown -R pricebot:pricebot /home/pricebot/MeetTheSpy

# Rendre les scripts exécutables
chmod +x /home/pricebot/MeetTheSpy/run.sh
```

## 📋 Checklist Post-Déploiement

- [ ] Le service démarre automatiquement au boot
- [ ] Les logs montrent une activité normale
- [ ] Le bot poste dans Discord
- [ ] Les deals sont bien filtrés
- [ ] Pas de crash toutes les 5 minutes
- [ ] La mémoire reste stable
- [ ] Les cookies fonctionnent (si nécessaire)
- [ ] Le firewall est configuré
- [ ] SSH sécurisé (clé SSH, fail2ban)
- [ ] Backups configurés

## 🔐 Backup de la configuration

```bash
# Backup .env et cookies
scp pricebot@server-ip:~/MeetTheSpy/.env ./backup-env
scp pricebot@server-ip:~/MeetTheSpy/cookies.json ./backup-cookies.json
```

## 📊 Supervision (Optionnel)

### Avec cron pour check de santé

```bash
crontab -e
```

Ajouter :
```bash
# Vérifier toutes les heures
0 * * * * systemctl is-active price-monitor || systemctl restart price-monitor
```

### Notification en cas de crash

Créer `/home/pricebot/check-bot.sh` :

```bash
#!/bin/bash
if ! systemctl is-active --quiet price-monitor; then
    echo "Price Monitor is down!" | mail -s "Bot Alert" your@email.com
    systemctl restart price-monitor
fi
```

Ajouter au cron :
```bash
*/15 * * * * /home/pricebot/check-bot.sh
```

## 🎉 C'est terminé !

Votre bot tourne maintenant 24/7 sur votre serveur.

**Commandes utiles au quotidien :**

```bash
# Voir les logs en direct
sudo journalctl -u price-monitor -f

# Redémarrer le bot
sudo systemctl restart price-monitor

# Vérifier le statut
sudo systemctl status price-monitor
```

---

**Besoin d'aide ? Ouvrez une issue sur GitHub.**
