#!/usr/bin/env python3
"""
Point d'entrée principal pour FlowTag Pro
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importer et lancer l'app
        from ui.flowtag_pro_app import FlowTagProApp
        
        print("🎵 Lancement de FlowTag Pro...")
        app = FlowTagProApp()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("\nVérifiez que tous les packages sont installés")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()