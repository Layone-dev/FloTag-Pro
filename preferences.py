"""
Gestionnaire de préférences utilisateur pour FloTag Pro
Sauvegarde les préférences dans un fichier JSON
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class PreferencesManager:
    """Gère les préférences utilisateur de l'application"""
    
    DEFAULT_PREFERENCES = {
        'ui': {
            'last_directory': str(Path.home() / 'Music'),
            'window_geometry': None,
            'show_tips': True,
            'confirm_on_save': True
        },
        'analysis': {
            'auto_analyze': True,
            'default_energy': 5,
            'preferred_contexts': ['Bar', 'Club'],
            'preferred_moments': ['Warmup', 'Peaktime'],
            'skip_existing': True
        },
        'tags': {
            'overwrite_existing': False,
            'backup_original': True,
            'write_artwork': True,
            'normalize_names': True
        },
        'cache': {
            'auto_cleanup': True,
            'cleanup_days': 30
        },
        'recent': {
            'files': [],
            'directories': [],
            'max_recent': 10
        }
    }
    
    def __init__(self, prefs_file: Optional[str] = None):
        """
        Initialise le gestionnaire de préférences.
        
        Args:
            prefs_file: Chemin du fichier de préférences (optionnel)
        """
        if prefs_file:
            self.prefs_file = Path(prefs_file)
        else:
            self.prefs_file = Path.home() / '.flotag_preferences.json'
        
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Charge les préférences depuis le fichier"""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    # Fusionner avec les préférences par défaut
                    return self._merge_preferences(self.DEFAULT_PREFERENCES, loaded_prefs)
            except Exception as e:
                print(f"⚠️  Erreur chargement préférences: {e}")
                return self.DEFAULT_PREFERENCES.copy()
        else:
            return self.DEFAULT_PREFERENCES.copy()
    
    def _merge_preferences(self, default: Dict, loaded: Dict) -> Dict:
        """Fusionne les préférences chargées avec les valeurs par défaut"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_preferences(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save(self) -> bool:
        """Sauvegarde les préférences dans le fichier"""
        try:
            # Ajouter un timestamp
            self.preferences['_metadata'] = {
                'last_saved': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde préférences: {e}")
            return False
    
    # === Getters ===
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Récupère une valeur de préférence.
        
        Args:
            key_path: Chemin de la clé (ex: 'ui.last_directory')
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de la préférence
        """
        keys = key_path.split('.')
        value = self.preferences
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    # === Setters ===
    
    def set(self, key_path: str, value: Any, auto_save: bool = True):
        """
        Définit une valeur de préférence.
        
        Args:
            key_path: Chemin de la clé (ex: 'ui.last_directory')
            value: Nouvelle valeur
            auto_save: Sauvegarder automatiquement
        """
        keys = key_path.split('.')
        target = self.preferences
        
        # Naviguer jusqu'à la clé parent
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Définir la valeur
        target[keys[-1]] = value
        
        # Sauvegarder si demandé
        if auto_save:
            self.save()
    
    # === Méthodes spécifiques ===
    
    def get_last_directory(self) -> str:
        """Retourne le dernier répertoire utilisé"""
        return self.get('ui.last_directory', str(Path.home() / 'Music'))
    
    def set_last_directory(self, directory: str):
        """Définit le dernier répertoire utilisé"""
        self.set('ui.last_directory', directory)
    
    def add_recent_file(self, file_path: str):
        """Ajoute un fichier aux fichiers récents"""
        recent_files = self.get('recent.files', [])
        
        # Retirer si déjà présent
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Ajouter en début
        recent_files.insert(0, file_path)
        
        # Limiter la taille
        max_recent = self.get('recent.max_recent', 10)
        recent_files = recent_files[:max_recent]
        
        self.set('recent.files', recent_files)
    
    def get_recent_files(self) -> list:
        """Retourne la liste des fichiers récents"""
        return self.get('recent.files', [])
    
    def clear_recent_files(self):
        """Vide la liste des fichiers récents"""
        self.set('recent.files', [])
    
    def get_preferred_contexts(self) -> list:
        """Retourne les contextes préférés"""
        return self.get('analysis.preferred_contexts', ['Bar', 'Club'])
    
    def set_preferred_contexts(self, contexts: list):
        """Définit les contextes préférés"""
        self.set('analysis.preferred_contexts', contexts)
    
    def get_preferred_moments(self) -> list:
        """Retourne les moments préférés"""
        return self.get('analysis.preferred_moments', ['Warmup', 'Peaktime'])
    
    def set_preferred_moments(self, moments: list):
        """Définit les moments préférés"""
        self.set('analysis.preferred_moments', moments)
    
    def should_auto_analyze(self) -> bool:
        """Indique si l'analyse automatique est activée"""
        return self.get('analysis.auto_analyze', True)
    
    def should_write_artwork(self) -> bool:
        """Indique si les pochettes doivent être écrites"""
        return self.get('tags.write_artwork', True)
    
    def should_backup_original(self) -> bool:
        """Indique si les tags originaux doivent être sauvegardés"""
        return self.get('tags.backup_original', True)
    
    def reset_to_defaults(self):
        """Réinitialise toutes les préférences aux valeurs par défaut"""
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        self.save()
    
    def export_preferences(self, export_path: str):
        """Exporte les préférences vers un fichier"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erreur export préférences: {e}")
            return False
    
    def import_preferences(self, import_path: str) -> bool:
        """Importe les préférences depuis un fichier"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Valider et fusionner
            self.preferences = self._merge_preferences(self.DEFAULT_PREFERENCES, imported)
            return self.save()
        except Exception as e:
            print(f"❌ Erreur import préférences: {e}")
            return False


# Instance globale
_preferences_instance: Optional[PreferencesManager] = None


def get_preferences() -> PreferencesManager:
    """Retourne l'instance globale du gestionnaire de préférences"""
    global _preferences_instance
    if _preferences_instance is None:
        _preferences_instance = PreferencesManager()
    return _preferences_instance 