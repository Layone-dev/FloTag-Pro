"""
Gestionnaire de cache corrigé pour FlowTag Pro
Gère correctement les données binaires (images)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import base64

class CacheManager:
    """Gère le cache des appels API pour éviter les limites de taux"""
    
    def __init__(self):
        self.cache_dir = Path.home() / '.flotag_pro' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=7)  # Cache valide 7 jours
        
    def _get_cache_path(self, cache_key: str, service: str) -> Path:
        """Retourne le chemin du fichier cache"""
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in "._- ")[:100]
        return self.cache_dir / f"{service}_{safe_key}.json"
        
    def get_api_cache(self, cache_key: str, service: str) -> Optional[Dict[str, Any]]:
        """Récupère une entrée du cache si elle existe et est valide"""
        cache_path = self._get_cache_path(cache_key, service)
        
        if not cache_path.exists():
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Vérifier la validité temporelle
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.cache_duration:
                cache_path.unlink()  # Supprimer le cache expiré
                return None
                
            # Décoder les données binaires si nécessaire
            response_data = cache_data['response_data']
            if isinstance(response_data, dict):
                for key, value in response_data.items():
                    if isinstance(value, dict) and value.get('_type') == 'bytes':
                        # Reconvertir en bytes
                        response_data[key] = base64.b64decode(value['data'])
                        
            return cache_data
            
        except Exception as e:
            print(f"Erreur lecture cache pour {cache_key}: {e}")
            return None
            
    def save_api_cache(self, cache_key: str, service: str, response_data: Any) -> None:
        """Sauvegarde une réponse API dans le cache"""
        cache_path = self._get_cache_path(cache_key, service)
        
        try:
            # Préparer les données pour la sérialisation JSON
            serializable_data = self._make_serializable(response_data)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'service': service,
                'cache_key': cache_key,
                'response_data': serializable_data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ Cache sauvegardé pour {service}: {cache_key[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder le cache pour {cache_key}: {e}")
            # Ne pas faire crasher l'app si le cache échoue
            
    def _make_serializable(self, obj: Any) -> Any:
        """Convertit les objets non-sérialisables en format JSON"""
        if isinstance(obj, bytes):
            # Encoder les bytes en base64
            return {
                '_type': 'bytes',
                'data': base64.b64encode(obj).decode('utf-8')
            }
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj
            
    def clear_cache(self, service: Optional[str] = None) -> None:
        """Efface le cache (optionnellement pour un service spécifique)"""
        if service:
            pattern = f"{service}_*.json"
        else:
            pattern = "*.json"
            
        for cache_file in self.cache_dir.glob(pattern):
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"Erreur suppression cache {cache_file}: {e}")
                
        print(f"✅ Cache effacé{f' pour {service}' if service else ''}")
        
    def get_cache_stats(self) -> Dict[str, int]:
        """Retourne des statistiques sur le cache"""
        stats = {}
        total_size = 0
        
        for service in ['spotify_search', 'spotify_analysis', 'discogs', 'openai', 'full_analysis']:
            files = list(self.cache_dir.glob(f"{service}_*.json"))
            stats[service] = len(files)
            
            for f in files:
                total_size += f.stat().st_size
                
        stats['total_files'] = sum(stats.values())
        stats['total_size_mb'] = round(total_size / 1024 / 1024, 2)
        
        return stats