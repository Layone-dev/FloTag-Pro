# === 1. config/dj_tags_config.py ===
"""
Configuration des tags DJ pour FlowTag Pro
"""

class DJTagsConfig:
    """Configuration centralisée des tags DJ"""
    
    def __init__(self):
        # Contextes possibles
        self.contexts = [
            'Bar', 'Club', 'Mariage', 'CorporateEvent', 
            'Restaurant', 'Festival', 'Anniversaire', 
            'CocktailChic', 'PoolParty', 'Brunch', 'Cocktail'
        ]
        
        # Moments possibles
        self.moments = [
            'Warmup', 'Peaktime', 'Closing'
        ]
        
        # Styles possibles
        self.styles = [
            'Banger', 'Bootleg', 'Classics', 'Funky', 
            'Ladies', 'Mashup', 'Commercial', 'House', 
            'Techno', 'Deep', 'Progressive', 'Vocal', 
            'Instrumental', 'Uplifting', 'Dark'
        ]
        
        # Mapping énergie vers moment
        self.energy_to_moment = {
            (1, 3): ['Closing'],
            (4, 6): ['Warmup'],
            (7, 10): ['Peaktime']
        }
        
        # Mapping BPM vers contexte suggéré
        self.bpm_to_context = {
            (60, 90): ['Restaurant', 'CocktailChic'],
            (90, 110): ['Bar', 'Brunch'],
            (110, 128): ['Anniversaire', 'Mariage'],
            (128, 140): ['Club', 'Festival'],
            (140, 180): ['Club', 'Festival']
        }


# === 2. services/__init__.py ===
"""
Module services pour FlowTag Pro
"""

from .analysis_orchestrator import AnalysisOrchestrator
from .cache_manager import CacheManager
from .tag_writer import TagWriter

__all__ = ['AnalysisOrchestrator', 'CacheManager', 'TagWriter']


# === 3. ui/__init__.py ===
"""
Module UI pour FlowTag Pro
"""

from .flotag_pro_app import FloTagProApp

__all__ = ['FloTagProApp']


# === 4. data/__init__.py ===
"""
Module data pour FlowTag Pro
"""

from .countries_db import detect_country, FLOWTAG_COUNTRIES
from .genres_db import get_genre_contexts, FLOWTAG_GENRES

__all__ = ['detect_country', 'FLOWTAG_COUNTRIES', 'get_genre_contexts', 'FLOWTAG_GENRES']


# === 5. config/__init__.py ===
"""
Module config pour FlowTag Pro
"""

from .dj_tags_config import DJTagsConfig

__all__ = ['DJTagsConfig']


# === 6. main.py (point d'entrée principal) ===
"""
Point d'entrée principal pour FlowTag Pro
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

# Configuration de l'environnement
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Pas de fichiers .pyc

# Import et lancement de l'application
def main():
    """Lance l'application FlowTag Pro"""
    try:
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importer et lancer l'app
        from FloTag_Pro.ui.flotag_pro_app import FloTagProApp
        
        print("🎵 Lancement de FlowTag Pro...")
        app = FloTagProApp()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("Vérifiez que tous les packages sont installés:")
        print("  pip install customtkinter pillow python-dotenv mutagen spotipy discogs-client openai requests aiohttp")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du lancement : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


# === 7. requirements.txt ===
"""
customtkinter==5.2.2
pillow==10.2.0
python-dotenv==1.0.0
mutagen==1.47.0
spotipy==2.23.0
discogs-client==2.3.0
openai==1.12.0
requests==2.31.0
aiohttp==3.9.3
"""


# === 8. .env.example ===
"""
# Spotify API (https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID=votre_client_id
SPOTIFY_CLIENT_SECRET=votre_client_secret

# Discogs API (https://www.discogs.com/settings/developers)
DISCOGS_TOKEN=votre_token

# OpenAI API (https://platform.openai.com/api-keys)
OPENAI_API_KEY=votre_cle_api
"""


# === 9. launch_app.command (pour Mac) ===
"""
#!/bin/bash
# Script de lancement pour FlowTag Pro sur macOS

# Aller dans le répertoire du script
cd "$(dirname "$0")"

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Lancer l'application
python main.py

# Garder la fenêtre ouverte en cas d'erreur
read -p "Appuyez sur Entrée pour fermer..."
"""


# === 10. ui/settings_dialog.py (dialogue de configuration simple) ===
"""
Dialogue de configuration des APIs
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, current_config: Dict):
        super().__init__(parent)
        
        self.title("Configuration des APIs")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.current_config = current_config
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Instructions
        tk.Label(
            self, 
            text="Configurez vos clés API pour activer toutes les fonctionnalités",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # Frame pour les champs
        fields_frame = tk.Frame(self)
        fields_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Champs de configuration
        self.fields = {}
        configs = [
            ("Spotify Client ID", "spotify_client_id", False),
            ("Spotify Client Secret", "spotify_client_secret", True),
            ("Discogs Token", "discogs_token", True),
            ("OpenAI API Key", "openai_api_key", True)
        ]
        
        for i, (label, key, is_password) in enumerate(configs):
            tk.Label(fields_frame, text=f"{label}:").grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            
            entry = tk.Entry(fields_frame, width=40)
            if is_password:
                entry.config(show="*")
            
            # Pré-remplir avec la valeur actuelle
            if key in self.current_config:
                entry.insert(0, self.current_config[key])
                
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.fields[key] = entry
        
        # Boutons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame, 
            text="Sauvegarder", 
            command=self._save
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame, 
            text="Annuler", 
            command=self.destroy
        ).pack(side="left", padx=5)
        
    def _save(self):
        # Récupérer les valeurs
        self.result = {}
        for key, entry in self.fields.items():
            value = entry.get().strip()
            if value:
                self.result[key] = value
        
        # Sauvegarder dans .env
        self._save_to_env()
        
        messagebox.showinfo(
            "Succès", 
            "Configuration sauvegardée!\nRedémarrez l'application pour appliquer les changements."
        )
        self.destroy()
        
    def _save_to_env(self):
        """Sauvegarde la configuration dans le fichier .env"""
        from pathlib import Path
        
        env_path = Path(__file__).parent.parent.parent / '.env'
        
        # Lire le contenu existant
        existing_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                existing_lines = f.readlines()
        
        # Mapper les clés
        key_mapping = {
            'spotify_client_id': 'SPOTIFY_CLIENT_ID',
            'spotify_client_secret': 'SPOTIFY_CLIENT_SECRET',
            'discogs_token': 'DISCOGS_TOKEN',
            'openai_api_key': 'OPENAI_API_KEY'
        }
        
        # Mettre à jour ou ajouter les lignes
        updated = False
        new_lines = []
        
        for line in existing_lines:
            updated_line = False
            for internal_key, env_key in key_mapping.items():
                if line.startswith(f"{env_key}=") and internal_key in self.result:
                    new_lines.append(f"{env_key}={self.result[internal_key]}\n")
                    updated_line = True
                    updated = True
                    break
            
            if not updated_line:
                new_lines.append(line)
        
        # Ajouter les nouvelles clés
        for internal_key, value in self.result.items():
            env_key = key_mapping.get(internal_key)
            if env_key and not any(line.startswith(f"{env_key}=") for line in new_lines):
                new_lines.append(f"{env_key}={value}\n")
        
        # Écrire le fichier
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
    def get_result(self) -> Optional[Dict]:
        return self.result