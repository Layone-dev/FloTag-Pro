#!/usr/bin/env python3
"""
Script pour créer automatiquement 50 playlists DJ sur ton compte Spotify
Ces playlists serviront de référence pour l'analyse FloTag Pro
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from datetime import datetime

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Authentification avec permissions
scope = "playlist-modify-public playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# Obtenir l'ID utilisateur
user_id = sp.current_user()['id']
print(f"👤 Création des playlists pour: {user_id}")

# Définir les playlists à créer
DJ_PLAYLISTS = {
    # MARIAGE (10 playlists)
    "DJ Mariage - Cérémonie": "Musiques douces pour l'entrée et la cérémonie",
    "DJ Mariage - Cocktail": "Ambiance lounge pour le vin d'honneur",
    "DJ Mariage - Dîner": "Background musical pour le repas",
    "DJ Mariage - Première Danse": "Slows et moments romantiques",
    "DJ Mariage - Party Time": "Hits pour faire danser tous les âges",
    "DJ Mariage - Classics": "Incontournables pour mariage",
    "DJ Mariage - Latino": "Salsa, bachata pour mariages",
    "DJ Mariage - Fin de Soirée": "Derniers slows et émotions",
    "DJ Mariage - Entrée Mariés": "Musiques épiques pour l'entrée",
    "DJ Mariage - Dance Floor": "Bangers pour enflammer la piste",
    
    # CLUB (10 playlists)
    "DJ Club - Warmup": "Montée progressive en début de soirée",
    "DJ Club - Peak Time": "Bangers pour le pic de la soirée",
    "DJ Club - EDM Hits": "Gros sons électro actuels",
    "DJ Club - House Selection": "Deep, tech, progressive house",
    "DJ Club - Hip Hop": "Rap et urban pour club",
    "DJ Club - Latino Club": "Reggaeton et latin urbain",
    "DJ Club - Commercial": "Hits radio version club",
    "DJ Club - Underground": "Sons pointus pour connaisseurs",
    "DJ Club - Closing Time": "Derniers morceaux avant fermeture",
    "DJ Club - Ladies Night": "Tubes qui font chanter les filles",
    
    # CORPORATE/COCKTAIL (8 playlists)
    "DJ Corporate - Accueil": "Ambiance pro décontractée",
    "DJ Corporate - Networking": "Background pour discussions",
    "DJ Corporate - Dîner Affaires": "Élégant et discret",
    "DJ Corporate - Awards": "Musiques de remise de prix",
    "DJ Cocktail - Lounge": "Ambiance feutrée et classe",
    "DJ Cocktail - Jazz Modern": "Nu jazz et acid jazz",
    "DJ Cocktail - Afterwork": "Décompression fin de journée",
    "DJ Cocktail - VIP": "Sélection premium et exclusive",
    
    # BAR/RESTAURANT (7 playlists)
    "DJ Bar - Happy Hour": "Ambiance décontractée 17h-20h",
    "DJ Bar - Soirée": "Montée progressive après 20h",
    "DJ Bar - Weekend": "Ambiance festive vendredi/samedi",
    "DJ Restaurant - Lunch": "Midi en douceur",
    "DJ Restaurant - Dîner": "Ambiance tamisée",
    "DJ Restaurant - Brunch": "Sunday vibes",
    "DJ Restaurant - Terrasse": "Soleil et bonne humeur",
    
    # ÉVÉNEMENTS SPÉCIAUX (8 playlists)
    "DJ Pool Party": "Summer hits et tropical house",
    "DJ Festival": "Gros sons pour plein air",
    "DJ Anniversaire": "Hits multi-générationnels",
    "DJ Nouvel An": "Compte à rebours et célébration",
    "DJ Halloween": "Dark et mystérieux",
    "DJ Noël Corporate": "Festif mais pro",
    "DJ Summer Party": "BBQ et plage",
    "DJ Graduation": "Fin d'études et célébration",
    
    # STYLES SPÉCIFIQUES (7 playlists)
    "DJ Funky Grooves": "Funk, disco, groove",
    "DJ French Touch": "House française et filter",
    "DJ Old School": "Classics 70s 80s 90s",
    "DJ Guilty Pleasures": "Tubes inavouables",
    "DJ Sing Along": "Tout le monde chante",
    "DJ Feel Good": "Bonne humeur garantie",
    "DJ Bangers Only": "Que des bombes"
}

# Créer les playlists
created_playlists = []
print(f"\n📝 Création de {len(DJ_PLAYLISTS)} playlists...\n")

for name, description in DJ_PLAYLISTS.items():
    try:
        # Créer la playlist
        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"🎵 {name}",
            public=True,
            description=f"{description} | FloTag Pro DJ System | Créé le {datetime.now().strftime('%d/%m/%Y')}"
        )
        
        created_playlists.append({
            'id': playlist['id'],
            'name': name,
            'url': playlist['external_urls']['spotify']
        })
        
        print(f"✅ Créé: {name}")
        print(f"   URL: {playlist['external_urls']['spotify']}")
        
    except Exception as e:
        print(f"❌ Erreur pour {name}: {e}")

# Sauvegarder les IDs des playlists
print(f"\n💾 Sauvegarde des IDs de playlists...\n")

with open('my_dj_playlists.py', 'w') as f:
    f.write('"""\nMes playlists DJ personnelles pour FloTag Pro\n"""\n\n')
    f.write('MY_DJ_PLAYLISTS = {\n')
    
    for pl in created_playlists:
        f.write(f'    "{pl["id"]}": "{pl["name"]}",\n')
    
    f.write('}\n')

print("✅ Fichier 'my_dj_playlists.py' créé avec tous les IDs")
print("\n🎉 Terminé ! Tu peux maintenant :")
print("1. Ajouter des morceaux dans ces playlists via Spotify")
print("2. Utiliser ces playlists dans FloTag Pro")
print("\n💡 Conseil : Ajoute au moins 20-50 morceaux par playlist pour une analyse pertinente")