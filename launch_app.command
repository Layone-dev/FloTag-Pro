#!/bin/bash

# FloTag Pro - Script de lancement
# Double-cliquez sur ce fichier pour lancer l'application

echo "🎵 ===== FloTag Pro ===== 🎵"
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Répertoire de travail : $SCRIPT_DIR"
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur : Python 3 n'est pas installé"
    echo "Veuillez installer Python 3 depuis https://python.org"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Python trouvé : $(python3 --version)"

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Erreur : Environnement virtuel non trouvé"
    echo "Veuillez d'abord exécuter le script d'installation"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Environnement virtuel trouvé"

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que les dépendances sont installées
if ! python -c "import customtkinter" &> /dev/null; then
    echo "❌ Erreur : Dépendances manquantes"
    echo "Installation des dépendances..."
    pip install -r requirements.txt
fi

echo "✅ Dépendances vérifiées"
echo ""

# Lancer l'application
echo "🚀 Lancement de FloTag Pro..."
echo ""

# Exécuter l'application
python main.py

# Attendre avant de fermer (en cas d'erreur)
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ L'application s'est fermée avec une erreur"
    read -p "Appuyez sur Entrée pour fermer..."
fi 