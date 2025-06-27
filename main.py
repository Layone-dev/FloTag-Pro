#!/usr/bin/env python3
"""
FloTag Pro - Application de tagging musical optimisée pour Serato DJ
Point d'entrée principal
"""

import sys
import os
from pathlib import Path

# Configuration des variables d'environnement si .env existe
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

from FlowTag_Pro.ui.flotag_pro_app import FloTagProApp


def main():
    # Vérifier les APIs
    print("=== FloTag Pro ===")
    print("État des APIs:")
    print(f"- Spotify: {'✅' if os.getenv('SPOTIFY_CLIENT_ID') else '⚠️  Non configuré'}")
    print(f"- Discogs: {'✅' if os.getenv('DISCOGS_TOKEN') else '⚠️  Non configuré'}")
    print(f"- OpenAI:  {'✅' if os.getenv('OPENAI_API_KEY') else '⚠️  Non configuré'}")
    print("\nLancement...\n")
    
    # Lancer l'app
    app = FloTagProApp()
    app.mainloop()


if __name__ == "__main__":
    main() 