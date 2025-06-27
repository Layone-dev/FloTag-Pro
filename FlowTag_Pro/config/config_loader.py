"""
Charge les configurations et clés API pour FlowTag Pro
"""

import os
from pathlib import Path

def load_api_keys():
    """
    Charge les clés API depuis les fichiers dans le répertoire home de l'utilisateur
    et les définit comme variables d'environnement.
    """
    home = Path.home()
    
    # Clé OpenAI
    try:
        with open(home / ".openai_key", "r") as f:
            os.environ['OPENAI_API_KEY'] = f.read().strip()
            print("Clé OpenAI chargée.")
    except FileNotFoundError:
        print("Avertissement: Fichier ~/.openai_key non trouvé.")
    
    # Identifiants Spotify
    try:
        with open(home / ".spotify_credentials", "r") as f:
            creds = f.read().strip().split(':')
            if len(creds) == 2:
                os.environ['SPOTIFY_CLIENT_ID'] = creds[0]
                os.environ['SPOTIFY_CLIENT_SECRET'] = creds[1]
                print("Identifiants Spotify chargés.")
    except FileNotFoundError:
        print("Avertissement: Fichier ~/.spotify_credentials non trouvé.")
        
    # Token Discogs
    try:
        with open(home / ".discogs_token", "r") as f:
            os.environ['DISCOGS_TOKEN'] = f.read().strip()
            print("Token Discogs chargé.")
    except FileNotFoundError:
        print("Avertissement: Fichier ~/.discogs_token non trouvé.") 