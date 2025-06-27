"""
FlowTag Pro - Orchestrateur d'analyse musical intelligent
Version complète avec système de corrections intégré
Objectif : 100% de réussite sur le tagging DJ
"""

import asyncio
import os
import random
from typing import Dict, Any, Optional, List, Tuple, Set
from pathlib import Path
from datetime import datetime

# Imports avec gestion d'erreur
try:
    from .cache_manager import CacheManager
    from .spotify_async import SpotifyService
    from .gemini_service import GeminiDiscogsService as OpenAIDiscogsService
    from .discogs_service import DiscogsService
    from .tag_writer import TagWriter
    from .corrections_database import CorrectionsDatabase, SmartFallback
except ImportError as e:
    print(f"Import relatif échoué, essai en absolu : {e}")
    from cache_manager import CacheManager
    from spotify_async import SpotifyService
    from openai_with_discogs import OpenAIDiscogsService
    from discogs_service import DiscogsService
    from tag_writer import TagWriter
    from corrections_database import CorrectionsDatabase, SmartFallback

# Import des données
try:
    from ..data.countries_db import detect_country
    from ..data.genres_db import get_genre_contexts, FLOWTAG_GENRES
except ImportError:
    from data.countries_db import detect_country
    from data.genres_db import get_genre_contexts, FLOWTAG_GENRES

# Pour extraction des métadonnées existantes
from mutagen import File
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC


