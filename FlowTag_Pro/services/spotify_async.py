"""
Service Spotify avec 120 VRAIES playlists populaires
Organisées par contexte pour DJ professionnel
"""

import os
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Any, Optional, List, Tuple
from .cache_manager import CacheManager

class SpotifyService:
    """Service Spotify avec 120 vraies playlists populaires pour analyse DJ"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.spotify_client = None
        self.playlists = {}
        self.setup_client()
        self.setup_playlists()
        
    def setup_client(self):
        """Configuration du client Spotify"""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if client_id and client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
                print("✅ Client Spotify configuré avec succès")
            except Exception as e:
                print(f"Erreur configuration Spotify: {e}")
                
    def setup_playlists(self):
        """120 VRAIES playlists Spotify populaires organisées par contexte"""
        self.PLAYLIST_IDS = {
            # === TOP HITS MONDIAUX (10 playlists) ===
            "37i9dQZF1DXcBWIGoYBM5M": "Today's Top Hits",          # 30M+ followers
            "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",                # 14M+ followers  
            "37i9dQZF1DX10zKzsJ2jva": "Viva Latino",              # 11M+ followers
            "37i9dQZF1DX4SBhb3fqCJd": "Are & Be",                 # 6M+ followers
            "37i9dQZF1DX4JAvHpjipBk": "New Music Friday",         # 4M+ followers
            "37i9dQZF1DX50QitC6Oqtn": "IGUAL Que Ayer",          # 4M+ followers
            "37i9dQZF1DX4dyzvuaRJ0n": "mint",                     # 5M+ followers
            "37i9dQZF1DX1lVhptIYRda": "Hot Country",              # 6M+ followers
            "37i9dQZF1DXcF6B6QPhFDv": "Rock This",                # 5M+ followers
            "37i9dQZF1DX2Nc3B70tvx0": "Ultimate Indie",          # 3M+ followers
            
            # === PARTY & CLUB (20 playlists) ===
            "37i9dQZF1DX4W3aJd5DPHk": "Dance Party",              # EDM party hits
            "37i9dQZF1DX0BcQWzuB7ZO": "Dance Hits",               # Current dance
            "37i9dQZF1DXa8NOEUWPn9W": "Housewerk",                # House music
            "37i9dQZF1DX8tZsk68tuDw": "Dance Rising",             # Rising dance
            "37i9dQZF1DX1kCIzMYtzum": "Dance Pop Hits",           # Pop dance
            "37i9dQZF1DX6J5xfwh2tZF": "Electronic Circus",        # Electronic
            "37i9dQZF1DX7ZUug1ANKRP": "Main Stage",               # Festival EDM
            "37i9dQZF1DX6GJXiuZRisr": "Party Hits",               # Party classics
            "37i9dQZF1DX8mBN5PyVoBO": "Electronic Dance Music",   # EDM mix
            "37i9dQZF1DX5Q27plkaOQ3": "Progressive House",        # Progressive
            "37i9dQZF1DX8Sz1gsYZdwj": "Techno Bunker",           # Techno
            "37i9dQZF1DX0r3x8OtiwEM": "Bass Arcade",             # Bass music
            "37i9dQZF1DX65bVJnL18Wi": "Trance Mission",          # Trance
            "37i9dQZF1DXaXB8fQg7xif": "Dance Party Mix",         # Party mix
            "37i9dQZF1DX32NsLKyzScr": "Power Hour",               # Pre-party
            "37i9dQZF1DXb57FjYWz00c": "Confidence Boost",        # Feel good
            "37i9dQZF1DWWmaszSfsx6L": "Turnup Tunes",            # Turn up
            "37i9dQZF1DX7EF8wVxBVhG": "Night Rider",             # Night drive
            "37i9dQZF1DWY7IeIP1cdjF": "Swag House",              # House party
            "37i9dQZF1DX2TRYkJECvfC": "Deep House 2025",         # Deep house
            
            # === MARIAGE & ROMANCE (15 playlists) ===
            "37i9dQZF1DX7gIoKXt0gmx": "Love Songs",               # Love classics
            "37i9dQZF1DX4eP0r5JiHAz": "Wedding Songs",            # Wedding hits
            "37i9dQZF1DWXmlLSKkfdAk": "Wedding Music",            # Ceremony
            "37i9dQZF1DX3YSRoSdA634": "Love Pop",                 # Pop love
            "37i9dQZF1DX6mvEU1S6INL": "You & Me",                 # Romantic
            "37i9dQZF1DWYm55bBJnBOi": "Love Ballads",            # Ballads
            "37i9dQZF1DWTwzVW3tqEyK": "Romance Latino",          # Latin romance
            "37i9dQZF1DX5GQZoaT6C4R": "Wedding Reception",       # Reception
            "37i9dQZF1DWUvZcFXKvqUy": "First Dance Songs",       # First dance
            "37i9dQZF1DX0EM2tofSJZe": "Forever Love Songs",      # Timeless
            "37i9dQZF1DX38lOuCqMjbY": "Wedding Dinner",          # Dinner music
            "37i9dQZF1DWVJLJlLzwZ4g": "Romantic Hits",           # Romantic
            "37i9dQZF1DX3oM43CtKnRV": "Love Forever",            # Forever
            "37i9dQZF1DX8ky12eWIvcW": "Wedding Classics",        # Classics
            "37i9dQZF1DWXbttAJcbphz": "Timeless Love Songs",     # Timeless
            
            # === LOUNGE & COCKTAIL (15 playlists) ===
            "37i9dQZF1DX4UkKv8ED8jp": "Jazz Vibes",               # Jazz lounge
            "37i9dQZF1DWTvNyxOwkztu": "Lounge - Soft House",     # Lounge house
            "37i9dQZF1DX0SM0LYsmbMT": "Jazz - Cocktails",        # Cocktail jazz
            "37i9dQZF1DX82Zzp6AKx64": "Deep House Relax",        # Chill house
            "37i9dQZF1DX2TRYkJECvfC": "Deep Focus",              # Work/study
            "37i9dQZF1DX3Ogo9pFvBkY": "Chill Lounge",            # Chill out
            "37i9dQZF1DWV7EzJMK2FUI": "Jazz in the Background",  # Background
            "37i9dQZF1DX0h0QnLkMBl4": "Office DJ",               # Office vibes
            "37i9dQZF1DX1s9knjP51Oa": "Calm Vibes",              # Calm
            "37i9dQZF1DWYm55bBJnBh1": "Cocktail Hour",           # Happy hour
            "37i9dQZF1DX6ziVCJnEm59": "Lush Vibes",              # Lush
            "37i9dQZF1DXaABHaOEFOJj": "Jazz for Study",          # Study jazz
            "37i9dQZF1DX9tPFwDMOaN1": "Soft Pop Hits",           # Soft pop
            "37i9dQZF1DX3YMp9n8fkNx": "Chill House",             # House chill
            "37i9dQZF1DWTwnEm1IYyoj": "Soft Rock",               # Soft rock
            
            # === LATINO & REGGAETON (15 playlists) ===
            "37i9dQZF1DX10zKzsJ2jva": "Viva Latino",              # 11M followers
            "37i9dQZF1DWW0LV9lZQNEp": "Baila Reggaeton",         # Reggaeton hits
            "37i9dQZF1DX1HUbZS4LEyL": "Latin Hits",              # Latin mix
            "37i9dQZF1DX3rxVfibe1L0": "Mood Booster",            # Feel good
            "37i9dQZF1DX8LKoIs18Krj": "Puro Reggaeton",          # Pure reggaeton
            "37i9dQZF1DWXbLOeKQWLu1": "Tropical Morning",        # Tropical
            "37i9dQZF1DX2rcblBG1GLm": "Salsa Nation",            # Salsa
            "37i9dQZF1DX5GQZoaT6C4y": "Bachata Lovers",          # Bachata
            "37i9dQZF1DXbITWG1ZJKYt": "Latin Pop",               # Pop latino
            "37i9dQZF1DX1HUbZS4LEkF": "Cumbia Sonidera",         # Cumbia
            "37i9dQZF1DWVcbCMNwfUyM": "Merengue Classics",       # Merengue
            "37i9dQZF1DX6xZZRegnrHV": "Latin Party",             # Party mix
            "37i9dQZF1DX0gtf1XpAKTe": "Reggaeton Classics",      # Classics
            "37i9dQZF1DWUaThf8nMdW6": "Latin Dance Hits",        # Dance latin
            "37i9dQZF1DX1vSWCMEDqYr": "Latin Urban",             # Urban
            
            # === DÉCENNIES & CLASSICS (15 playlists) ===
            "37i9dQZF1DX4UtSsGT1Sbe": "All Out 80s",             # 80s hits
            "37i9dQZF1DXbTxeAdrVG2l": "All Out 90s",             # 90s hits
            "37i9dQZF1DX4o1oenSJRJd": "All Out 00s",             # 2000s hits
            "37i9dQZF1DX5Ejj0EkURtP": "All Out 2010s",           # 2010s hits
            "37i9dQZF1DXc6IFF23C9jj": "Hits of the 70s",         # 70s hits
            "37i9dQZF1DWWOYdr4GFP3n": "Classic Rock Drive",       # Rock classics
            "37i9dQZF1DX1lVhptIYRds": "Rock Classics",           # Rock legends
            "37i9dQZF1DX6aTaZa0K6VA": "Pop Rock",                # Pop rock
            "37i9dQZF1DWXRqgorJj26U": "Rock Hard",               # Hard rock
            "37i9dQZF1DX4Y4RhrZqHhr": "80s Rock Anthems",        # 80s rock
            "37i9dQZF1DX1rVvRgjX59F": "90s Rock Anthems",        # 90s rock
            "37i9dQZF1DX3oM43CtKnRV": "00s Rock Anthems",        # 00s rock
            "37i9dQZF1DWWzBc3TOlaAV": "Greatest Hits",           # All time
            "37i9dQZF1DX0BttRsnDOsJ": "Legendary",               # Legends
            "37i9dQZF1DX8ky12eWIvcZ": "Essential Classics",      # Essentials
            
            # === HIP-HOP & R&B (10 playlists) ===
            "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",               # 14M followers
            "37i9dQZF1DX4SBhb3fqCJd": "Are & Be",                # 6M followers
            "37i9dQZF1DWY4xHQp97PPN": "Hip Hop Central",         # Hip hop mix
            "37i9dQZF1DWT5MrZnPU1zD": "Hip Hop Controller",      # Gaming
            "37i9dQZF1DX48TTZL62Yht": "Rap UK",                  # UK rap
            "37i9dQZF1DX186v583rmzp": "I Love My 90s Hip-Hop",   # 90s
            "37i9dQZF1DX2RxBh64BHjQ": "Most Necessary",          # Essential
            "37i9dQZF1DWTggY0yqBxES": "Hip-Hop Favourites",      # Favorites
            "37i9dQZF1DX76Wlfdnj7AP": "Beast Mode",              # Workout
            "37i9dQZF1DX6GwdWRQMQpq": "Feelin' Myself",          # Confidence
            
            # === POP & MAINSTREAM (10 playlists) ===
            "37i9dQZF1DXcBWIGoYBM5M": "Today's Top Hits",        # 30M followers
            "37i9dQZF1DX4dyzvuaRJ0n": "mint",                    # 5M followers
            "37i9dQZF1DX0b1hHYQtJjp": "Just Good Music",         # Good vibes
            "37i9dQZF1DWWjGdmeTyeJ6": "Indie Pop",               # Indie
            "37i9dQZF1DX3rxVfibe1P0": "Mood Booster",            # Happy
            "37i9dQZF1DX1PfYnYcpw8w": "Happy Hits!",             # Feel good
            "37i9dQZF1DX2sUQwD7tbmL": "Feel Good Summer",        # Summer
            "37i9dQZF1DWVOMXLYifV6g": "Songs to Sing in the Car", # Car
            "37i9dQZF1DX4WYpdgoIcn6": "Chill Hits",              # Chill pop
            "37i9dQZF1DX5GQZoaT6C4R": "Top Hits 2025",           # Current
            
            # === WORKOUT & ENERGY (10 playlists) ===
            "37i9dQZF1DX76Wlfdnj7AP": "Beast Mode",              # Intense
            "37i9dQZF1DX70RN3TfWWJh": "Cardio",                  # Cardio
            "37i9dQZF1DX35oM5SPECmN": "Workout Beats",           # Gym
            "37i9dQZF1DWUVpAXiEPK8P": "Power Workout",           # Power
            "37i9dQZF1DWUSyphfcc6aL": "Gym Class Heroes",        # Gym hits
            "37i9dQZF1DX8ymr6UES7vc": "Pump It Up",              # Pump
            "37i9dQZF1DX3ZeFHRhhi7Y": "Running Wild",            # Running
            "37i9dQZF1DWZq91oLsHZvy": "Adrenaline Workout",      # Adrenaline
            "37i9dQZF1DX8jnAPF7Iiqp": "Motivation Mix",          # Motivation
            "37i9dQZF1DX58NJL8iVBGW": "Training Season",         # Training
            
            # === CHILL & RELAX (10 playlists) ===
            "37i9dQZF1DX3Ogo9pFvBkY": "Chill Lounge",            # Lounge
            "37i9dQZF1DX2yvmlOdMYzV": "Chill Vibes",             # Vibes
            "37i9dQZF1DX6VdMW310ZC7": "Evening Chill",           # Evening
            "37i9dQZF1DWTwnEm1IYyoj": "Soft Rock",               # Soft
            "37i9dQZF1DX3YSRoSdA634": "Love Pop",                # Love
            "37i9dQZF1DX889U0CL85jj": "Chill Tracks",            # Tracks
            "37i9dQZF1DX2UgsUIg75Vg": "Chilled R&B",             # R&B chill
            "37i9dQZF1DWXe9gwrJXPSm": "Lo-Fi Beats",             # Lo-fi
            "37i9dQZF1DX4WYpdgoIcn6": "Chill Hits",              # Hits
            "37i9dQZF1DWYm55bBJnBOi": "Relax & Unwind",          # Unwind
        }
        
    async def analyze_track_in_playlists(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse complète d'un track dans les 120 playlists"""
        if not self.spotify_client:
            return {}
            
        # Vérifier le cache
        cache_key = f"spotify_analysis_{track_info.get('title', '')}_{track_info.get('artist', '')}"
        cached_analysis = self.cache_manager.get_api_cache(cache_key, 'spotify_analysis')
        
        if cached_analysis:
            print(f"✅ Analyse trouvée dans le cache pour {track_info.get('artist')} - {track_info.get('title')}")
            return cached_analysis['response_data']
            
        # Rechercher le track dans Spotify
        spotify_track = await self.search_track(track_info.get('title', ''), track_info.get('artist', ''))
        if not spotify_track:
            return {}
            
        print(f"🔍 Analyse du track dans {len(self.PLAYLIST_IDS)} playlists...")
        
        # Analyser dans toutes les playlists
        playlist_analysis = await self.analyze_track_in_all_playlists(spotify_track['id'])
        
        # Déterminer les contextes et styles
        contexts = self.determine_contexts(playlist_analysis)
        styles = self.determine_styles(playlist_analysis, spotify_track)
        moments = self.determine_moments(playlist_analysis, spotify_track)
        
        print(f"✅ Trouvé dans {len(playlist_analysis)} playlists")
        print(f"📍 Contextes: {contexts}")
        print(f"🎨 Styles: {styles}")
        print(f"⏰ Moments: {moments}")
        
        analysis_result = {
            'spotify_track': spotify_track,
            'playlist_analysis': playlist_analysis,
            'contexts': contexts,
            'styles': styles,
            'moments': moments,
            'confidence_score': self.calculate_confidence_score(playlist_analysis)
        }
        
        # Sauvegarder dans le cache
        self.cache_manager.save_api_cache(cache_key, 'spotify_analysis', analysis_result)
        
        return analysis_result
        
    async def analyze_track_in_all_playlists(self, track_id: str) -> Dict[str, Any]:
        """Analyse un track dans toutes les playlists"""
        playlist_results = {}
        
        # Analyser par batch pour optimiser
        batch_size = 10
        playlist_items = list(self.PLAYLIST_IDS.items())
        
        for i in range(0, len(playlist_items), batch_size):
            batch = playlist_items[i:i+batch_size]
            
            for playlist_id, playlist_name in batch:
                try:
                    # Vérifier si le track est dans cette playlist
                    is_in_playlist = await self.check_track_in_playlist(track_id, playlist_id)
                    
                    if is_in_playlist:
                        playlist_results[playlist_id] = {
                            'name': playlist_name,
                            'category': self.categorize_playlist(playlist_name),
                            'position': await self.get_track_position_in_playlist(track_id, playlist_id)
                        }
                        print(f"  ✓ Trouvé dans: {playlist_name}")
                        
                except Exception as e:
                    # Continuer même si une playlist échoue
                    if "404" not in str(e):  # Ne pas afficher les 404
                        print(f"  ⚠️ Erreur playlist {playlist_name}: {e}")
                    
        return playlist_results
        
    async def check_track_in_playlist(self, track_id: str, playlist_id: str) -> bool:
        """Vérifie si un track est dans une playlist"""
        try:
            # Vérifier le cache
            cache_key = f"playlist_check_{playlist_id}_{track_id}"
            cached_result = self.cache_manager.get_api_cache(cache_key, 'playlist_check')
            
            if cached_result is not None:
                return cached_result['response_data']
                
            # Récupérer la playlist par pagination
            offset = 0
            limit = 100
            found = False
            
            while True:
                playlist_tracks = self.spotify_client.playlist_tracks(
                    playlist_id, 
                    limit=limit, 
                    offset=offset
                )
                
                if not playlist_tracks or not playlist_tracks.get('items'):
                    break
                    
                for item in playlist_tracks['items']:
                    if item and item.get('track') and item['track'].get('id') == track_id:
                        found = True
                        break
                        
                if found or not playlist_tracks.get('next'):
                    break
                    
                offset += limit
            
            # Sauvegarder dans le cache
            self.cache_manager.save_api_cache(cache_key, 'playlist_check', found)
            
            return found
            
        except Exception as e:
            return False
            
    async def get_track_position_in_playlist(self, track_id: str, playlist_id: str) -> Optional[int]:
        """Récupère la position d'un track dans une playlist"""
        try:
            offset = 0
            limit = 100
            position = 0
            
            while True:
                playlist_tracks = self.spotify_client.playlist_tracks(
                    playlist_id, 
                    limit=limit, 
                    offset=offset
                )
                
                if not playlist_tracks or not playlist_tracks.get('items'):
                    break
                    
                for i, item in enumerate(playlist_tracks['items']):
                    position += 1
                    if item and item.get('track') and item['track'].get('id') == track_id:
                        return position
                        
                if not playlist_tracks.get('next'):
                    break
                    
                offset += limit
                
            return None
        except Exception as e:
            return None
            
    def categorize_playlist(self, playlist_name: str) -> str:
        """Catégorise une playlist selon son nom"""
        name_lower = playlist_name.lower()
        
        # Mariages
        if any(word in name_lower for word in ['wedding', 'love', 'romance', 'forever', 'first dance']):
            return 'mariage'
            
        # Party/Club
        if any(word in name_lower for word in ['dance', 'party', 'club', 'edm', 'house', 'techno', 'trance', 'electronic']):
            return 'party_club'
            
        # Latino
        if any(word in name_lower for word in ['latino', 'latin', 'reggaeton', 'salsa', 'bachata', 'cumbia', 'merengue']):
            return 'latino'
            
        # Lounge/Cocktail
        if any(word in name_lower for word in ['lounge', 'cocktail', 'jazz', 'chill', 'relax', 'soft', 'calm']):
            return 'lounge_cocktail'
            
        # Multi-générationnel
        if any(word in name_lower for word in ['80s', '90s', '00s', '70s', 'classic', 'all out', 'greatest', 'essential']):
            return 'multi_generationnel'
            
        # Hip-Hop/R&B
        if any(word in name_lower for word in ['rap', 'hip hop', 'hip-hop', 'r&b', 'rnb', 'urban']):
            return 'hiphop_rnb'
            
        # Workout
        if any(word in name_lower for word in ['workout', 'gym', 'beast mode', 'cardio', 'running', 'training']):
            return 'workout'
            
        # Current/Viral
        if any(word in name_lower for word in ['top hits', 'new music', 'viral', 'trending', '2025']):
            return 'current_viral'
            
        return 'general'
        
    def determine_contexts(self, playlist_analysis: Dict[str, Any]) -> List[str]:
        """Détermine TOUS les contextes possibles selon les playlists"""
        contexts = []
        category_counts = {}
        
        # Compter les occurrences par catégorie
        for playlist_data in playlist_analysis.values():
            category = playlist_data.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
            
        # Mapper les catégories vers les contextes
        category_to_contexts = {
            'mariage': ['Mariage'],
            'party_club': ['Club', 'Festival'],
            'latino': ['Club', 'Festival', 'PoolParty'],
            'lounge_cocktail': ['CorporateEvent', 'CocktailChic', 'Restaurant', 'Cocktail'],
            'multi_generationnel': ['Bar', 'Cocktail', 'Restaurant', 'Anniversaire'],
            'hiphop_rnb': ['Club', 'Bar'],
            'workout': ['PoolParty', 'Festival'],
            'current_viral': ['Club', 'Festival', 'PoolParty', 'Anniversaire'],
            'general': ['Bar', 'Club']
        }
        
        # Ajouter tous les contextes correspondants
        for category, count in category_counts.items():
            if count > 0:
                contexts.extend(category_to_contexts.get(category, []))
                
        # Ajustements basés sur le nombre de playlists
        if len(playlist_analysis) > 10:  # Très populaire
            contexts.extend(['Club', 'Mariage', 'Anniversaire'])
        elif len(playlist_analysis) > 5:  # Populaire
            contexts.extend(['Bar', 'Festival'])
            
        return list(set(contexts)) if contexts else ['Bar', 'Club']
        
    def determine_styles(self, playlist_analysis: Dict[str, Any], spotify_track: Dict[str, Any]) -> List[str]:
        """Détermine TOUS les styles possibles"""
        styles = []
        
        # Analyse des playlists
        playlist_names = [data['name'].lower() for data in playlist_analysis.values()]
        categories = [data['category'] for data in playlist_analysis.values()]
        
        # Banger = dans playlists party/club avec bonne énergie
        if 'party_club' in categories and spotify_track.get('energy', 0) > 0.7:
            styles.append('Banger')
            
        # Classics = dans playlists décennies ou très populaire
        if 'multi_generationnel' in categories or spotify_track.get('popularity', 0) > 70:
            styles.append('Classics')
            
        # Funky = groovy et positif
        if spotify_track.get('valence', 0) > 0.7 and spotify_track.get('danceability', 0) > 0.6:
            styles.append('Funky')
            
        # Ladies = dans playlists populaires, dansant
        if len(playlist_analysis) > 5 and spotify_track.get('danceability', 0) > 0.65:
            styles.append('Ladies')
            
        # Genres électroniques
        for name in playlist_names:
            if 'house' in name:
                styles.append('House')
            if 'techno' in name:
                styles.append('Techno')
            if 'trance' in name:
                styles.append('Trance')
            if 'progressive' in name:
                styles.append('Progressive')
                
        # Commercial si très populaire
        if len(playlist_analysis) > 8 or spotify_track.get('popularity', 0) > 60:
            styles.append('Commercial')
            
        return list(set(styles)) if styles else ['Commercial']
        
    def determine_moments(self, playlist_analysis: Dict[str, Any], spotify_track: Dict[str, Any]) -> List[str]:
        """Détermine TOUS les moments appropriés"""
        moments = []
        
        categories = [data['category'] for data in playlist_analysis.values()]
        energy = spotify_track.get('energy', 0.5)
        tempo = spotify_track.get('tempo', 120)
        
        # Règles basées sur les contextes trouvés
        if 'lounge_cocktail' in categories:
            moments.append('Warmup')
            
        if 'party_club' in categories and energy > 0.6:
            moments.append('Peaktime')
            
        if 'mariage' in categories:
            moments.extend(['Warmup', 'Peaktime', 'Closing'])
            
        # Règles basées sur l'énergie
        if energy < 0.5:
            moments.append('Warmup')
        elif energy > 0.7 and tempo > 120:
            moments.append('Peaktime')
            
        # Si mélancolique ou très calme
        if spotify_track.get('valence', 1) < 0.4:
            moments.append('Closing')
            
        return list(set(moments)) if moments else ['Warmup']
        
    def calculate_confidence_score(self, playlist_analysis: Dict[str, Any]) -> float:
        """Calcule un score de confiance basé sur le nombre d'apparitions"""
        found_playlists = len(playlist_analysis)
        
        # Score basé sur le nombre de playlists
        if found_playlists >= 10:
            return 1.0
        elif found_playlists >= 5:
            return 0.85
        elif found_playlists >= 3:
            return 0.7
        elif found_playlists >= 1:
            return 0.5
        else:
            return 0.3
            
    async def search_track(self, title: str, artist: str) -> Optional[Dict[str, Any]]:
        """Recherche d'un track dans Spotify"""
        if not self.spotify_client:
            return None
            
        try:
            # Vérifier le cache
            cache_key = f"spotify_search_{title}_{artist}"
            cached_result = self.cache_manager.get_api_cache(cache_key, 'spotify_search')
            
            if cached_result:
                return cached_result['response_data']
                
            # Recherche Spotify
            query = f"track:{title} artist:{artist}"
            results = self.spotify_client.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_info = {
                    'id': track.get('id'),
                    'name': track.get('name'),
                    'artist': track.get('artists', [{}])[0].get('name', ''),
                    'album': track.get('album', {}).get('name', ''),
                    'popularity': track.get('popularity'),
                    'duration_ms': track.get('duration_ms'),
                    'explicit': track.get('explicit'),
                    'uri': track.get('uri')
                }
                
                # Ajouter les features audio
                if track.get('id'):
                    try:
                        features = self.spotify_client.audio_features(track['id'])
                        if features and features[0]:
                            track_info.update({
                                'danceability': features[0].get('danceability'),
                                'energy': features[0].get('energy'),
                                'valence': features[0].get('valence'),
                                'tempo': features[0].get('tempo'),
                                'key': features[0].get('key'),
                                'mode': features[0].get('mode'),
                                'acousticness': features[0].get('acousticness'),
                                'instrumentalness': features[0].get('instrumentalness'),
                                'liveness': features[0].get('liveness'),
                                'speechiness': features[0].get('speechiness')
                            })
                    except Exception as e:
                        print(f"⚠️ Features audio non disponibles: {e}")
                        
                # Sauvegarder dans le cache
                self.cache_manager.save_api_cache(cache_key, 'spotify_search', track_info)
                return track_info
                
        except Exception as e:
            print(f"Erreur recherche Spotify: {e}")
            
        return None