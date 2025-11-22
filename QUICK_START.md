# 🚀 Quick Start Guide

Guide de démarrage rapide pour lancer le bot en 5 minutes.

## Installation Rapide

### Windows

```bash
# 1. Installer Python 3.10+
# Télécharger depuis python.org

# 2. Ouvrir PowerShell dans le dossier du projet
cd path\to\MeetTheSpy

# 3. Créer l'environnement virtuel
python -m venv venv

# 4. Activer l'environnement
venv\Scripts\activate

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Installer Playwright Chromium
playwright install chromium
```

### Linux/Mac

```bash
# 1. Ouvrir le terminal dans le dossier du projet
cd /path/to/MeetTheSpy

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Installer Playwright
playwright install chromium
playwright install-deps  # Installe les dépendances système
```

## Configuration

### 1. Créer le fichier .env

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec votre éditeur préféré
nano .env  # ou vim, code, notepad, etc.
```

### 2. Obtenir le Token Discord

1. Aller sur https://discord.com/developers/applications
2. Cliquer "New Application"
3. Donner un nom (ex: "Price Monitor")
4. Aller dans l'onglet "Bot"
5. Cliquer "Add Bot"
6. **Activer "Message Content Intent"** (important !)
7. Cliquer "Reset Token" et copier le token
8. Coller dans `.env` : `DISCORD_TOKEN=votre_token_ici`

### 3. Obtenir l'ID du Channel

1. Dans Discord, activer le Mode Développeur :
   - Paramètres > Avancés > Mode Développeur ✅
2. Clic droit sur votre channel > "Copier l'identifiant"
3. Coller dans `.env` : `DISCORD_CHANNEL_ID=123456789`

### 4. Inviter le Bot

Remplacer `CLIENT_ID` par votre Application ID :

```
https://discord.com/api/oauth2/authorize?client_id=1441716678181519382&permissions=51200&scope=bot
```

Permissions requises :
- ✅ Send Messages
- ✅ Embed Links
- ✅ Attach Files

## Premier Test

### Test 1 : Scraper (Sans Discord)

```bash
# Mode visible (voir le navigateur)
HEADLESS_MODE=false python test_scraper.py
```

Si ça fonctionne, vous verrez les deals extraits de Keepa.

### Test 2 : Discord (Sans Scraper)

```bash
python test_discord.py
```

Vérifiez votre channel Discord, vous devriez voir 5 deals de test.

## Lancement Production

### Méthode 1 : Ligne de commande

```bash
python main.py
```

### Méthode 2 : Scripts de démarrage

**Windows :**
```bash
run.bat
```

**Linux/Mac :**
```bash
chmod +x run.sh
./run.sh
```

## Cookies Cloudflare (Si nécessaire)

Si Keepa bloque le bot :

```bash
python extract_cookies.py
```

1. Une fenêtre de navigateur s'ouvre
2. Résolvez le challenge Cloudflare
3. Appuyez sur ENTRÉE
4. Les cookies sont sauvegardés dans `cookies.json`
5. Activez dans `.env` : `USE_COOKIES=true`

## Troubleshooting

### Le bot ne se connecte pas à Discord

- ❌ Token invalide → Vérifier `DISCORD_TOKEN` dans `.env`
- ❌ Permissions manquantes → Réinviter le bot avec le bon lien
- ❌ Channel introuvable → Vérifier `DISCORD_CHANNEL_ID`

### Le scraper ne trouve rien

- ⚠️ Cloudflare bloque → Utiliser `extract_cookies.py`
- ⚠️ Seuil trop élevé → Réduire `MIN_DISCOUNT_PERCENT` (ex: 30)
- ⚠️ Page a changé → Activer `DEBUG=true` et vérifier les logs

### Erreur "playwright not found"

```bash
playwright install chromium
```

### Erreur "Module not found"

```bash
pip install -r requirements.txt
```

## Configuration Avancée

### Changer l'intervalle de scan

Dans `.env` :
```env
SCRAPER_INTERVAL=300  # secondes (5 minutes par défaut)
```

### Changer le seuil de réduction

```env
MIN_DISCOUNT_PERCENT=30  # % (40% par défaut)
```

### Activer les logs détaillés

```env
DEBUG=true
```

## Déploiement 24/7

### VPS Linux (Recommandé)

1. Louer un VPS (OVH, Scaleway, DigitalOcean...)
2. Se connecter en SSH
3. Installer le bot (voir README.md section Déploiement)
4. Créer un service systemd
5. Le bot tourne H24 même si vous fermez le terminal

### PC Local (Simple)

**Windows :** Laisser le terminal ouvert

**Linux/Mac :** Utiliser `screen` ou `tmux`

```bash
# Avec screen
screen -S pricebot
python main.py
# Ctrl+A puis D pour détacher
# Pour revenir : screen -r pricebot
```

## Structure des Fichiers

```
MeetTheSpy/
├── main.py              ← Point d'entrée principal
├── bot.py               ← Bot Discord
├── scraper.py           ← Scraper Keepa
├── cache.py             ← Cache anti-doublon
├── .env                 ← Configuration (à créer)
├── requirements.txt     ← Dépendances Python
├── test_scraper.py      ← Test du scraper
├── test_discord.py      ← Test du bot Discord
├── extract_cookies.py   ← Outil d'extraction cookies
├── run.bat / run.sh     ← Scripts de démarrage
└── README.md            ← Documentation complète
```

## Commandes Utiles

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Voir les logs en direct
tail -f price_monitor.log  # Linux/Mac
Get-Content price_monitor.log -Wait  # Windows PowerShell

# Arrêter le bot
Ctrl+C

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade
```

## Besoin d'aide ?

📖 Lire le [README.md](README.md) complet

🐛 Ouvrir une issue sur GitHub

💬 Rejoindre le Discord du projet

---

**Bon monitoring ! 🚀**
