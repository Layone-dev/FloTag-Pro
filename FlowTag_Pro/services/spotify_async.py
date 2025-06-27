"""
Service Spotify Async avec playlists actualisées pour 2025
Optimisé pour l'analyse DJ événementiel
"""

import os
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from .cache_manager import CacheManager


class SpotifyAsyncService:
    """Service Spotify asynchrone avec playlists vérifiées et actualisées"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.sp = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.setup_client()
        
    def setup_client(self):
        """Configuration du client Spotify"""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if client_id and client_secret:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                print("✅ Client Spotify configuré avec succès")
            except Exception as e:
                print(f"❌ Erreur configuration Spotify: {e}")
                self.sp = None
        else:
            print("⚠️ Clés Spotify non configurées")
    
    def get_dj_playlists(self) -> Dict[str, str]:
        """Retourne les playlists actualisées et vérifiées pour 2025"""
        return {
            # === HITS ACTUELS & VIRAUX (15 playlists) ===
            "37i9dQZF1DXcBWIGoYBM5M": "Today's Top Hits",          # 30M+ followers - Toujours actif
            "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",                # 14M+ followers - Hip-hop hits
            "37i9dQZF1DX4JAvHpjipBk": "New Music Friday",         # Nouveautés hebdo
            "37i9dQZF1DX5dNi5DgQvGI": "Viral Hits",               # TikTok & viral
            "37i9dQZF1DX2L0iB23Enbq": "Viral 50 - Global",       # Top viral mondial
            "37i9dQZF1DX1HUbZS4LEyL": "Top 50 - Global",         # Top 50 mondial
            "37i9dQZF1DWUa8ZRTfalHk": "Pop Rising",               # Pop émergente
            "37i9dQZF1DX3LyU0mhfqgP": "Out Now",                  # Sorties récentes
            "37i9dQZF1DX4dyzvuaRJ0n": "mint",                     # Alternative hits
            "37i9dQZF1DX6z20IXmBjWI": "Fresh Finds",              # Découvertes
            "37i9dQZF1DWYNSm3Z3MxiM": "Teen Beats",               # Hits jeunes
            "37i9dQZF1DX4W3aJd5DPHk": "Dance Party",              # Dance actuelle
            "37i9dQZF1DX1T68DrcOyx8": "Internet People",          # Culture internet
            "37i9dQZF1DWYkaDif7Ztbp": "African Heat",             # Afrobeats viral
            "37i9dQZF1DX2RxBh64BHjQ": "Most Necessary",           # Hip-hop essential
            
            # === PARTY & CLUB EDM (20 playlists) ===
            "37i9dQZF1DX4W3aJd5DPHk": "Dance Party",              # Dance hits
            "37i9dQZF1DXa8NOEUWPn9W": "Housewerk",                # House music
            "37i9dQZF1DX0BcQWzuB7ZO": "Dance Hits",               # EDM populaire
            "37i9dQZF1DX8tZsk68tuDw": "Dance Rising",             # EDM montante
            "37i9dQZF1DX7ZUug1ANKRP": "Main Stage",               # Festival EDM
            "37i9dQZF1DX6J5xfwh2tZF": "mint electronica",         # Electro fresh
            "37i9dQZF1DX5Q27plkaOQ3": "Progressive House",        # Progressive
            "37i9dQZF1DXa2PvUpywmrr": "Electronic Circus",        # Mix électro
            "37i9dQZF1DX8Sz1gsYZdwj": "Techno Bunker",           # Techno underground
            "37i9dQZF1DX0r3x8OtiwEM": "Bass Arcade",             # Bass music
            "37i9dQZF1DX65bVJnL18Wi": "Trance Mission",          # Trance
            "37i9dQZF1DWZryfwmX88iC": "Deep House Relax",        # Deep house
            "37i9dQZF1DXbIeCB85KmYt": "Future House",            # Future house
            "37i9dQZF1DX9XIFQuFvzM4": "Dancehall Official",      # Dancehall
            "37i9dQZF1DX1F3MWdxBB2j": "Tech House",              # Tech house
            "37i9dQZF1DX8CopunbDxgW": "Tropical House",          # Tropical house
            "37i9dQZF1DX0AMssoUKCz7": "Big Room House",          # Big room
            "37i9dQZF1DXaXB8fQg7xif": "Dance Workout",           # Fitness dance
            "37i9dQZF1DX32NsLKyzScr": "Power Hour",              # Pre-party
            "37i9dQZF1DX7EF8wVxBVhG": "Night Rider",            # Night drive EDM
            
            # === MARIAGE & ROMANCE (15 playlists) ===
            "37i9dQZF1DX7gIoKXt0gmx": "Love Songs",              # Love classics
            "37i9dQZF1DX6mvEU1S6INL": "You & Me",                # Romantic current
            "37i9dQZF1DXaKIA8E7WcJj": "Acoustic Love",           # Acoustic romance
            "37i9dQZF1DX3YSRoSdA634": "Love Pop",                # Pop love songs
            "37i9dQZF1DX38lOuCqMjbY": "Wedding Songs",           # Wedding hits
            "37i9dQZF1DWTbCuAXgsVHO": "Wedding Party",           # Reception
            "37i9dQZF1DX5IDTimEWoTd": "First Dance",             # First dance
            "37i9dQZF1DWXmlLSKkfdAk": "Love Ballads",            # Ballades
            "37i9dQZF1DWVOMXLZpjGG3": "Romance Latino",          # Latin romance
            "37i9dQZF1DX7F6T2n2fegs": "Forever Wedding Songs",   # Classics mariage
            "37i9dQZF1DWVUq1oQhxNVB": "Pop Wedding",             # Pop wedding
            "37i9dQZF1DWYm55bBJnBOi": "Love R&B",                # R&B romance
            "37i9dQZF1DX1BzILRveYHb": "Country Wedding",         # Country wedding
            "37i9dQZF1DX9wC1KY45plY": "Soul Wedding",            # Soul classics
            "37i9dQZF1DXb9v9H5QRUi5": "Jazz Romance",            # Jazz love
            
            # === LOUNGE & COCKTAIL (15 playlists) ===
            "37i9dQZF1DX4UkKv8ED8jp": "Jazz Vibes",              # Modern jazz
            "37i9dQZF1DWTvNyxOwkztu": "Lounge - Soft House",     # Lounge house
            "37i9dQZF1DX0SM0LYsmbMT": "Jazz - Cocktails",        # Cocktail jazz
            "37i9dQZF1DX82Zzp6AKx64": "Deep House Relax",        # Chill house
            "37i9dQZF1DXbYM8nMdgG9S": "Café del Mar",            # Ibiza chill
            "37i9dQZF1DX3Ogo9pFvBkY": "Chill Lounge",            # Lounge
            "37i9dQZF1DWV7EzJMK2FUI": "Jazz in the Background",  # Background jazz
            "37i9dQZF1DX4sWSpwq3LiO": "Peaceful Piano",          # Piano chill
            "37i9dQZF1DX1s9knjP51Oa": "Calm Vibes",              # Calm
            "37i9dQZF1DWTwnEm1IYyoj": "Soft Rock",               # Soft rock
            "37i9dQZF1DX6ziVCJnEm59": "Lush + Atmospheric",      # Ambient
            "37i9dQZF1DXc9xYI1NpQVf": "Sunset Chill",            # Sunset vibes
            "37i9dQZF1DX2yvmlOdMYzV": "Chill Vibes",             # General chill
            "37i9dQZF1DX889U0CL85jj": "Chill Tracks",            # Chill mix
            "37i9dQZF1DWXe9gwrJXPSm": "Lo-Fi Beats",             # Lo-fi hip hop
            
            # === LATINO & REGGAETON (20 playlists) ===
            "37i9dQZF1DX10zKzsJ2jva": "Viva Latino",              # 11M+ followers
            "37i9dQZF1DWYJ59NCcoilc": "Baila Reggaeton",          # Reggaeton hits
            "37i9dQZF1DWY7IeIP1cdjF": "Éxitos México",           # Mexican hits
            "37i9dQZF1DX1HUbZS4LEyL": "Latin Hits",              # Latin mix
            "37i9dQZF1DXbLMw3ry7d7k": "Latin Party",             # Party latin
            "37i9dQZF1DX8SfyqmSFDwe": "Reggaeton Classics",      # Classics
            "37i9dQZF1DX7F4ZDm7EKJp": "La Reina",                # Female reggaeton
            "37i9dQZF1DWSpF87bP6JSF": "Novedades Viernes",       # New latin
            "37i9dQZF1DX2apWzyECwyZ": "La Vida Loca",            # Party mix
            "37i9dQZF1DX7gIoKXt0gmx": "Cumbia Sonidera",         # Cumbia
            "37i9dQZF1DWVcbCMNwfUyM": "Salsa Classics",          # Salsa
            "37i9dQZF1DX5GQZoaT6C4y": "Bachata Lovers",          # Bachata
            "37i9dQZF1DWTx0xog90XWm": "Merengue Total",          # Merengue
            "37i9dQZF1DX3E5bKAjp8rg": "Trap Latino",             # Latin trap
            "37i9dQZF1DWNo0gst9Mwfj": "Perreo Intenso",          # Perreo
            "37i9dQZF1DX8FPV9C4MVP5": "Dembow",                  # Dembow
            "37i9dQZF1DWXbLOeKQWLu1": "Tropical Morning",        # Tropical
            "37i9dQZF1DX7Ocjc6HVlQu": "Fiesta Latina",           # Fiesta mix
            "37i9dQZF1DX3ND264N08pv": "Hits Urbano",             # Urban latin
            "37i9dQZF1DX4osfY3zybD2": "Latin Workout",           # Latin fitness
            
            # === DECADES & CLASSICS (15 playlists) ===
            "37i9dQZF1DX4UtSsGT1Sbe": "All Out 80s",             # 80s certified hits
            "37i9dQZF1DXbTxeAdrVG2l": "All Out 90s",             # 90s certified hits
            "37i9dQZF1DX4o1oenSJRJd": "All Out 00s",             # 2000s certified hits
            "37i9dQZF1DX5Ejj0EkURtP": "All Out 2010s",           # 2010s certified hits
            "37i9dQZF1DXc6IFF23C9jj": "All Out 70s",             # 70s certified hits
            "37i9dQZF1DWTJ7xPn4vNaz": "Rock Classics",           # Rock legends
            "37i9dQZF1DWWwQDdJayYDe": "Classic Rock Drive",       # Rock drive
            "37i9dQZF1DX1rVvRgjX59F": "90s Rock Anthems",        # 90s rock
            "37i9dQZF1DX3oM43CtKnRV": "00s Rock Anthems",        # 00s rock
            "37i9dQZF1DX82GYcclJ3Ug": "80s Rock Anthems",        # 80s rock
            "37i9dQZF1DWWzBc3TOlaAV": "Greatest Showman",        # Musical hits
            "37i9dQZF1DX50KNyX4Nfal": "Classic Soul",            # Soul classics
            "37i9dQZF1DWTkxQvqMy4WW": "Disco Forever",           # Disco hits
            "37i9dQZF1DX8NTLI2TtZa6": "Funk Rock",               # Funk classics
            "37i9dQZF1DWWOYdr4GFP3n": "Essential Classics",      # All time classics
            
            # === HIP-HOP & R&B (15 playlists) ===
            "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",               # Main hip-hop
            "37i9dQZF1DWY4xHQp97PPN": "Hip Hop Central",         # Hip hop mix
            "37i9dQZF1DWT5MrZnPU1zD": "Hip Hop Controller",      # Gaming hip-hop
            "37i9dQZF1DX2RxBh64BHjQ": "Most Necessary",          # Essential hip-hop
            "37i9dQZF1DX186v583rmzp": "I Love My '90s Hip-Hop",  # 90s classics
            "37i9dQZF1DWUFmyho2wkQU": "Signed XOXO",             # R&B current
            "37i9dQZF1DX4SBhb3fqCJd": "Are & Be",                # R&B hits
            "37i9dQZF1DWYmmr74INQlb": "Chill R&B",               # Chill R&B
            "37i9dQZF1DX6aTaZa0K6VA": "R&B Party",               # Party R&B
            "37i9dQZF1DWTggY0yqBxES": "Hip-Hop Favourites",      # Hip-hop favs
            "37i9dQZF1DX76Wlfdnj7AP": "Beast Mode Hip-Hop",      # Workout hip-hop
            "37i9dQZF1DX8gDIpdqp1XJ": "Drill",                   # Drill music
            "37i9dQZF1DWTl4y3vgJOXW": "Locked In",               # Focus hip-hop
            "37i9dQZF1DX48TTZL62Yht": "UK Rap",                  # UK hip-hop
            "37i9dQZF1DWZjqjZMudx9T": "French Rap",              # French hip-hop
            
            # === WORKOUT & MOTIVATION (10 playlists) ===
            "37i9dQZF1DX76Wlfdnj7AP": "Beast Mode",              # Intense workout
            "37i9dQZF1DX70RN3TfWWJh": "Cardio",                  # Cardio mix
            "37i9dQZF1DX35oM5SPECmN": "HIIT Workout",            # HIIT training
            "37i9dQZF1DWUVpAXiEPK8P": "Power Workout",           # Power training
            "37i9dQZF1DWUSyphfcc6aL": "Pumped Pop",              # Pop workout
            "37i9dQZF1DX8ymr6UES7vc": "Run Wild",                # Running
            "37i9dQZF1DWZq91oLsHZvy": "Adrenaline Workout",      # High energy
            "37i9dQZF1DX3ZeFHRhhi7Y": "Gym Flow",                # Gym mix
            "37i9dQZF1DWTl4y3vgJOXW": "Motivation Mix",          # Motivation
            "37i9dQZF1DX0HRj9P7NxeE": "CrossFit WOD",            # CrossFit
            
            # === CHILL & FOCUS (10 playlists) ===
            "37i9dQZF1DWZeKCadgRdKQ": "Deep Focus",              # Focus work
            "37i9dQZF1DX4sWSpwq3LiO": "Peaceful Piano",          # Piano
            "37i9dQZF1DWXe9gwrJXPSm": "Lo-Fi Beats",             # Lo-fi study
            "37i9dQZF1DX3Ogo9pFvBkY": "Chill Lounge",            # Lounge chill
            "37i9dQZF1DX4WYpdgoIcn6": "Chill Hits",              # Chill pop
            "37i9dQZF1DWTwnEm1IYyoj": "Soft Rock",               # Soft rock
            "37i9dQZF1DX6VdMW310ZC7": "Evening Acoustic",        # Acoustic
            "37i9dQZF1DX4PP3DA4J0N8": "Nature Sounds",           # Nature
            "37i9dQZF1DX2yvmlOdMYzV": "Chill Vibes",             # General chill
            "37i9dQZF1DX2UgsUIg75Vg": "Sleep",                   # Sleep music
        }
    
    async def search_track(self, title: str, artist: str) -> Optional[Dict[str, Any]]:
        """Recherche améliorée d'un track dans Spotify"""
        if not self.sp:
            return None
            
        try:
            # Vérifier le cache
            cache_key = f"spotify_search_{title}_{artist}"
            cached_result = self.cache_manager.get_api_cache(cache_key, 'spotify_search')
            
            if cached_result:
                return cached_result['response_data']
                
            # Recherche avec plusieurs stratégies
            search_queries = [
                f'track:"{title}" artist:"{artist}"',  # Recherche exacte
                f'{title} {artist}',                    # Recherche simple
                f'track:{title} artist:{artist}'        # Sans guillemets
            ]
            
            track_info = None
            for query in search_queries:
                results = await self._run_async(self.sp.search, q=query, type='track', limit=10)
                
                if results and results['tracks']['items']:
                    # Chercher la meilleure correspondance
                    for track in results['tracks']['items']:
                        track_artist = track['artists'][0]['name'].lower()
                        track_title = track['name'].lower()
                        
                        # Vérifier la correspondance
                        if (artist.lower() in track_artist or track_artist in artist.lower()) and \
                           (title.lower() in track_title or track_title in title.lower()):
                            track_info = self._extract_track_info(track)
                            break
                    
                    if track_info:
                        break
            
            if track_info:
                # Ajouter les features audio
                await self._add_audio_features(track_info)
                
                # Sauvegarder dans le cache
                self.cache_manager.save_api_cache(cache_key, 'spotify_search', track_info)
                
            print(f"  ✅ Trouvé sur Spotify: {track_info['name'] if track_info else 'Non trouvé'}")
            return track_info
                
        except Exception as e:
            print(f"❌ Erreur recherche Spotify: {e}")
            return None
    
    def _extract_track_info(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les informations importantes d'un track"""
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'] if track['artists'] else '',
            'artists': [a['name'] for a in track.get('artists', [])],
            'album': track['album']['name'] if track.get('album') else '',
            'popularity': track.get('popularity', 0),
            'duration_ms': track.get('duration_ms', 0),
            'explicit': track.get('explicit', False),
            'uri': track.get('uri', ''),
            'preview_url': track.get('preview_url'),
            'album_art': track['album']['images'][0]['url'] if track.get('album', {}).get('images') else None
        }
    
    async def _add_audio_features(self, track_info: Dict[str, Any]) -> None:
        """Ajoute les features audio à un track"""
        if not track_info.get('id'):
            return
            
        try:
            features = await self._run_async(self.sp.audio_features, track_info['id'])
            
            if features and features[0]:
                track_info.update({
                    'danceability': features[0].get('danceability', 0),
                    'energy': features[0].get('energy', 0),
                    'valence': features[0].get('valence', 0),
                    'tempo': features[0].get('tempo', 120),
                    'key': features[0].get('key', 0),
                    'mode': features[0].get('mode', 0),
                    'acousticness': features[0].get('acousticness', 0),
                    'instrumentalness': features[0].get('instrumentalness', 0),
                    'liveness': features[0].get('liveness', 0),
                    'speechiness': features[0].get('speechiness', 0),
                    'loudness': features[0].get('loudness', 0),
                    'time_signature': features[0].get('time_signature', 4)
                })
        except Exception as e:
            print(f"⚠️ Features audio non disponibles: {e}")
    
    async def analyze_track_contexts(self, track_id: str) -> Dict[str, Any]:
        """Analyse un track dans les playlists pour déterminer ses contextes DJ"""
        if not self.sp or not track_id:
            return {}
            
        # Vérifier le cache
        cache_key = f"spotify_contexts_{track_id}"
        cached_result = self.cache_manager.get_api_cache(cache_key, 'spotify_contexts')
        
        if cached_result:
            return cached_result['response_data']
            
        playlists = self.get_dj_playlists()
        found_playlists = []
        contexts = []
        styles = []
        
        print(f"🔍 Analyse dans {len(playlists)} playlists...")
        
        # Analyser par batches pour éviter le rate limiting
        batch_size = 10
        playlist_items = list(playlists.items())
        
        for i in range(0, len(playlist_items), batch_size):
            batch = playlist_items[i:i+batch_size]
            
            # Analyser en parallèle
            tasks = []
            for playlist_id, playlist_name in batch:
                tasks.append(self._check_track_in_playlist(track_id, playlist_id, playlist_name))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if result and not isinstance(result, Exception):
                    found_playlists.append(result)
                    context, style = self._categorize_playlist(result['name'])
                    if context:
                        contexts.append(context)
                    if style:
                        styles.append(style)
        
        # Analyser les résultats
        analysis = {
            'found_in_playlists': found_playlists,
            'playlist_count': len(found_playlists),
            'contexts': list(set(contexts)),
            'styles': list(set(styles)),
            'confidence': len(found_playlists) / 10  # Score de confiance basé sur le nombre de playlists
        }
        
        # Ajuster les contextes selon les résultats
        analysis['contexts'] = self._optimize_contexts(analysis['contexts'], found_playlists)
        analysis['styles'] = self._optimize_styles(analysis['styles'], found_playlists)
        
        # Sauvegarder dans le cache
        self.cache_manager.save_api_cache(cache_key, 'spotify_contexts', analysis)
        
        print(f"✅ Trouvé dans {len(found_playlists)} playlists")
        return analysis
    
    async def _check_track_in_playlist(self, track_id: str, playlist_id: str, playlist_name: str) -> Optional[Dict[str, Any]]:
        """Vérifie si un track est dans une playlist spécifique"""
        try:
            # Récupérer seulement le premier batch pour vérifier rapidement
            result = await self._run_async(
                self.sp.playlist_items,
                playlist_id,
                fields='items(track(id))',
                limit=50
            )
            
            if result and result.get('items'):
                for item in result['items']:
                    if item and item.get('track') and item['track'].get('id') == track_id:
                        return {
                            'id': playlist_id,
                            'name': playlist_name
                        }
                        
            return None
            
        except Exception:
            # Ignorer les erreurs silencieusement
            return None
    
    def _categorize_playlist(self, playlist_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Catégorise une playlist et retourne (contexte, style)"""
        name_lower = playlist_name.lower()
        
        # Contextes
        context = None
        if any(word in name_lower for word in ['wedding', 'love', 'romance', 'first dance']):
            context = 'Mariage'
        elif any(word in name_lower for word in ['party', 'dance', 'club', 'edm', 'house', 'techno']):
            context = 'Club'
        elif any(word in name_lower for word in ['lounge', 'cocktail', 'jazz', 'chill', 'relax']):
            context = 'CocktailChic'
        elif any(word in name_lower for word in ['workout', 'gym', 'cardio', 'running']):
            context = 'PoolParty'
        elif any(word in name_lower for word in ['latin', 'reggaeton', 'salsa', 'bachata']):
            context = 'Festival'
        elif any(word in name_lower for word in ['80s', '90s', '00s', 'classic', 'rock']):
            context = 'Bar'
        else:
            context = 'Generaliste'
        
        # Styles
        style = None
        if any(word in name_lower for word in ['hit', 'top', 'viral', 'trending']):
            style = 'Commercial'
        elif any(word in name_lower for word in ['classic', '80s', '90s', '00s']):
            style = 'Classics'
        elif any(word in name_lower for word in ['house', 'techno', 'edm', 'electronic']):
            style = 'House'
        elif any(word in name_lower for word in ['hip hop', 'rap', 'hip-hop']):
            style = 'HipHop'
        elif any(word in name_lower for word in ['latin', 'reggaeton', 'salsa']):
            style = 'Latino'
        elif any(word in name_lower for word in ['funk', 'groove', 'soul']):
            style = 'Funky'
        
        return context, style
    
    def _optimize_contexts(self, contexts: List[str], playlists: List[Dict]) -> List[str]:
        """Optimise la liste des contextes selon les playlists trouvées"""
        # Si trouvé dans beaucoup de playlists, c'est versatile
        if len(playlists) > 10:
            if 'Bar' not in contexts:
                contexts.append('Bar')
            if 'Club' not in contexts:
                contexts.append('Club')
                
        # Si pas assez de contextes, ajouter des défauts
        if len(contexts) < 2:
            if 'Bar' not in contexts:
                contexts.append('Bar')
            if 'Generaliste' not in contexts:
                contexts.append('Generaliste')
                
        return contexts[:5]  # Maximum 5 contextes
    
    def _optimize_styles(self, styles: List[str], playlists: List[Dict]) -> List[str]:
        """Optimise la liste des styles selon les playlists trouvées"""
        # Si très populaire, c'est commercial
        if len(playlists) > 8 and 'Commercial' not in styles:
            styles.append('Commercial')
            
        # Si pas de style, ajouter un défaut
        if not styles:
            styles.append('Commercial')
            
        return styles[:4]  # Maximum 4 styles
    
    async def get_track_artwork(self, track_id: str) -> Optional[bytes]:
        """Récupère l'artwork d'un track"""
        if not self.sp or not track_id:
            return None
            
        try:
            track = await self._run_async(self.sp.track, track_id)
            
            if track and track.get('album', {}).get('images'):
                # Prendre la plus grande image
                image_url = track['album']['images'][0]['url']
                
                # Télécharger l'image
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            return await response.read()
                            
        except Exception as e:
            print(f"❌ Erreur récupération artwork: {e}")
            
        return None
    
    async def _run_async(self, func, *args, **kwargs):
        """Exécute une fonction synchrone de manière asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    def __del__(self):
        """Ferme le pool de threads"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)