class AnalysisOrchestrator:
    """
    Orchestrateur intelligent pour l'analyse musicale DJ.
    Combine plusieurs sources (Spotify, Discogs, OpenAI) pour un tagging optimal.
    Intègre un système de corrections pour apprendre et s'améliorer.
    """

    def __init__(self):
        """Initialise l'orchestrateur avec tous les services."""
        self.cache_manager = CacheManager()
        
        # Initialiser les services
        self.spotify_service = SpotifyService(self.cache_manager)
        self.discogs_service = DiscogsService(self.cache_manager)
        self.openai_service = OpenAIDiscogsService(self.cache_manager)
        
        # Système de corrections intelligentes
        self.corrections_db = CorrectionsDatabase()
        self.smart_fallback = SmartFallback(self.corrections_db)
        print("✅ Système de corrections activé")
        
        # Vérifier la disponibilité des services
        self.check_services_availability()
        
        # Configuration des données de fallback
        self.setup_fallback_data()
        
        # Statistiques pour tracking
        self.stats = {
            'total_analyzed': 0,
            'successful_tags': 0,
            'api_hits': {'spotify': 0, 'discogs': 0, 'openai': 0},
            'corrections_used': 0
        }

    def check_services_availability(self):
        """Vérifie quels services API sont configurés et fonctionnels."""
        self.has_spotify = bool(os.getenv('SPOTIFY_CLIENT_ID')) and bool(os.getenv('SPOTIFY_CLIENT_SECRET'))
        self.has_discogs = bool(os.getenv('DISCOGS_TOKEN'))
        self.has_openai = bool(os.getenv('OPENAI_API_KEY'))
        
        print(f"\n🔧 FlowTag Pro - État des services:")
        print(f"  - Spotify: {'✅ Actif' if self.has_spotify else '❌ Inactif'}")
        print(f"  - Discogs: {'✅ Actif' if self.has_discogs else '❌ Inactif'}")
        print(f"  - OpenAI: {'✅ Actif' if self.has_openai else '❌ Inactif'}")
        print(f"  - Corrections DB: ✅ Actif ({len(self.corrections_db.corrections)} corrections)")
        
        if not any([self.has_spotify, self.has_discogs, self.has_openai]):
            print("\n⚠️  Mode OFFLINE : Analyse basique activée")
            print("💡 Conseil : Configurez au moins une API pour de meilleurs résultats")
        else:
            print(f"\n✨ Mode {'COMPLET' if all([self.has_spotify, self.has_discogs, self.has_openai]) else 'PARTIEL'}")

    def setup_fallback_data(self):
        """Configure les données de fallback pour le mode offline."""
        # Contextes possibles (sans Anniversaire, avec Generaliste)
        self.fallback_contexts = [
            'Bar', 'Club', 'Mariage', 'CorporateEvent', 'Restaurant', 
            'Generaliste', 'CocktailChic', 'PoolParty'
        ]
        
        # Moments DJ
        self.fallback_moments = ['Warmup', 'Peaktime', 'Closing']
        
        # Styles musicaux
        self.fallback_styles = [
            'Commercial', 'House', 'Funky', 'Classics', 'Ladies', 
            'Banger', 'Progressive', 'Deep', 'Tech', 'Vocal', 
            'Latino', 'HipHop', 'Minimal', 'Disco'
        ]
        
        # Clés Camelot
        self.fallback_keys = [
            '1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', 
            '5A', '5B', '6A', '6B', '7A', '7B', '8A', '8B', 
            '9A', '9B', '10A', '10B', '11A', '11B', '12A', '12B'
        ]

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyse complète d'un fichier audio avec toutes les sources disponibles.
        Utilise d'abord le système de corrections si disponible.
        
        Args:
            file_path: Chemin vers le fichier audio
            
        Returns:
            Dict contenant toutes les métadonnées analysées et les tags
        """
        self.stats['total_analyzed'] += 1
        filename = os.path.basename(file_path)
        
        print(f"\n{'='*60}")
        print(f"🎵 Analyse de : {filename}")
        print(f"{'='*60}")
        
        # 1. Extraction des métadonnées existantes
        existing_metadata = self._extract_existing_metadata(file_path)
        
        # 2. Parser le nom du fichier intelligemment
        parsed_info = self._parse_filename(filename, existing_metadata)
        artist = parsed_info['artist']
        title = parsed_info['title']
        
        # 2.5 Vérifier d'abord la base de corrections
        correction_result = self.smart_fallback.analyze_with_corrections(
            artist, title, existing_metadata
        )
        
        if correction_result and correction_result['confidence'] >= 0.7:
            print(f"🎯 Utilisation de la base de corrections (confiance: {correction_result['confidence']:.0%})")
            self.stats['corrections_used'] += 1
            
            # Si on a une correction avec haute confiance, l'utiliser directement
            if correction_result['confidence'] >= 0.9:
                return self._build_result_from_correction(
                    file_path, parsed_info, correction_result['data'], existing_metadata
                )
        
        # 3. Préparer les métadonnées initiales
        initial_metadata = {
            'artist': artist,
            'title': title,
            'album': existing_metadata.get('album', ''),
            'year': existing_metadata.get('year', ''),
            'genre': existing_metadata.get('genre', ''),
            'file_path': file_path
        }
        
        # Si on a des infos de correction mais pas assez de confiance, les utiliser comme base
        if correction_result:
            correction_data = correction_result['data']
            initial_metadata['genre'] = correction_data.get('genre', initial_metadata['genre'])
        
        # 4. Vérifier le cache
        cache_key = f"full_analysis_v5_{artist}_{title}"
        cached_result = self.cache_manager.get_api_cache(cache_key, 'full_analysis')
        if cached_result and cached_result.get('response_data'):
            print(f"✅ Résultat trouvé dans le cache")
            return cached_result['response_data']
        
        # 5. Lancer les analyses en parallèle
        spotify_analysis = {}
        discogs_data = {}
        gpt_analysis = {}
        
        # Analyse Spotify
        if self.has_spotify:
            try:
                print(f"\n🔎 Recherche Spotify...")
                spotify_analysis = await self.spotify_service.analyze_track_in_playlists(initial_metadata)
                if spotify_analysis.get('spotify_track'):
                    self.stats['api_hits']['spotify'] += 1
                    print(f"  ✅ Trouvé sur Spotify")
            except Exception as e:
                print(f"  ⚠️ Erreur Spotify : {e}")
        
        # Récupération Discogs
        if self.has_discogs:
            try:
                print(f"\n💿 Recherche Discogs...")
                discogs_data = await self.discogs_service.get_discogs_info_and_artwork(artist, title)
                if discogs_data.get('year'):
                    self.stats['api_hits']['discogs'] += 1
                    print(f"  ✅ Infos Discogs récupérées")
            except Exception as e:
                print(f"  ⚠️ Erreur Discogs : {e}")
        
        # Analyse OpenAI
        if self.has_openai:
            try:
                print(f"\n🤖 Analyse IA...")
                gpt_analysis = await self.openai_service.analyze_track_dj(
                    initial_metadata,
                    spotify_analysis,
                    discogs_data
                )
                if gpt_analysis.get('genre'):
                    self.stats['api_hits']['openai'] += 1
                    print(f"  ✅ Analyse IA complétée")
            except Exception as e:
                print(f"  ⚠️ Erreur OpenAI : {e}")
        
        # 6. Compiler l'analyse finale
        if not any([spotify_analysis, discogs_data, gpt_analysis]):
            print(f"\n🎲 Mode fallback activé")
            final_analysis = self._generate_fallback_analysis(file_path, initial_metadata, existing_metadata)
        else:
            # Enrichir avec les données de correction si disponibles
            if correction_result:
                spotify_analysis = self._enrich_with_correction_data(
                    spotify_analysis, correction_result['data']
                )
            
            final_analysis = self._compile_final_analysis(
                file_path,
                initial_metadata,
                spotify_analysis,
                gpt_analysis,
                discogs_data,
                existing_metadata
            )
        
        # 7. Sauvegarder dans le cache
        self.cache_manager.save_api_cache(cache_key, 'full_analysis', final_analysis)
        
        # 8. Calculer le taux de réussite
        if self._evaluate_analysis_quality(final_analysis):
            self.stats['successful_tags'] += 1
        
        # 9. Afficher les statistiques
        success_rate = (self.stats['successful_tags'] / self.stats['total_analyzed']) * 100
        print(f"\n📊 Statistiques :")
        print(f"  - Taux de réussite : {success_rate:.1f}%")
        print(f"  - Corrections utilisées : {self.stats['corrections_used']}")
        
        # 10. Proposer de sauvegarder si confiance faible
        if final_analysis.get('confidence_score', 0) < 0.7:
            print(f"\n💡 Confiance faible ({final_analysis.get('confidence_score', 0):.2f})")
            print("   → Vérifiez les tags et sauvegardez une correction si nécessaire")
        
        return final_analysis

    def _build_result_from_correction(self, file_path: str, parsed_info: Dict, 
                                    correction_data: Dict, existing_metadata: Dict) -> Dict[str, Any]:
        """Construit le résultat final depuis les données de correction."""
        # Utiliser les données de correction comme base
        artist = correction_data.get('artist', parsed_info['artist'])
        title = correction_data.get('title', parsed_info['title'])
        
        # Construire les tags
        contexts = correction_data.get('contexts', ['Bar', 'Club'])
        moments = correction_data.get('moments', ['Warmup'])
        styles = correction_data.get('styles', ['Commercial'])
        
        # Générer les paires contexte-moment
        comment_tags = []
        for context in contexts:
            for moment in moments:
                comment_tags.append(f"#[{context}] #[{moment}]")
        
        grouping_tags = [f"#{style}" for style in styles]
        
        # Détection du pays
        country_info = detect_country(artist)
        country_str = f"{country_info[0]} {country_info[1]}"
        
        return {
            'file_path': file_path,
            'artist': artist,
            'title': title,
            'album': correction_data.get('album', ''),
            'year': str(correction_data.get('year', '')),
            'genre': correction_data.get('genre', ''),
            'key': correction_data.get('key', ''),
            'bpm': str(correction_data.get('bpm', '')),
            'energy': correction_data.get('energy', 5),
            'comment_tags': comment_tags,
            'grouping_tags': grouping_tags,
            'comment': ' '.join(comment_tags),
            'grouping': ' '.join(grouping_tags),
            'label': correction_data.get('country', country_str),
            'artwork_bytes': existing_metadata.get('artwork_bytes'),
            'has_artwork': bool(existing_metadata.get('artwork_bytes')),
            'is_modified': False,
            'confidence_score': 1.0,  # Confiance maximale pour les corrections
            'source': 'corrections_db'
        }

    def _enrich_with_correction_data(self, spotify_analysis: Dict, correction_data: Dict) -> Dict:
        """Enrichit l'analyse Spotify avec les données de correction."""
        if not spotify_analysis.get('contexts'):
            spotify_analysis['contexts'] = correction_data.get('contexts', [])
        if not spotify_analysis.get('moments'):
            spotify_analysis['moments'] = correction_data.get('moments', [])
        if not spotify_analysis.get('styles'):
            spotify_analysis['styles'] = correction_data.get('styles', [])
        return spotify_analysis

    def _parse_filename(self, filename: str, existing_metadata: Dict) -> Dict[str, str]:
        """
        Parse intelligent du nom de fichier pour extraire artiste et titre.
        Gère les formats courants et les cas spéciaux.
        """
        # Enlever l'extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Si on a déjà des métadonnées, les utiliser en priorité
        if existing_metadata.get('artist') and existing_metadata.get('title'):
            return {
                'artist': existing_metadata['artist'],
                'title': existing_metadata['title']
            }
        
        # Patterns courants à essayer
        patterns = [
            # "Artiste - Titre (Remix)"
            r'^(.+?)\s*-\s*(.+?)(?:\s*\(.*\))?$',
            # "Artiste_-_Titre"
            r'^(.+?)_-_(.+?)$',
            # "01. Artiste - Titre"
            r'^\d+\.?\s*(.+?)\s*-\s*(.+?)$',
            # "Artiste - Titre [Label]"
            r'^(.+?)\s*-\s*(.+?)(?:\s*\[.*\])?$',
        ]
        
        import re
        for pattern in patterns:
            match = re.match(pattern, name_without_ext)
            if match:
                return {
                    'artist': match.group(1).strip(),
                    'title': match.group(2).strip()
                }
        
        # Cas par défaut : pas de séparateur trouvé
        return {
            'artist': existing_metadata.get('artist', 'Unknown Artist'),
            'title': existing_metadata.get('title', name_without_ext)
        }

    def _extract_existing_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extraction complète des métadonnées existantes d'un fichier audio."""
        metadata = {}
        
        try:
            audio = File(file_path)
            if audio is None:
                return metadata
            
            # Mapping des tags ID3
            tag_mapping = {
                'TIT2': 'title',
                'TPE1': 'artist',
                'TALB': 'album',
                'TDRC': 'year',
                'TCON': 'genre',
                'TKEY': 'key',
                'TBPM': 'bpm',
                'COMM': 'comment',
                'GRP1': 'grouping',
                'TPUB': 'label',
                'TPE2': 'album_artist',
                'TPOS': 'disc_number',
                'TRCK': 'track_number'
            }
            
            # Extraire tous les tags disponibles
            for tag_id, field_name in tag_mapping.items():
                if tag_id in audio:
                    value = str(audio[tag_id])
                    if field_name == 'year':
                        # Extraire juste l'année (YYYY)
                        try:
                            metadata[field_name] = value[:4]
                        except:
                            metadata[field_name] = value
                    elif field_name in ['bpm', 'disc_number', 'track_number']:
                        # Nettoyer les valeurs numériques
                        try:
                            metadata[field_name] = str(int(float(value)))
                        except:
                            metadata[field_name] = value
                    else:
                        metadata[field_name] = value
            
            # Récupérer la pochette si présente
            if 'APIC:' in audio:
                try:
                    metadata['artwork_bytes'] = audio['APIC:'].data
                    metadata['has_artwork'] = True
                except:
                    metadata['has_artwork'] = False
                    
        except Exception as e:
            print(f"⚠️ Erreur extraction métadonnées : {e}")
        
        return metadata

    def detect_genre_from_title_and_artist(self, title: str, artist: str = '') -> str:
        """
        Détection intelligente du genre basée sur le titre et l'artiste.
        Utilise des mots-clés et patterns spécifiques.
        """
        # Combiner titre et artiste en minuscules
        combined = f"{title.lower()} {artist.lower()}"
        
        # Base de détection par mots-clés (ordre = priorité)
        genre_keywords = {
            'Reggaeton': [
                'reggaeton', 'reggaetón', 'perreo', 'dembow', 
                'kuduro', 'gasolina', 'bellaqueo', 'sandungueo'
            ],
            'Latin': [
                'salsa', 'bachata', 'merengue', 'cumbia', 
                'vallenato', 'banda', 'mariachi', 'tango'
            ],
            'Hip-Hop': [
                'hip hop', 'hip-hop', 'rap', 'trap', 'freestyle', 
                'boom bap', 'drill', 'grime', 'old school'
            ],
            'House': [
                'house', 'deep house', 'tech house', 'progressive house',
                'funky house', 'soulful house', 'tribal house', 'jackin'
            ],
            'Techno': [
                'techno', 'minimal', 'acid', 'detroit', 'berlin',
                'industrial', 'hard techno', 'melodic techno'
            ],
            'Drum & Bass': [
                'drum and bass', 'drum & bass', 'dnb', 'd&b',
                'jungle', 'liquid', 'neurofunk', 'jump up'
            ],
            'Dancehall': [
                'dancehall', 'ragga', 'bashment', 'riddim',
                'dutty wine', 'bubble', 'wine'
            ],
            'Afrobeat': [
                'afrobeat', 'afrobeats', 'afro', 'amapiano',
                'gqom', 'azonto', 'kizomba', 'kuduro'
            ],
            'Pop': [
                'pop', 'mainstream', 'chart', 'hit single',
                'radio edit', 'top 40'
            ],
            'Rock': [
                'rock', 'metal', 'punk', 'grunge', 'indie',
                'alternative', 'classic rock', 'hard rock'
            ],
            'R&B': [
                'r&b', 'rnb', 'soul', 'neo soul', 'contemporary r&b',
                'rhythm and blues', 'slow jam'
            ],
            'Funk': [
                'funk', 'funky', 'groove', 'p-funk', 'g-funk',
                'boogie', 'electro funk'
            ],
            'Disco': [
                'disco', 'nu disco', 'nu-disco', 'italo disco',
                'space disco', 'disco house', 'filter house'
            ],
            'Jazz': [
                'jazz', 'swing', 'bebop', 'smooth jazz',
                'acid jazz', 'fusion', 'bossa nova'
            ],
            'Electronic': [
                'electronic', 'edm', 'electro', 'synth',
                'future bass', 'dubstep', 'breaks'
            ]
        }
        
        # Vérifier d'abord si on connaît l'artiste
        artist_info = self.corrections_db.get_artist_info(artist)
        if artist_info:
            return artist_info['genre']
        
        # Sinon, vérifier chaque genre par mots-clés
        for genre, keywords in genre_keywords.items():
            for keyword in keywords:
                if keyword in combined:
                    return genre
        
        # Détection par patterns de remix
        if any(pattern in combined for pattern in ['remix', 'bootleg', 'edit', 'rework']):
            # Essayer de détecter le genre du remix
            if 'house' in combined or 'club' in combined:
                return 'House'
            elif 'techno' in combined:
                return 'Techno'
            elif 'trap' in combined:
                return 'Hip-Hop'
        
        return ''

    def _compile_final_analysis(self, file_path: str, metadata: Dict, 
                               spotify_analysis: Dict, gpt_analysis: Dict, 
                               discogs_data: Dict, existing_metadata: Dict) -> Dict[str, Any]:
        """
        Compile toutes les analyses en un résultat final optimisé.
        Utilise une hiérarchie de confiance pour chaque donnée.
        """
        # Récupérer les infos Spotify
        spotify_track = spotify_analysis.get('spotify_track', {})
        
        # === INFORMATIONS DE BASE ===
        # Hiérarchie : Métadonnées existantes > Spotify > Discogs > GPT > Nom fichier
        
        artist = (
            existing_metadata.get('artist') or 
            spotify_track.get('artist') or 
            discogs_data.get('artist') or 
            metadata.get('artist', 'Unknown Artist')
        )
        
        title = (
            existing_metadata.get('title') or 
            spotify_track.get('name') or 
            discogs_data.get('title') or 
            metadata.get('title', 'Unknown Title')
        )
        
        album = (
            existing_metadata.get('album') or 
            spotify_track.get('album') or 
            discogs_data.get('album', '')
        )
        
        # Année : Discogs est généralement plus fiable pour les dates
        year = discogs_data.get('year') or existing_metadata.get('year') or ''
        if not year and spotify_track.get('album_release_date'):
            year = str(spotify_track.get('album_release_date', ''))[:4]
        
        # === GENRE (DETECTION MULTI-SOURCES) ===
        genre = (
            existing_metadata.get('genre') or
            gpt_analysis.get('genre') or
            self.detect_genre_from_title_and_artist(title, artist) or
            (discogs_data.get('genre', [''])[0] if discogs_data.get('genre') else '') or
            self._guess_genre_from_spotify_data(spotify_analysis) or
            ''
        )
        
        # Normaliser le genre si on a un alias
        genre = self.corrections_db.normalize_genre(genre)
        
        # === ANALYSE TECHNIQUE ===
        # BPM
        bpm = existing_metadata.get('bpm') or gpt_analysis.get('bpm') or ''
        if not bpm and spotify_track.get('tempo'):
            bpm = str(int(round(spotify_track.get('tempo', 0))))
        
        # Énergie (0-10)
        energy = gpt_analysis.get('energy', 5)
        if not energy and spotify_track.get('energy'):
            energy = int(spotify_track.get('energy', 0.5) * 10)
        
        # Clé musicale (notation Camelot)
        key = (
            existing_metadata.get('key') or 
            gpt_analysis.get('key') or 
            self._convert_spotify_key(spotify_track.get('key'), spotify_track.get('mode'))
        )
        
        # === TAGS CONTEXTUELS ===
        # Récupération des tags de base depuis Spotify
        contexts = list(set(spotify_analysis.get('contexts', ['Bar', 'Club'])))
        moments = list(set(spotify_analysis.get('moments', ['Warmup'])))
        styles = list(set(spotify_analysis.get('styles', ['Commercial'])))
        
        # Enrichissement basé sur les caractéristiques audio
        if spotify_track:
            contexts, moments, styles = self._enrich_tags_from_audio_features(
                contexts, moments, styles, spotify_track, genre, year
            )
        
        # Enrichissement depuis l'analyse GPT
        if gpt_analysis.get('context_moment_pairs'):
            for context, moment in gpt_analysis['context_moment_pairs']:
                clean_context = context.replace('#', '').replace('[', '').replace(']', '').strip()
                clean_moment = moment.replace('#', '').replace('[', '').replace(']', '').strip()
                if clean_context and clean_context not in contexts:
                    contexts.append(clean_context)
                if clean_moment and clean_moment not in moments:
                    moments.append(clean_moment)
        
        if gpt_analysis.get('additional_styles'):
            for style in gpt_analysis['additional_styles']:
                clean_style = style.replace('#', '').strip()
                if clean_style and clean_style not in styles:
                    styles.append(clean_style)
        
        # Ajustements selon le genre détecté
        styles = self._adjust_styles_by_genre(styles, genre)
        
        # === CONSTRUCTION DES TAGS FINAUX ===
        # Limitation intelligente du nombre de tags
        contexts = contexts[:5]  # Max 5 contextes
        moments = moments[:3]    # Max 3 moments
        styles = styles[:6]      # Max 6 styles
        
        # Debug pour voir l'analyse
        print("\n🔍 Résultat de l'analyse :")
        print(f"  🎤 Artiste: {artist}")
        print(f"  🎵 Titre: {title}")
        print(f"  🎸 Genre: {genre}")
        print(f"  🎹 BPM: {bpm} | Key: {key} | Energy: {energy}/10")
        print(f"  📍 Contextes: {contexts}")
        print(f"  ⏰ Moments: {moments}")
        print(f"  🎨 Styles: {styles}")
        
        # Construire les paires contexte-moment
        comment_tags = []
        for context in contexts:
            for moment in moments:
                comment_tags.append(f"#[{context}] #[{moment}]")
        
        # Limiter à 10 combinaisons maximum (les plus pertinentes)
        if len(comment_tags) > 10:
            # Prioriser certaines combinaisons
            priority_combos = []
            other_combos = []
            
            for tag in comment_tags:
                if any(priority in tag for priority in ['Peaktime', 'Club', 'Generaliste']):
                    priority_combos.append(tag)
                else:
                    other_combos.append(tag)
            
            comment_tags = priority_combos[:6] + other_combos[:4]
        
        # Tags de style avec hashtag
        grouping_tags = [f"#{style}" for style in styles]
        
        # === INFORMATIONS SUPPLEMENTAIRES ===
        # Détection du pays
        country_info = detect_country(artist)
        country_str = f"{country_info[0]} {country_info[1]}"
        
        # Label avec infos de sample
        sample_info = gpt_analysis.get('sample_info')
        label_parts = [country_str]
        if sample_info and sample_info not in ['null', 'None', 'Unknown', '']:
            label_parts.append(f"Sample: {sample_info}")
        label = " | ".join(label_parts)
        
        # Pochette
        artwork_bytes = existing_metadata.get('artwork_bytes') or discogs_data.get('artwork_bytes')
        
        # Affichage final des tags
        print(f"\n🏷️ Tags finaux :")
        print(f"  📝 Comment: {' '.join(comment_tags[:3])}...")
        print(f"  🎯 Grouping: {' '.join(grouping_tags)}")
        print(f"  🌍 Label: {label}")
        
        # === RESULTAT FINAL ===
        return {
            'file_path': file_path,
            'artist': artist,
            'title': title,
            'album': album,
            'year': str(year),
            'genre': genre,
            'key': key,
            'bpm': str(bpm) if bpm else '',
            'energy': energy,
            'comment_tags': comment_tags,
            'grouping_tags': grouping_tags,
            'comment': ' '.join(comment_tags),
            'grouping': ' '.join(grouping_tags),
            'label': label,
            'artwork_bytes': artwork_bytes,
            'has_artwork': bool(artwork_bytes),
            'is_modified': False,
            'confidence_score': self._calculate_confidence_score(
                spotify_track, discogs_data, gpt_analysis
            )
        }

    def _enrich_tags_from_audio_features(self, contexts: List[str], moments: List[str], 
                                       styles: List[str], spotify_track: Dict, 
                                       genre: str, year: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Enrichit les tags basés sur les caractéristiques audio Spotify.
        Logique intelligente basée sur de vraies pratiques DJ.
        """
        # Récupérer les features
        popularity = spotify_track.get('popularity', 0)
        danceability = spotify_track.get('danceability', 0)
        energy = spotify_track.get('energy', 0)
        valence = spotify_track.get('valence', 0.5)  # Positivité
        tempo = spotify_track.get('tempo', 120)
        
        # === ENRICHISSEMENT DES CONTEXTES ===
        
        # Hits très populaires → Mariage & Corporate
        if popularity > 70:
            if 'Mariage' not in contexts:
                contexts.append('Mariage')
            if popularity > 80 and 'CorporateEvent' not in contexts:
                contexts.append('CorporateEvent')
        
        # Très dansant → PoolParty
        if danceability > 0.75 and energy > 0.6:
            if 'PoolParty' not in contexts:
                contexts.append('PoolParty')
        
        # Énergique + Populaire → Generaliste
        if energy > 0.7 and popularity > 65:
            if 'Generaliste' not in contexts:
                contexts.append('Generaliste')
        
        # Ambiance lounge/chill
        if energy < 0.5 and tempo < 110:
            if 'CocktailChic' not in contexts:
                contexts.append('CocktailChic')
            if 'Restaurant' not in contexts:
                contexts.append('Restaurant')
        
        # === ENRICHISSEMENT DES MOMENTS ===
        
        # Très énergique → Peaktime
        if energy > 0.8 or (energy > 0.7 and tempo > 128):
            if 'Peaktime' not in moments:
                moments.append('Peaktime')
        
        # Calme ou lent → Warmup/Closing
        if energy < 0.6 or tempo < 115:
            if 'Warmup' not in moments:
                moments.append('Warmup')
            if energy < 0.4 and 'Closing' not in moments:
                moments.append('Closing')
        
        # === ENRICHISSEMENT DES STYLES ===
        
        # Classique (ancien et toujours populaire)
        if year:
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if year_int < (current_year - 5) and popularity > 60:
                    if 'Classics' not in styles:
                        styles.append('Classics')
                    # Les vrais classiques passent en mariage
                    if year_int < (current_year - 10) and 'Mariage' not in contexts:
                        contexts.append('Mariage')
            except:
                pass
        
        # Banger (très énergique et populaire)
        if energy > 0.85 and popularity > 70:
            if 'Banger' not in styles:
                styles.append('Banger')
        
        # Ladies (positif, dansant, populaire)
        if valence > 0.7 and danceability > 0.7 and popularity > 65:
            if 'Ladies' not in styles:
                styles.append('Ladies')
        
        # Vocal (détection basique)
        if genre in ['Pop', 'R&B', 'Soul'] and 'Vocal' not in styles:
            styles.append('Vocal')
        
        # Deep/Tech (BPM et énergie spécifiques)
        if 118 <= tempo <= 128:
            if energy < 0.7 and 'Deep' not in styles:
                styles.append('Deep')
            elif energy > 0.8 and 'Tech' not in styles:
                styles.append('Tech')
        
        return contexts, moments, styles

    def _adjust_styles_by_genre(self, styles: List[str], genre: str) -> List[str]:
        """Ajuste les styles selon le genre détecté."""
        genre_lower = genre.lower()
        
        # Ajouts automatiques selon le genre
        if any(g in genre_lower for g in ['reggaeton', 'latin', 'salsa', 'bachata']):
            if 'Latino' not in styles:
                styles.append('Latino')
        
        if any(g in genre_lower for g in ['hip-hop', 'hip hop', 'rap', 'trap']):
            if 'HipHop' not in styles:
                styles.append('HipHop')
        
        if 'house' in genre_lower:
            if 'House' not in styles:
                styles.append('House')
        
        if 'disco' in genre_lower and 'Disco' not in styles:
            styles.append('Disco')
        
        if 'funk' in genre_lower and 'Funky' not in styles:
            styles.append('Funky')
        
        return styles

    def _generate_fallback_analysis(self, file_path: str, metadata: Dict, 
                                  existing_metadata: Dict) -> Dict[str, Any]:
        """
        Génère une analyse de fallback intelligente sans APIs.
        Utilise toutes les informations disponibles localement.
        """
        print("\n🎯 Analyse fallback intelligente...")
        
        # Récupérer les infos de base
        artist = existing_metadata.get('artist') or metadata.get('artist', 'Unknown Artist')
        title = existing_metadata.get('title') or metadata.get('title', 'Unknown Title')
        album = existing_metadata.get('album', '')
        year = existing_metadata.get('year', '')
        
        # Détection du genre (utilise la base de corrections)
        genre = (
            existing_metadata.get('genre') or 
            self.detect_genre_from_title_and_artist(title, artist) or 
            'Electronic'  # Défaut pour un DJ
        )
        
        # Détection du pays
        country_info = detect_country(artist)
        country_str = f"{country_info[0]} {country_info[1]}"
        
        # En mode fallback, on fait simple mais intelligent
        # Sélection basée sur le genre détecté
        if genre.lower() in ['reggaeton', 'latin']:
            contexts = ['Bar', 'Club', 'PoolParty']
            moments = ['Warmup', 'Peaktime']
            styles = ['Latino', 'Commercial', 'Banger']
            energy = random.randint(7, 9)
        elif 'house' in genre.lower():
            contexts = ['Club', 'Bar']
            moments = ['Warmup', 'Peaktime']
            styles = ['House', 'Commercial']
            energy = random.randint(6, 8)
        elif 'hip' in genre.lower() or 'rap' in genre.lower():
            contexts = ['Bar', 'Club']
            moments = ['Warmup', 'Peaktime']
            styles = ['HipHop', 'Commercial']
            energy = random.randint(6, 8)
        else:
            # Défaut générique
            contexts = random.sample(self.fallback_contexts, k=min(3, len(self.fallback_contexts)))
            moments = random.sample(self.fallback_moments, k=2)
            styles = random.sample(self.fallback_styles, k=3)
            energy = random.randint(5, 8)
        
        # Ajout du style Latino si c'est détecté
        if any(g in genre.lower() for g in ['reggaeton', 'latin', 'salsa']) and 'Latino' not in styles:
            styles.append('Latino')
        
        # Génération des paires contexte-moment
        comment_tags = []
        for context in contexts[:3]:
            for moment in moments[:2]:
                comment_tags.append(f"#[{context}] #[{moment}]")
        
        grouping_tags = [f"#{style}" for style in styles]
        
        # BPM estimation selon le genre
        bpm = existing_metadata.get('bpm', '')
        if not bpm:
            bpm_ranges = {
                'house': (120, 130),
                'techno': (125, 135),
                'hip': (80, 100),
                'trap': (140, 160),
                'drum': (170, 180),
                'reggaeton': (90, 105),
                'latin': (100, 130)
            }
            
            # Chercher une correspondance
            for genre_key, (min_bpm, max_bpm) in bpm_ranges.items():
                if genre_key in genre.lower():
                    bpm = str(random.randint(min_bpm, max_bpm))
                    break
            
            if not bpm:
                bpm = str(random.randint(100, 140))
        
        # Key aléatoire si pas présente
        key = existing_metadata.get('key') or random.choice(self.fallback_keys)
        
        return {
            'file_path': file_path,
            'artist': artist,
            'title': title,
            'album': album,
            'year': year,
            'genre': genre,
            'key': key,
            'bpm': bpm,
            'energy': energy,
            'comment_tags': comment_tags,
            'grouping_tags': grouping_tags,
            'comment': ' '.join(comment_tags),
            'grouping': ' '.join(grouping_tags),
            'label': country_str,
            'artwork_bytes': existing_metadata.get('artwork_bytes'),
            'has_artwork': bool(existing_metadata.get('artwork_bytes')),
            'is_modified': False,
            'confidence_score': 0.3  # Score faible en fallback
        }

    def _convert_spotify_key(self, key_num: Optional[int], mode: Optional[int]) -> str:
        """Convertit la clé Spotify (0-11) en notation Camelot."""
        if key_num is None:
            return ""
        
        # Mapping Spotify vers Camelot
        camelot_keys = {
            # Majeur (mode=1)
            (0, 1): "8B",   # C major
            (1, 1): "3B",   # C# major
            (2, 1): "10B",  # D major
            (3, 1): "5B",   # Eb major
            (4, 1): "12B",  # E major
            (5, 1): "7B",   # F major
            (6, 1): "2B",   # F# major
            (7, 1): "9B",   # G major
            (8, 1): "4B",   # Ab major
            (9, 1): "11B",  # A major
            (10, 1): "6B",  # Bb major
            (11, 1): "1B",  # B major
            # Mineur (mode=0)
            (0, 0): "5A",   # C minor
            (1, 0): "12A",  # C# minor
            (2, 0): "7A",   # D minor
            (3, 0): "2A",   # Eb minor
            (4, 0): "9A",   # E minor
            (5, 0): "4A",   # F minor
            (6, 0): "11A",  # F# minor
            (7, 0): "6A",   # G minor
            (8, 0): "1A",   # Ab minor
            (9, 0): "8A",   # A minor
            (10, 0): "3A",  # Bb minor
            (11, 0): "10A", # B minor
        }
        
        return camelot_keys.get((key_num, mode), "")

    def _guess_genre_from_spotify_data(self, spotify_analysis: Dict[str, Any]) -> str:
        """
        Devine le genre basé sur les données Spotify (playlists, audio features).
        Plus intelligent que l'ancienne version.
        """
        playlist_analysis = spotify_analysis.get('playlist_analysis', {})
        spotify_track = spotify_analysis.get('spotify_track', {})
        
        # Compteur de genres potentiels
        genre_scores = {}
        
        # Analyser les catégories de playlists
        category_genre_hints = {
            'party_club': ['Electronic', 'House', 'EDM'],
            'latino': ['Latin', 'Reggaeton'],
            'reggaeton': ['Reggaeton'],
            'dancehall': ['Dancehall'],
            'hiphop_rnb': ['Hip-Hop', 'R&B'],
            'trap': ['Hip-Hop', 'Trap'],
            'lounge_cocktail': ['Jazz', 'Soul', 'Funk'],
            'mariage': ['Pop', 'Commercial'],
            'rock': ['Rock'],
            'funk': ['Funk', 'Disco'],
            'disco': ['Disco'],
            'afro': ['Afrobeat'],
            'house': ['House'],
            'techno': ['Techno'],
            'dnb': ['Drum & Bass']
        }
        
        # Parcourir toutes les playlists
        for playlist_data in playlist_analysis.values():
            category = playlist_data.get('category', '').lower()
            playlist_name = playlist_data.get('name', '').lower()
            
            # Score basé sur la catégorie
            for cat_key, genres in category_genre_hints.items():
                if cat_key in category:
                    for genre in genres:
                        genre_scores[genre] = genre_scores.get(genre, 0) + 2
            
            # Score basé sur le nom de la playlist
            genre_name_hints = {
                'reggaeton': 'Reggaeton',
                'latin': 'Latin',
                'salsa': 'Latin',
                'house': 'House',
                'techno': 'Techno',
                'hip hop': 'Hip-Hop',
                'rap': 'Hip-Hop',
                'r&b': 'R&B',
                'rock': 'Rock',
                'jazz': 'Jazz',
                'funk': 'Funk',
                'disco': 'Disco',
                'drum & bass': 'Drum & Bass',
                'dnb': 'Drum & Bass'
            }
            
            for hint, genre in genre_name_hints.items():
                if hint in playlist_name:
                    genre_scores[genre] = genre_scores.get(genre, 0) + 1
        
        # Utiliser les features audio pour affiner
        if spotify_track:
            tempo = spotify_track.get('tempo', 120)
            energy = spotify_track.get('energy', 0.5)
            danceability = spotify_track.get('danceability', 0.5)
            acousticness = spotify_track.get('acousticness', 0.5)
            speechiness = spotify_track.get('speechiness', 0.1)
            
            # Heuristiques basées sur les features
            if 118 <= tempo <= 132 and energy > 0.6:
                genre_scores['House'] = genre_scores.get('House', 0) + 1
            if 85 <= tempo <= 105 and danceability > 0.7:
                genre_scores['Reggaeton'] = genre_scores.get('Reggaeton', 0) + 1
            if 70 <= tempo <= 110 and speechiness > 0.3:
                genre_scores['Hip-Hop'] = genre_scores.get('Hip-Hop', 0) + 1
            if acousticness > 0.7:
                genre_scores['Jazz'] = genre_scores.get('Jazz', 0) + 1
            if 170 <= tempo <= 180:
                genre_scores['Drum & Bass'] = genre_scores.get('Drum & Bass', 0) + 1
        
        # Retourner le genre avec le score le plus élevé
        if genre_scores:
            return max(genre_scores.items(), key=lambda x: x[1])[0]
        
        # Vérifier aussi dans les styles détectés
        styles = spotify_analysis.get('styles', [])
        style_genre_map = {
            'Latino': 'Latin',
            'House': 'House',
            'Tech': 'Techno',
            'HipHop': 'Hip-Hop',
            'Disco': 'Disco',
            'Funky': 'Funk'
        }
        
        for style, genre in style_genre_map.items():
            if style in styles:
                return genre
        
        return ''  # Pas de genre détecté

    def _calculate_confidence_score(self, spotify_data: Dict, discogs_data: Dict, 
                                  gpt_data: Dict) -> float:
        """
        Calcule un score de confiance pour l'analyse (0.0 - 1.0).
        Utile pour identifier les analyses qui nécessitent une révision.
        """
        score = 0.0
        factors = 0
        
        # Spotify trouvé = bonne confiance
        if spotify_data:
            score += 0.4
            factors += 1
            
            # Bonus si popularité élevée (plus de données)
            popularity = spotify_data.get('popularity', 0)
            if popularity > 70:
                score += 0.1
        
        # Discogs trouvé
        if discogs_data and discogs_data.get('year'):
            score += 0.2
            factors += 1
        
        # GPT a analysé
        if gpt_data and gpt_data.get('genre'):
            score += 0.2
            factors += 1
        
        # Ajustement selon le nombre de sources
        if factors >= 3:
            score += 0.2  # Bonus si toutes les sources sont disponibles
        elif factors == 0:
            score = 0.1   # Score minimal en fallback
        
        return min(score, 1.0)

    def _evaluate_analysis_quality(self, analysis: Dict) -> bool:
        """
        Évalue si une analyse est de bonne qualité.
        Utilisé pour calculer le taux de réussite.
        """
        # Critères de qualité
        has_genre = bool(analysis.get('genre') and analysis['genre'] != 'Unknown')
        has_bpm = bool(analysis.get('bpm') and analysis['bpm'] != '0')
        has_contexts = len(analysis.get('comment_tags', [])) >= 2
        has_styles = len(analysis.get('grouping_tags', [])) >= 2
        confidence_ok = analysis.get('confidence_score', 0) >= 0.5
        
        # Au moins 4 critères sur 5 pour être considéré comme réussi
        criteria_met = sum([has_genre, has_bpm, has_contexts, has_styles, confidence_ok])
        
        return criteria_met >= 4

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation de l'orchestrateur."""
        success_rate = 0
        if self.stats['total_analyzed'] > 0:
            success_rate = (self.stats['successful_tags'] / self.stats['total_analyzed']) * 100
        
        # Statistiques de la base de corrections
        corrections_stats = self.corrections_db.get_statistics()
        
        return {
            'total_analyzed': self.stats['total_analyzed'],
            'successful_tags': self.stats['successful_tags'],
            'success_rate': f"{success_rate:.1f}%",
            'corrections_used': self.stats['corrections_used'],
            'api_usage': self.stats['api_hits'],
            'spotify_hit_rate': f"{(self.stats['api_hits']['spotify'] / max(self.stats['total_analyzed'], 1) * 100):.1f}%",
            'discogs_hit_rate': f"{(self.stats['api_hits']['discogs'] / max(self.stats['total_analyzed'], 1) * 100):.1f}%",
            'openai_hit_rate': f"{(self.stats['api_hits']['openai'] / max(self.stats['total_analyzed'], 1) * 100):.1f}%",
            'corrections_database': corrections_stats
        }

    def save_manual_correction(self, file_path: str, corrected_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde une correction manuelle après vérification par l'utilisateur.
        
        Args:
            file_path: Chemin du fichier audio
            corrected_data: Données corrigées par l'utilisateur
        
        Returns:
            bool: True si sauvegarde réussie
        """
        filename = os.path.basename(file_path)
        parsed = self._parse_filename(filename, {})
        
        # Préparer les données pour la sauvegarde
        correction_data = {
            'genre': corrected_data.get('genre'),
            'contexts': corrected_data.get('contexts', []),
            'moments': corrected_data.get('moments', []),
            'styles': corrected_data.get('styles', []),
            'bpm': corrected_data.get('bpm'),
            'key': corrected_data.get('key'),
            'energy': corrected_data.get('energy', 5),
            'year': corrected_data.get('year'),
            'album': corrected_data.get('album')
        }
        
        # Sauvegarder la correction
        self.corrections_db.save_correction(
            parsed['artist'],
            parsed['title'],
            correction_data
        )
        
        print(f"✅ Correction sauvegardée pour {parsed['artist']} - {parsed['title']}")
        print(f"📊 Total de corrections : {len(self.corrections_db.corrections)}")
        
        return True

    def get_correction_suggestions(self, genre: str, energy: int) -> List[Dict[str, Any]]:
        """
        Obtient des suggestions basées sur des morceaux similaires.
        
        Args:
            genre: Genre du morceau
            energy: Niveau d'énergie (0-10)
            
        Returns:
            Liste de suggestions de morceaux similaires
        """
        return self.corrections_db.get_similar_tracks(genre, energy)