#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification des playlists Spotify avec gestion UTF-8
"""

import os
import sys
import locale
from pathlib import Path

# Forcer l'encodage UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Configurer l'environnement
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Charger les variables d'environnement
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("❌ Spotipy n'est pas installé !")
    print("👉 Installez-le avec : pip install spotipy")
    sys.exit(1)


def test_simple():
    """Test simple et rapide"""
    print("🧪 TEST RAPIDE SPOTIFY")
    print("=" * 60)
    
    # Vérifier les clés
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Clés Spotify manquantes dans .env")
        return False
    
    print("✅ Clés trouvées")
    
    try:
        # Connexion
        auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth)
        print("✅ Connexion établie")
        
        # Test simple - pas de caractères spéciaux
        print("\n🔍 Test de recherche simple...")
        results = sp.search(q='track:Thriller artist:Michael Jackson', type='track', limit=1)
        
        if results and results['tracks']['items']:
            track = results['tracks']['items'][0]
            # Encoder proprement pour l'affichage
            track_name = track['name'].encode('utf-8', 'replace').decode('utf-8')
            artist_name = track['artists'][0]['name'].encode('utf-8', 'replace').decode('utf-8')
            print(f"✅ Trouvé : {track_name} by {artist_name}")
        else:
            print("❌ Aucun résultat")
            
        # Test d'une playlist officielle
        print("\n📋 Test d'une playlist officielle...")
        try:
            playlist = sp.playlist('37i9dQZF1DXcBWIGoYBM5M')  # Today's Top Hits
            if playlist:
                print(f"✅ Playlist OK : Today's Top Hits")
                print(f"   Followers : {playlist.get('followers', {}).get('total', 0):,}")
                return True
        except Exception as e:
            print(f"❌ Erreur playlist : {str(e).encode('utf-8', 'replace').decode('utf-8')}")
            
    except Exception as e:
        error_msg = str(e).encode('utf-8', 'replace').decode('utf-8')
        print(f"❌ Erreur : {error_msg}")
        
    return False


def main():
    """Fonction principale simplifiée"""
    # Info système
    print(f"🖥️  Encodage système : {sys.stdout.encoding}")
    print(f"🌍 Locale : {locale.getpreferredencoding()}")
    print("")
    
    # Test simple
    success = test_simple()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ SPOTIFY FONCTIONNE !")
        print("\n💡 Les playlists obsolètes seront ignorées automatiquement")
        print("   FloTag Pro utilisera les playlists officielles qui fonctionnent")
    else:
        print("❌ PROBLÈME DÉTECTÉ")
        print("\n💡 Solutions :")
        print("1. Vérifiez vos clés sur https://developer.spotify.com")
        print("2. Créez une nouvelle app Spotify si nécessaire")
        print("3. Assurez-vous que les clés sont bien dans le fichier .env")


if __name__ == "__main__":
    main()
