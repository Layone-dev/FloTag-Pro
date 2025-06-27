"""
Service Discogs corrigé pour FlowTag Pro
"""

import os
import time
import requests
from typing import Dict, Any, Optional, List
from .cache_manager import CacheManager

class DiscogsService:
    """Service pour récupérer les infos et pochettes depuis Discogs"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.token = os.getenv('DISCOGS_TOKEN')
        self.headers = {
            'Authorization': f'Discogs token={self.token}',
            'User-Agent': 'FloTagPro/1.0'
        }
        self.base_url = 'https://api.discogs.com'
        
    async def get_discogs_info_and_artwork(self, artist: str, title: str) -> Dict[str, Any]:
        """Récupère les infos et la pochette d'un track depuis Discogs"""
        cache_key = f"discogs_full_{artist}_{title}"
        cached_result = self.cache_manager.get_api_cache(cache_key, 'discogs')
        
        if cached_result:
            return cached_result['response_data']
            
        result = {
            'album': None,
            'year': None,
            'genre': None,
            'label': None,
            'artwork_bytes': None
        }
        
        try:
            # Rechercher le release
            search_results = await self.search_release(artist, title)
            
            if search_results and search_results.get('results'):
                # Prendre le premier résultat
                release_data = search_results['results'][0]
                
                # Extraire les infos basiques depuis les résultats de recherche
                result['album'] = release_data.get('title', '')
                result['year'] = release_data.get('year')
                result['genre'] = release_data.get('genre', [])
                result['label'] = release_data.get('label', [''])[0] if release_data.get('label') else ''
                
                # Si on a un ID de release, essayer de récupérer plus de détails
                if release_data.get('id'):
                    try:
                        # Récupérer les détails complets du release
                        detailed_release = await self.get_release_details(release_data['id'])
                        if detailed_release:
                            # Mettre à jour avec les infos détaillées si disponibles
                            if detailed_release.get('title'):
                                result['album'] = detailed_release['title']
                            if detailed_release.get('year'):
                                result['year'] = detailed_release['year']
                            if detailed_release.get('genres'):
                                result['genre'] = detailed_release['genres']
                            if detailed_release.get('labels'):
                                result['label'] = detailed_release['labels'][0].get('name', '') if detailed_release['labels'] else ''
                    except Exception as e:
                        print(f"Erreur récupération détails release: {e}")
                        # Continuer avec les infos basiques
                
                # Récupérer la pochette
                if release_data.get('cover_image'):
                    artwork_bytes = await self.download_artwork(release_data['cover_image'])
                    result['artwork_bytes'] = artwork_bytes
                    
        except Exception as e:
            print(f"Erreur lors de la récupération des infos Discogs: {e}")
            
        # Sauvegarder dans le cache
        self.cache_manager.save_api_cache(cache_key, 'discogs', result)
        
        return result
        
    async def search_release(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Recherche un release dans Discogs"""
        if not self.token:
            return None
            
        try:
            # D'abord essayer avec artiste + titre
            params = {
                'artist': artist,
                'track': title,
                'type': 'release',
                'per_page': 10
            }
            
            response = requests.get(
                f"{self.base_url}/database/search",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return data
                    
            # Si pas de résultat, essayer avec une recherche plus large
            params = {
                'q': f"{artist} {title}",
                'type': 'release',
                'per_page': 10
            }
            
            response = requests.get(
                f"{self.base_url}/database/search",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"Erreur recherche Discogs: {e}")
            
        return None
        
    async def get_release_details(self, release_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails complets d'un release"""
        if not self.token:
            return None
            
        try:
            response = requests.get(
                f"{self.base_url}/releases/{release_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"Erreur récupération release {release_id}: {e}")
            
        return None
        
    async def download_artwork(self, image_url: str) -> Optional[bytes]:
        """Télécharge une image de pochette"""
        try:
            # Discogs limite les requêtes, on attend un peu
            time.sleep(0.5)
            
            response = requests.get(image_url, headers=self.headers)
            if response.status_code == 200:
                return response.content
                
        except Exception as e:
            print(f"Erreur téléchargement pochette: {e}")
            
        return None
        
    async def search_artwork(self, artist: str, title: str) -> Optional[bytes]:
        """Recherche et télécharge uniquement la pochette"""
        # Utiliser la méthode complète qui inclut la pochette
        result = await self.get_discogs_info_and_artwork(artist, title)
        return result.get('artwork_bytes')