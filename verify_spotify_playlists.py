#!/usr/bin/env python3
"""
Script simplifié de vérification des playlists Spotify
Version autonome sans dépendances complexes
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Charger les variables d'environnement
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

# Import minimal de Spotify
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("❌ Spotipy n'est pas installé !")
    print("👉 Installez-le avec : pip install spotipy")
    sys.exit(1)


def get_spotify_client():
    """Crée un client Spotify"""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Clés Spotify non trouvées dans .env")
        print("👉 Configurez vos clés dans FloTag Pro")
        return None
    
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"❌ Erreur configuration Spotify: {e}")
        return None


def get_dj_playlists():
    """Retourne la liste des playlists DJ"""
    return {
        # === HITS ACTUELS & VIRAUX (15 playlists) ===
        "37i9dQZF1DXcBWIGoYBM5M": "Today's Top Hits",
        "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",
        "37i9dQZF1DX4JAvHpjipBk": "New Music Friday",
        "37i9dQZF1DX5dNi5DgQvGI": "Viral Hits",
        "37i9dQZF1DX2L0iB23Enbq": "Viral 50 - Global",
        "37i9dQZF1DX1HUbZS4LEyL": "Top 50 - Global",
        "37i9dQZF1DWUa8ZRTfalHk": "Pop Rising",
        "37i9dQZF1DX3LyU0mhfqgP": "Out Now",
        "37i9dQZF1DX4dyzvuaRJ0n": "mint",
        "37i9dQZF1DX6z20IXmBjWI": "Fresh Finds",
        "37i9dQZF1DWYNSm3Z3MxiM": "Teen Beats",
        "37i9dQZF1DX1T68DrcOyx8": "Internet People",
        "37i9dQZF1DWYkaDif7Ztbp": "African Heat",
        "37i9dQZF1DX2RxBh64BHjQ": "Most Necessary",
        
        # === PARTY & CLUB EDM (20 playlists) ===
        "37i9dQZF1DX4W3aJd5DPHk": "Dance Party",
        "37i9dQZF1DXa8NOEUWPn9W": "Housewerk",
        "37i9dQZF1DX0BcQWzuB7ZO": "Dance Hits",
        "37i9dQZF1DX8tZsk68tuDw": "Dance Rising",
        "37i9dQZF1DX7ZUug1ANKRP": "Main Stage",
        "37i9dQZF1DX6J5xfwh2tZF": "mint electronica",
        "37i9dQZF1DX5Q27plkaOQ3": "Progressive House",
        "37i9dQZF1DXa2PvUpywmrr": "Electronic Circus",
        "37i9dQZF1DX8Sz1gsYZdwj": "Techno Bunker",
        "37i9dQZF1DX0r3x8OtiwEM": "Bass Arcade",
        "37i9dQZF1DX65bVJnL18Wi": "Trance Mission",
        "37i9dQZF1DWZryfwmX88iC": "Deep House Relax",
        "37i9dQZF1DXbIeCB85KmYt": "Future House",
        "37i9dQZF1DX9XIFQuFvzM4": "Dancehall Official",
        "37i9dQZF1DX1F3MWdxBB2j": "Tech House",
        "37i9dQZF1DX8CopunbDxgW": "Tropical House",
        "37i9dQZF1DX0AMssoUKCz7": "Big Room House",
        "37i9dQZF1DXaXB8fQg7xif": "Dance Workout",
        "37i9dQZF1DX32NsLKyzScr": "Power Hour",
        "37i9dQZF1DX7EF8wVxBVhG": "Night Rider",
        
        # === MARIAGE & ROMANCE (15 playlists) ===
        "37i9dQZF1DX7gIoKXt0gmx": "Love Songs",
        "37i9dQZF1DX6mvEU1S6INL": "You & Me",
        "37i9dQZF1DXaKIA8E7WcJj": "Acoustic Love",
        "37i9dQZF1DX3YSRoSdA634": "Love Pop",
        "37i9dQZF1DX38lOuCqMjbY": "Wedding Songs",
        "37i9dQZF1DWTbCuAXgsVHO": "Wedding Party",
        "37i9dQZF1DX5IDTimEWoTd": "First Dance",
        "37i9dQZF1DWXmlLSKkfdAk": "Love Ballads",
        "37i9dQZF1DWVOMXLZpjGG3": "Romance Latino",
        "37i9dQZF1DX7F6T2n2fegs": "Forever Wedding Songs",
        "37i9dQZF1DWVUq1oQhxNVB": "Pop Wedding",
        "37i9dQZF1DWYm55bBJnBOi": "Love R&B",
        "37i9dQZF1DX1BzILRveYHb": "Country Wedding",
        "37i9dQZF1DX9wC1KY45plY": "Soul Wedding",
        "37i9dQZF1DXb9v9H5QRUi5": "Jazz Romance",
        
        # === LOUNGE & COCKTAIL (15 playlists) ===
        "37i9dQZF1DX4UkKv8ED8jp": "Jazz Vibes",
        "37i9dQZF1DWTvNyxOwkztu": "Lounge - Soft House",
        "37i9dQZF1DX0SM0LYsmbMT": "Jazz - Cocktails",
        "37i9dQZF1DX82Zzp6AKx64": "Deep House Relax",
        "37i9dQZF1DXbYM8nMdgG9S": "Café del Mar",
        "37i9dQZF1DX3Ogo9pFvBkY": "Chill Lounge",
        "37i9dQZF1DWV7EzJMK2FUI": "Jazz in the Background",
        "37i9dQZF1DX4sWSpwq3LiO": "Peaceful Piano",
        "37i9dQZF1DX1s9knjP51Oa": "Calm Vibes",
        "37i9dQZF1DWTwnEm1IYyoj": "Soft Rock",
        "37i9dQZF1DX6ziVCJnEm59": "Lush + Atmospheric",
        "37i9dQZF1DXc9xYI1NpQVf": "Sunset Chill",
        "37i9dQZF1DX2yvmlOdMYzV": "Chill Vibes",
        "37i9dQZF1DX889U0CL85jj": "Chill Tracks",
        "37i9dQZF1DWXe9gwrJXPSm": "Lo-Fi Beats",
        
        # === LATINO & REGGAETON (20 playlists) ===
        "37i9dQZF1DX10zKzsJ2jva": "Viva Latino",
        "37i9dQZF1DWYJ59NCcoilc": "Baila Reggaeton",
        "37i9dQZF1DWY7IeIP1cdjF": "Éxitos México",
        "37i9dQZF1DX1HUbZS4LEyL": "Latin Hits",
        "37i9dQZF1DXbLMw3ry7d7k": "Latin Party",
        "37i9dQZF1DX8SfyqmSFDwe": "Reggaeton Classics",
        "37i9dQZF1DX7F4ZDm7EKJp": "La Reina",
        "37i9dQZF1DWSpF87bP6JSF": "Novedades Viernes",
        "37i9dQZF1DX2apWzyECwyZ": "La Vida Loca",
        "37i9dQZF1DX7gIoKXt0gmx": "Cumbia Sonidera",
        "37i9dQZF1DWVcbCMNwfUyM": "Salsa Classics",
        "37i9dQZF1DX5GQZoaT6C4y": "Bachata Lovers",
        "37i9dQZF1DWTx0xog90XWm": "Merengue Total",
        "37i9dQZF1DX3E5bKAjp8rg": "Trap Latino",
        "37i9dQZF1DWNo0gst9Mwfj": "Perreo Intenso",
        "37i9dQZF1DX8FPV9C4MVP5": "Dembow",
        "37i9dQZF1DWXbLOeKQWLu1": "Tropical Morning",
        "37i9dQZF1DX7Ocjc6HVlQu": "Fiesta Latina",
        "37i9dQZF1DX3ND264N08pv": "Hits Urbano",
        "37i9dQZF1DX4osfY3zybD2": "Latin Workout",
    }


def verify_playlist(sp, playlist_id, playlist_name):
    """Vérifie une playlist individuelle"""
    try:
        playlist_info = sp.playlist(playlist_id, fields="id,name,tracks.total,followers.total")
        
        if playlist_info:
            return {
                'valid': True,
                'id': playlist_id,
                'name': playlist_info['name'],
                'tracks': playlist_info['tracks']['total'],
                'followers': playlist_info.get('followers', {}).get('total', 0)
            }
    except Exception as e:
        error_msg = str(e)
        return {
            'valid': False,
            'id': playlist_id,
            'name': playlist_name,
            'error': '404' if '404' in error_msg else error_msg[:50]
        }
    
    return {
        'valid': False,
        'id': playlist_id,
        'name': playlist_name,
        'error': 'Unknown'
    }


def main():
    """Fonction principale"""
    print("🔍 Vérification des playlists Spotify pour FloTag Pro")
    print("=" * 60)
    
    # Créer le client Spotify
    sp = get_spotify_client()
    if not sp:
        return
    
    print("✅ Client Spotify connecté")
    print("")
    
    # Récupérer les playlists
    playlists = get_dj_playlists()
    total = len(playlists)
    
    print(f"📋 Total de playlists à vérifier : {total}")
    print("-" * 60)
    
    # Vérifier chaque playlist
    valid_count = 0
    invalid_count = 0
    valid_playlists = []
    invalid_playlists = []
    
    for i, (playlist_id, playlist_name) in enumerate(playlists.items(), 1):
        result = verify_playlist(sp, playlist_id, playlist_name)
        
        if result['valid']:
            valid_count += 1
            valid_playlists.append(result)
            print(f"✅ [{i:3d}/{total}] {result['name'][:40]:<40} | {result['tracks']:>5} tracks | {result['followers']:>8} followers")
        else:
            invalid_count += 1
            invalid_playlists.append(result)
            if '404' in result['error']:
                print(f"❌ [{i:3d}/{total}] {result['name'][:40]:<40} | Playlist n'existe plus")
            else:
                print(f"❌ [{i:3d}/{total}] {result['name'][:40]:<40} | Erreur: {result['error']}")
    
    # Afficher le rapport
    print("\n" + "=" * 60)
    print("📊 RAPPORT DE VÉRIFICATION")
    print("=" * 60)
    
    print(f"\n✅ Playlists valides : {valid_count}/{total} ({valid_count/total*100:.1f}%)")
    print(f"❌ Playlists invalides : {invalid_count}/{total} ({invalid_count/total*100:.1f}%)")
    
    # Top 10 par followers
    print("\n📈 Top 10 des playlists par nombre de followers :")
    print("-" * 60)
    
    valid_playlists.sort(key=lambda x: x['followers'], reverse=True)
    for i, playlist in enumerate(valid_playlists[:10], 1):
        followers_m = playlist['followers'] / 1_000_000
        print(f"{i:2d}. {playlist['name'][:40]:<40} | {followers_m:>5.1f}M followers | {playlist['tracks']:>5} tracks")
    
    # Afficher les invalides
    if invalid_playlists:
        print(f"\n⚠️  {len(invalid_playlists)} playlists invalides trouvées")
        print("Ces playlists seront ignorées automatiquement par FloTag Pro")
    
    print("\n✨ Vérification terminée !")
    
    # Proposition de test
    print("\n" + "=" * 60)
    response = input("💡 Voulez-vous tester la recherche d'un morceau ? (o/N) : ")
    
    if response.lower() == 'o':
        test_search(sp)


def test_search(sp):
    """Test de recherche simple"""
    print("\n🎵 TEST DE RECHERCHE")
    print("-" * 60)
    
    artist = input("Entrez le nom de l'artiste : ")
    title = input("Entrez le titre du morceau : ")
    
    print(f"\n🔍 Recherche de '{artist} - {title}'...")
    
    try:
        results = sp.search(q=f'artist:{artist} track:{title}', type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            print(f"\n✅ Trouvé !")
            print(f"   Titre : {track['name']}")
            print(f"   Artiste : {track['artists'][0]['name']}")
            print(f"   Album : {track['album']['name']}")
            print(f"   Popularité : {track['popularity']}")
            
            # Récupérer les features
            features = sp.audio_features(track['id'])[0]
            if features:
                print(f"   Tempo : {features['tempo']:.0f} BPM")
                print(f"   Énergie : {features['energy']:.2f}")
                print(f"   Dansabilité : {features['danceability']:.2f}")
        else:
            print("❌ Aucun résultat trouvé")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    main()
