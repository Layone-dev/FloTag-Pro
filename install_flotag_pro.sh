#!/bin/bash
echo "🎵 Installation de FlowTag Pro"
echo "=============================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
else
    echo "✅ Python trouvé"
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "🌐 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement
source venv/bin/activate

# Installer les packages
echo "📦 Installation des packages..."
pip install --upgrade pip
pip install customtkinter==5.2.2
pip install pillow==10.2.0
pip install python-dotenv==1.0.0
pip install mutagen==1.47.0
pip install spotipy==2.23.0
pip install discogs-client==2.3.0
pip install openai==1.12.0
pip install requests==2.31.0
pip install aiohttp==3.9.3

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour lancer l'app : python main.py"
