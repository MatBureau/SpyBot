# 🤖 Amazon Price Monitor Bot

Bot Discord autonome qui surveille les erreurs de prix sur Amazon France en temps réel via le scraping de Keepa.com.

## 📋 Fonctionnalités

- ✅ Scraping automatique de Keepa.com (Deals France)
- ✅ Détection des baisses de prix > 40% (configurable)
- ✅ Messages Discord riches avec embeds et graphiques Keepa
- ✅ Boutons d'action rapide (BuyBox, Lookup, Keepa)
- ✅ Cache intelligent pour éviter les doublons (24h)
- ✅ Gestion automatique des erreurs et redémarrages
- ✅ Mode furtif avec Playwright Stealth
- ✅ Support des cookies Cloudflare

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Compte Discord avec un bot créé
- Un serveur Discord où poster les deals

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone <repo-url>
cd MeetTheSpy
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Installer Playwright Chromium**

```bash
playwright install chromium
```

5. **Configurer les variables d'environnement**

Copier `.env.example` vers `.env` et remplir vos valeurs :

```bash
cp .env.example .env
```

Éditer `.env` :

```env
DISCORD_TOKEN=votre_token_discord_bot
DISCORD_CHANNEL_ID=id_du_channel_discord
```

### 📝 Obtenir le Token Discord

1. Aller sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créer une nouvelle application
3. Aller dans "Bot" > "Add Bot"
4. Copier le Token
5. Activer les "Privileged Gateway Intents" (Message Content Intent)
6. Inviter le bot sur votre serveur avec les permissions :
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History

URL d'invitation (remplacer CLIENT_ID) :
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=51200&scope=bot
```

### 🔑 Obtenir l'ID du Channel Discord

1. Activer le Mode Développeur dans Discord (Paramètres > Avancés > Mode développeur)
2. Clic droit sur le channel souhaité > Copier l'identifiant

## 🍪 Configuration des Cookies (Optionnel)

Si Keepa est protégé par Cloudflare, vous devrez fournir des cookies valides.

### Méthode 1 : Extension de navigateur (Recommandé)

1. Installer l'extension [Cookie-Editor](https://cookie-editor.cgagnier.ca/)
2. Visiter https://keepa.com et compléter le challenge Cloudflare
3. Cliquer sur l'extension > Export > JSON
4. Sauvegarder le contenu dans `cookies.json`

### Méthode 2 : DevTools Chrome

1. Visiter https://keepa.com
2. Ouvrir DevTools (F12) > Application > Cookies
3. Copier les cookies `cf_clearance` et autres cookies Keepa
4. Créer `cookies.json` selon le format de `cookies.json.example`

### Méthode 3 : Script Python (Automatique)

```python
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Visitez Keepa et résolvez le challenge manuellement
    page.goto("https://keepa.com")
    input("Appuyez sur Entrée après avoir résolu le CAPTCHA...")

    # Sauvegardez les cookies
    cookies = context.cookies()
    with open("cookies.json", "w") as f:
        json.dump(cookies, f, indent=2)

    browser.close()
    print("Cookies sauvegardés dans cookies.json")
```

Activez ensuite les cookies dans `.env` :

```env
USE_COOKIES=true
COOKIES_FILE=cookies.json
```

## ▶️ Lancement

```bash
python main.py
```

Le bot va :
1. Se connecter à Discord
2. Initialiser le navigateur Playwright
3. Commencer à scraper Keepa toutes les 5 minutes (configurable)
4. Poster les deals détectés dans le channel configuré

## 🎛️ Configuration Avancée

Toutes les options dans `.env` :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DISCORD_TOKEN` | Token du bot Discord | **Requis** |
| `DISCORD_CHANNEL_ID` | ID du channel Discord | **Requis** |
| `KEEPA_URL` | URL de la page Keepa Deals | `https://keepa.com/#!deals/4` |
| `SCRAPER_INTERVAL` | Intervalle entre les scans (secondes) | `300` |
| `HEADLESS_MODE` | Navigateur invisible | `true` |
| `MIN_DISCOUNT_PERCENT` | Réduction minimum pour notifier | `40` |
| `CACHE_DURATION_HOURS` | Durée du cache anti-doublon | `24` |
| `USE_COOKIES` | Utiliser les cookies | `false` |
| `COOKIES_FILE` | Fichier de cookies | `cookies.json` |
| `DEBUG` | Mode debug (logs verbeux) | `false` |

