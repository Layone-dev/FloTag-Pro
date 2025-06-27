"""
Configuration centralisée pour FloTag Pro
Gère le chargement des variables d'environnement et les paramètres par défaut
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Configuration principale de l'application"""
    
    def __init__(self):
        """Initialise la configuration et charge les variables d'environnement"""
        self._load_env()
        self._setup_paths()
    
    def _load_env(self):
        """Charge les variables d'environnement depuis .env si disponible"""
        try:
            from dotenv import load_dotenv
            env_path = Path('.env')
            if env_path.exists():
                load_dotenv(env_path)
                print("✅ Variables d'environnement chargées depuis .env")
        except ImportError:
            print("⚠️  python-dotenv non installé, utilisation des variables système uniquement")
    
    def _setup_paths(self):
        """Configure les chemins de l'application"""
        self.BASE_DIR = Path(__file__).parent
        self.CACHE_DIR = Path(os.getenv('CACHE_DIR', Path.home() / '.flotag_cache'))
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # === API Keys ===
    
    @property
    def SPOTIFY_CLIENT_ID(self) -> Optional[str]:
        """Client ID Spotify"""
        return os.getenv('SPOTIFY_CLIENT_ID')
    
    @property
    def SPOTIFY_CLIENT_SECRET(self) -> Optional[str]:
        """Client Secret Spotify"""
        return os.getenv('SPOTIFY_CLIENT_SECRET')
    
    @property
    def DISCOGS_TOKEN(self) -> Optional[str]:
        """Token Discogs"""
        return os.getenv('DISCOGS_TOKEN')
    
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        """Clé API OpenAI"""
        return os.getenv('OPENAI_API_KEY')
    
    # === Configuration Cache ===
    
    @property
    def MAX_CACHE_AGE_DAYS(self) -> int:
        """Âge maximum du cache en jours"""
        return int(os.getenv('MAX_CACHE_AGE_DAYS', '30'))
    
    @property
    def CACHE_ENABLED(self) -> bool:
        """Active/désactive le cache"""
        return os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    
    # === Configuration Application ===
    
    @property
    def APP_NAME(self) -> str:
        """Nom de l'application"""
        return "FloTag Pro"
    
    @property
    def APP_VERSION(self) -> str:
        """Version de l'application"""
        return "1.0.0"
    
    @property
    def SUPPORTED_FORMATS(self) -> list:
        """Formats de fichiers audio supportés"""
        return ['.mp3', '.flac', '.m4a', '.mp4', '.aiff', '.wav']
    
    @property
    def DEFAULT_ENERGY(self) -> int:
        """Niveau d'énergie par défaut (1-10)"""
        return 5
    
    # === Configuration UI ===
    
    @property
    def WINDOW_WIDTH(self) -> int:
        """Largeur de la fenêtre"""
        return 1100
    
    @property
    def WINDOW_HEIGHT(self) -> int:
        """Hauteur de la fenêtre"""
        return 750
    
    @property
    def THEME(self) -> str:
        """Thème de l'interface (Dark/Light)"""
        return "Dark"
    
    @property
    def COLOR_THEME(self) -> str:
        """Thème de couleur"""
        return "blue"
    
    # === Méthodes utilitaires ===
    
    def get_api_status(self) -> Dict[str, bool]:
        """Retourne le statut de configuration des APIs"""
        return {
            'spotify': bool(self.SPOTIFY_CLIENT_ID and self.SPOTIFY_CLIENT_SECRET),
            'discogs': bool(self.DISCOGS_TOKEN),
            'openai': bool(self.OPENAI_API_KEY)
        }
    
    def is_fully_configured(self) -> bool:
        """Vérifie si toutes les APIs sont configurées"""
        status = self.get_api_status()
        return all(status.values())
    
    def get_missing_apis(self) -> list:
        """Retourne la liste des APIs non configurées"""
        status = self.get_api_status()
        return [api for api, configured in status.items() if not configured]
    
    def print_status(self):
        """Affiche le statut de configuration"""
        print(f"\n=== {self.APP_NAME} v{self.APP_VERSION} ===")
        print("\nConfiguration des APIs:")
        
        status = self.get_api_status()
        for api, configured in status.items():
            icon = "✅" if configured else "⚠️ "
            status_text = "Configuré" if configured else "Non configuré"
            print(f"  {icon} {api.capitalize()}: {status_text}")
        
        if not self.is_fully_configured():
            print("\n💡 Conseil: Configurez les APIs manquantes dans le fichier .env")
            print("   Consultez .env.example pour un modèle")
        
        print(f"\n📁 Cache: {self.CACHE_DIR}")
        print(f"   Activé: {'Oui' if self.CACHE_ENABLED else 'Non'}")
        print(f"   Durée max: {self.MAX_CACHE_AGE_DAYS} jours")
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporte la configuration sous forme de dictionnaire"""
        return {
            'app': {
                'name': self.APP_NAME,
                'version': self.APP_VERSION,
                'supported_formats': self.SUPPORTED_FORMATS
            },
            'apis': self.get_api_status(),
            'cache': {
                'enabled': self.CACHE_ENABLED,
                'directory': str(self.CACHE_DIR),
                'max_age_days': self.MAX_CACHE_AGE_DAYS
            },
            'ui': {
                'width': self.WINDOW_WIDTH,
                'height': self.WINDOW_HEIGHT,
                'theme': self.THEME,
                'color_theme': self.COLOR_THEME
            }
        }


# Instance globale de configuration
config = Config()


# Fonctions utilitaires pour un accès facile
def get_config() -> Config:
    """Retourne l'instance de configuration"""
    return config


def is_api_configured(api_name: str) -> bool:
    """Vérifie si une API spécifique est configurée"""
    return config.get_api_status().get(api_name.lower(), False) 