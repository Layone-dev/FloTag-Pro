"""
Service d'orchestration de l'analyse des fichiers audio
Simule l'analyse avec des données de test
"""

import asyncio
import os
import random
from typing import Dict, Any, List
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

# Tenter d'importer d'autres formats si nécessaire
try:
    from mutagen.aiff import AIFF
except ImportError:
    AIFF = None # type: ignore
try:
    from mutagen.wave import WAVE
except ImportError:
    WAVE = None # type: ignore


class AnalysisOrchestrator:
    """
    Orchestre l'analyse des fichiers audio.
    Pour l'instant, retourne des données simulées.
    """
    
    def __init__(self):
        """Initialise l'orchestrateur."""
        self.genres = ["House", "Techno", "Disco", "Funk", "Soul", "Jazz", "Hip-Hop", "Electronic"]
        self.keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.modes = ["maj", "min"]
        
        # Tags prédéfinis pour les tests
        self.comment_tags_pool = [
            "#[Soirée] #[Warmup]", "#[Club] #[Peak Time]", "#[Sunset] #[Chill]",
            "#[After] #[Deep]", "#[Bar] #[Groovy]"
        ]
        
        self.grouping_tags_pool = [
            "#Groovy", "#Melancolique", "#Uplifting", "#Deep", "#Vocal",
            "#Instrumental", "#Classic", "#Modern", "#Underground", "#Commercial"
        ]
        
        self.countries = ["🇫🇷 France", "🇺🇸 USA", "🇬🇧 UK", "🇩🇪 Germany", "🇯🇵 Japan", "🇧🇷 Brazil", "🇪🇸 Spain"]

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyse un fichier audio et retourne les métadonnées.
        
        Args:
            file_path: Chemin vers le fichier audio
            
        Returns:
            Dictionnaire contenant toutes les métadonnées extraites et analysées
        """
        # Simuler un délai d'analyse (comme si on appelait une vraie API)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Extraire les métadonnées existantes du fichier
        existing_metadata = self._extract_existing_metadata(file_path)
        
        # Générer des données d'analyse simulées
        filename = os.path.basename(file_path)
        
        # Essayer d'extraire artiste et titre du nom de fichier
        try:
            artist, title = filename.rsplit(' - ', 1)
            title = os.path.splitext(title)[0]
        except ValueError:
            artist = existing_metadata.get('artist', 'Artiste Inconnu')
            title = existing_metadata.get('title', os.path.splitext(filename)[0])
        
        # Générer des tags simulés
        comment_tags = random.sample(self.comment_tags_pool, k=random.randint(1, 2))
        grouping_tags = random.sample(self.grouping_tags_pool, k=random.randint(2, 4))
        
        # Construire le résultat final
        result = {
            'file_path': file_path,
            'artist': existing_metadata.get('artist', artist),
            'title': existing_metadata.get('title', title),
            'album': existing_metadata.get('album', 'Album Inconnu'),
            'year': existing_metadata.get('year', random.randint(1980, 2024)),
            'genre': existing_metadata.get('genre', random.choice(self.genres)),
            'key': f"{random.choice(self.keys)}{random.choice(self.modes)}",
            'bpm': random.randint(90, 140),
            'energy': random.randint(3, 9),
            'comment_tags': comment_tags,
            'grouping_tags': grouping_tags,
            'comment': " ".join(comment_tags),
            'grouping': " ".join(grouping_tags),
            'label': f"{random.choice(self.countries)} | {'Sampled' if random.random() > 0.5 else 'Original'}",
            'artwork_bytes': existing_metadata.get('artwork_bytes', None),
            'is_modified': False
        }
        
        return result

    def _extract_existing_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extrait les métadonnées existantes d'un fichier audio.
        """
        metadata = {}
        audio = None
        try:
            # Essayer de charger le fichier avec le bon type
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.mp3':
                audio = MP3(file_path)
            elif ext == '.flac':
                audio = FLAC(file_path)
            elif AIFF and ext == '.aiff':
                audio = AIFF(file_path)
            elif WAVE and ext == '.wav':
                 audio = WAVE(file_path)
            else:
                return metadata

            if audio is not None:
                if 'TIT2' in audio: metadata['title'] = str(audio.get('TIT2'))
                if 'TPE1' in audio: metadata['artist'] = str(audio.get('TPE1'))
                if 'TALB' in audio: metadata['album'] = str(audio.get('TALB'))
                if 'TDRC' in audio: 
                    try: metadata['year'] = int(str(audio.get('TDRC')))
                    except (ValueError, TypeError): pass
                if 'TCON' in audio: metadata['genre'] = str(audio.get('TCON'))
                
                apic_tag = audio.get('APIC:')
                if apic_tag:
                    metadata['artwork_bytes'] = apic_tag.data
                    
        except Exception as e:
            # On capture toutes les erreurs possibles de mutagen et autres
            print(f"Erreur d'extraction (mock) pour {os.path.basename(file_path)}: {e}")
            
        return metadata 