## 📊 Logs

Les logs sont écrits dans :
- Console (stdout)
- Fichier `price_monitor.log`

## 🐛 Dépannage

### Le bot ne démarre pas

- Vérifiez que toutes les dépendances sont installées
- Vérifiez que Playwright Chromium est installé : `playwright install chromium`
- Vérifiez les permissions du bot Discord

### Le scraper ne trouve pas de deals

- Vérifiez que l'URL Keepa est correcte
- Activez le mode debug (`DEBUG=true`)
- Essayez en mode non-headless (`HEADLESS_MODE=false`) pour voir le navigateur
- Vérifiez les logs pour les erreurs de parsing

### Cloudflare bloque le bot

- Configurez les cookies (voir section Cookies)
- Vérifiez que `playwright-stealth` est bien installé
- Essayez d'augmenter le délai entre les requêtes

### Les embeds ne s'affichent pas correctement

- Vérifiez que le bot a les permissions "Embed Links"
- Vérifiez que les URLs des images Keepa sont accessibles

## 🏗️ Architecture

```
.
├── main.py           # Point d'entrée, orchestration
├── scraper.py        # Moteur de scraping Playwright
├── bot.py            # Bot Discord et embeds
├── cache.py          # Système de cache anti-doublon
├── requirements.txt  # Dépendances Python
├── .env             # Configuration (à créer)
├── .env.example     # Exemple de configuration
├── cookies.json     # Cookies navigateur (optionnel)
└── price_monitor.log # Fichier de logs
```

## 🔒 Sécurité

⚠️ **Important** : Ne jamais commit les fichiers suivants :
- `.env` (contient votre token Discord)
- `cookies.json` (contient vos cookies de session)
- `price_monitor.log` (peut contenir des données sensibles)

Ajoutez-les à `.gitignore`.

## 📝 Exemple d'Embed Discord

```
╔═══════════════════════════════════════╗
║ 🚨 Price Error Detected - 65% OFF!   ║
║                                       ║
║ Store: Amazon FR                      ║
║ Price: €99.99 → €34.99               ║
║ Discount: -65%                        ║
║ Availability: In Stock                ║
║ ASIN: B08XYZABC12                     ║
║                                       ║
║ [🛒 BuyBox] [🔍 Lookup] [📈 Keepa]   ║
║                                       ║
║ [Graphique Keepa]                     ║
╚═══════════════════════════════════════╝
```

## 🚦 Déploiement en Production

### Sur un serveur Linux (VPS)

1. **Installer les dépendances système**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

2. **Cloner et installer**

```bash
git clone <repo>
cd MeetTheSpy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps  # Dépendances système pour Chromium
```

3. **Créer un service systemd**

Créer `/etc/systemd/system/price-monitor.service` :

```ini
[Unit]
Description=Amazon Price Monitor Bot
After=network.target

[Service]
Type=simple
User=votre_user
WorkingDirectory=/chemin/vers/MeetTheSpy
Environment="PATH=/chemin/vers/MeetTheSpy/venv/bin"
ExecStart=/chemin/vers/MeetTheSpy/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Activer et démarrer**

```bash
sudo systemctl daemon-reload
sudo systemctl enable price-monitor
sudo systemctl start price-monitor
sudo systemctl status price-monitor
```

5. **Voir les logs**

```bash
sudo journalctl -u price-monitor -f
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou une pull request.

## 📄 Licence

MIT License - Libre d'utilisation et de modification.

## ⚠️ Avertissement

Ce bot est fourni à des fins éducatives. L'utilisation intensive de scraping peut violer les Conditions d'Utilisation de Keepa.com. Utilisez-le de manière responsable et respectez les limites de taux.

---

**Développé avec ❤️ par un Senior Python Engineer**
