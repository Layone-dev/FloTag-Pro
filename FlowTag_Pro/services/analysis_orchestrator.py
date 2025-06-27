"""
Orchestrateur principal pour l'analyse des tracks
Coordonne tous les services (Spotify, Discogs, Gemini/OpenAI)
Version mise à jour avec SpotifyAsyncService
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiofiles
from mutagen import File as MutagenFile

from .cache_manager import CacheManager
from .spotify_async import SpotifyAsyncService
from .gemini_service import GeminiDiscogsService
from .corrections_database import CorrectionsDatabase
from ..data.countries_db import detect_country


class AnalysisOrchestrator:
    """Orchestrateur principal coordonnant tous les services d'analyse"""
    
    def __init__(self):
        # Initialiser le cache manager
        self.cache_manager = CacheManager()
        
        # Initialiser les services
        self.spotify_service = SpotifyAsyncService(self.cache_manager)
        self.ai_service = GeminiDiscogsService(self.cache_manager)  # Utilise Gemini par défaut
        self.corrections_db = CorrectionsDatabase()
        
        # État des services
        self.services_status = self._check_services_status()
        
    def _check_services_status(self) -> Dict[str, bool]:
        """Vérifie l'état de tous les services"""
        status = {
            'spotify': self.spotify_service.sp is not None,
            'discogs': self.ai_service.discogs_client is not None,
            'gemini': self.ai_service.gemini_model is not None,
            'corrections': True,  # Toujours actif
            'cache': True  # Toujours actif
        }
        
        # Mode de fonctionnement
        if all(status.values()):
            print("✨ Mode COMPLET - Tous les services sont actifs")
        elif status['spotify'] and (status['gemini'] or status.get('openai', False)):
            print("🔧 Mode STANDARD - Spotify + IA actifs")
        elif status['spotify']:
            print("⚠️ Mode LIMITÉ - Seulement Spotify actif")
        else:
            print("❌ Mode DÉGRADÉ - Services limités")
            
        return status
        
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyse complète d'un fichier audio"""
        print("\n" + "=" * 60)
        print(f"🎵 Analyse de : {Path(file_path).name}")
        print("=" * 60)
        
        # Vérifier le cache complet d'abord
        cache_key = f"full_analysis_v5_{Path(file_path).stem}"
        cached_result = self.cache_manager.get_api_cache(cache_key, 'full_analysis')
        
        if cached_result:
            print("✅ Analyse complète trouvée dans le cache")
            return cached_result['response_data']
            
        # 1. Extraire les métadonnées du fichier
        track_info = await self._extract_file_metadata(file_path)
        
        # 2. Vérifier les corrections utilisateur
        corrections = self.corrections_db.get_corrections(
            track_info.get('artist', ''),
            track_info.get('title', '')
        )
        
        if corrections:
            print(f"✅ Corrections trouvées : {len(corrections)} entrées")
            track_info.update(corrections)
            
        # 3. Enrichissement Spotify
        spotify_data = await self._enrich_with_spotify(track_info)
        
        # 4. Enrichissement Discogs
        discogs_data = await self._enrich_with_discogs(track_info)
        
        # 5. Analyse IA pour le DJ
        ai_analysis = await self._analyze_with_ai(track_info, spotify_data, discogs_data)
        
        # 6. Générer l'analyse finale
        final_analysis = self._generate_final_analysis(
            track_info, spotify_data, discogs_data, ai_analysis
        )
        
        # 7. Formater les tags pour Serato
        final_analysis = self._format_tags_for_serato(final_analysis)
        
        # Afficher le résumé
        self._print_analysis_summary(final_analysis)
        
        # Sauvegarder dans le cache
        self.cache_manager.save_api_cache(cache_key, 'full_analysis', final_analysis)
        
        # Stats
        print(f"\n📊 Statistiques :")
        print(f"  - Taux de réussite : {self._calculate_success_rate(final_analysis):.1f}%")
        print(f"  - Corrections utilisées : {len(corrections) if corrections else 0}")
        
        return final_analysis
        
    async def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait les métadonnées d'un fichier audio"""
        try:
            audio_file = MutagenFile(file_path)
            
            if audio_file is None:
                # Fallback sur le nom du fichier
                filename = Path(file_path).stem
                parts = filename.split(' - ', 1)
                
                return {
                    'file_path': file_path,
                    'artist': parts[0] if len(parts) > 1 else 'Unknown',
                    'title': parts[1] if len(parts) > 1 else filename,
                    'album': '',
                    'year': '',
                    'genre': ''
                }
                
            # Extraire les tags standards
            tags = {
                'file_path': file_path,
                'artist': '',
                'title': '',
                'album': '',
                'year': '',
                'genre': '',
                'bpm': '',
                'key': ''
            }
            
            # Mapping des tags selon le format
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # MP3 ID3
                if 'TPE1' in audio_file.tags:
                    tags['artist'] = str(audio_file.tags['TPE1'])
                elif 'artist' in audio_file.tags:
                    tags['artist'] = str(audio_file.tags['artist'][0])
                    
                if 'TIT2' in audio_file.tags:
                    tags['title'] = str(audio_file.tags['TIT2'])
                elif 'title' in audio_file.tags:
                    tags['title'] = str(audio_file.tags['title'][0])
                    
                if 'TALB' in audio_file.tags:
                    tags['album'] = str(audio_file.tags['TALB'])
                elif 'album' in audio_file.tags:
                    tags['album'] = str(audio_file.tags['album'][0])
                    
                if 'TDRC' in audio_file.tags:
                    tags['year'] = str(audio_file.tags['TDRC'])
                elif 'date' in audio_file.tags:
                    tags['year'] = str(audio_file.tags['date'][0])
                    
                if 'TCON' in audio_file.tags:
                    tags['genre'] = str(audio_file.tags['TCON'])
                elif 'genre' in audio_file.tags:
                    tags['genre'] = str(audio_file.tags['genre'][0])
                    
                if 'TBPM' in audio_file.tags:
                    tags['bpm'] = str(audio_file.tags['TBPM'])
                    
                if 'TKEY' in audio_file.tags:
                    tags['key'] = str(audio_file.tags['TKEY'])
                    
            # Fallback sur le nom du fichier si pas de tags
            if not tags['artist'] or not tags['title']:
                filename = Path(file_path).stem
                parts = filename.split(' - ', 1)
                
                if len(parts) > 1:
                    tags['artist'] = parts[0].strip()
                    tags['title'] = parts[1].strip()
                else:
                    tags['title'] = filename
                    
            # Récupérer l'artwork
            tags['artwork_bytes'] = self._extract_artwork(audio_file)
            
            return tags
            
        except Exception as e:
            print(f"❌ Erreur extraction métadonnées : {e}")
            filename = Path(file_path).stem
            return {
                'file_path': file_path,
                'artist': 'Unknown',
                'title': filename,
                'error': str(e)
            }
            
    def _extract_artwork(self, audio_file) -> Optional[bytes]:
        """Extrait l'artwork d'un fichier audio"""
        try:
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # MP3
                if 'APIC:' in audio_file.tags:
                    return audio_file.tags['APIC:'].data
                # MP4/M4A
                elif 'covr' in audio_file.tags:
                    covers = audio_file.tags['covr']
                    if covers:
                        return bytes(covers[0])
            return None
        except Exception:
            return None
            
    async def _enrich_with_spotify(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les données avec Spotify"""
        if not self.services_status['spotify']:
            return {}
            
        print("\n🔎 Recherche Spotify...")
        
        # Rechercher le track
        spotify_track = await self.spotify_service.search_track(
            track_info.get('title', ''),
            track_info.get('artist', '')
        )
        
        if not spotify_track:
            print("  ❌ Non trouvé sur Spotify")
            return {}
            
        # Analyser les contextes via les playlists
        contexts_analysis = await self.spotify_service.analyze_track_contexts(
            spotify_track['id']
        )
        
        # Récupérer l'artwork si pas déjà présent
        if not track_info.get('artwork_bytes') and spotify_track.get('album_art'):
            artwork = await self.spotify_service.get_track_artwork(spotify_track['id'])
            if artwork:
                track_info['artwork_bytes'] = artwork
                
        return {
            'spotify_track': spotify_track,
            'contexts': contexts_analysis.get('contexts', []),
            'styles': contexts_analysis.get('styles', []),
            'playlist_count': contexts_analysis.get('playlist_count', 0),
            'confidence': contexts_analysis.get('confidence', 0)
        }
        
    async def _enrich_with_discogs(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les données avec Discogs"""
        if not self.services_status['discogs']:
            return {}
            
        print("\n💿 Recherche Discogs...")
        
        discogs_info = await self.ai_service.get_discogs_info(track_info)
        
        if discogs_info:
            print("  ✅ Infos Discogs récupérées")
        else:
            print("  ❌ Non trouvé sur Discogs")
            
        return discogs_info
        
    async def _analyze_with_ai(self, track_info: Dict[str, Any], 
                              spotify_data: Dict[str, Any],
                              discogs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse avec l'IA (Gemini ou OpenAI)"""
        if not self.services_status['gemini']:
            print("\n⚠️ IA non disponible, utilisation du mode fallback")
            return {}
            
        print("\n🤖 Analyse IA...")
        
        return await self.ai_service.analyze_track_dj(
            track_info, spotify_data, discogs_data
        )
        
    def _generate_final_analysis(self, track_info: Dict[str, Any],
                                spotify_data: Dict[str, Any],
                                discogs_data: Dict[str, Any],
                                ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère l'analyse finale en combinant toutes les sources"""
        
        # Base avec les infos du fichier
        final = track_info.copy()
        
        # Ajouter/mettre à jour avec Spotify
        if spotify_data.get('spotify_track'):
            spotify_track = spotify_data['spotify_track']
            final.update({
                'artist': spotify_track.get('artist') or final.get('artist', ''),
                'title': spotify_track.get('name') or final.get('title', ''),
                'album': spotify_track.get('album') or final.get('album', ''),
                'popularity': spotify_track.get('popularity', 0),
                'duration_ms': spotify_track.get('duration_ms', 0),
                'spotify_id': spotify_track.get('id'),
                'spotify_uri': spotify_track.get('uri'),
                'tempo': spotify_track.get('tempo'),
                'energy_raw': spotify_track.get('energy', 0),
                'danceability': spotify_track.get('danceability', 0),
                'valence': spotify_track.get('valence', 0)
            })
            
        # Ajouter les infos Discogs
        if discogs_data:
            final['year'] = discogs_data.get('year') or final.get('year', '')
            final['discogs_genre'] = discogs_data.get('genre', [])
            final['discogs_style'] = discogs_data.get('style', [])
            
        # Ajouter l'analyse IA
        if ai_analysis:
            final['genre'] = ai_analysis.get('genre') or final.get('genre', '')
            final['bpm'] = ai_analysis.get('bpm') or final.get('tempo')
            final['key'] = ai_analysis.get('key') or final.get('key', '')
            final['energy'] = ai_analysis.get('energy', 5)
            final['mood'] = ai_analysis.get('mood', '')
            final['dj_tips'] = ai_analysis.get('dj_tips', '')
            
        # Contextes et styles (combiner toutes les sources)
        all_contexts = []
        all_styles = []
        
        # Depuis Spotify
        all_contexts.extend(spotify_data.get('contexts', []))
        all_styles.extend(spotify_data.get('styles', []))
        
        # Depuis l'IA
        if ai_analysis.get('context_moment_pairs'):
            for pair in ai_analysis['context_moment_pairs']:
                if len(pair) >= 2:
                    all_contexts.append(pair[0].replace('#', ''))
                    
        all_styles.extend([s.replace('#', '') for s in ai_analysis.get('additional_styles', [])])
        
        # Dédupliquer et formater
        final['contexts'] = list(set(all_contexts))[:5]
        final['styles'] = list(set(all_styles))[:5]
        
        # Moments depuis l'IA
        final['moments'] = []
        if ai_analysis.get('context_moment_pairs'):
            moments_set = set()
            for pair in ai_analysis['context_moment_pairs']:
                if len(pair) >= 2:
                    moments_set.add(pair[1].replace('#', ''))
            final['moments'] = list(moments_set)
            
        # Détection du pays
        country_info = detect_country(final.get('artist', ''))
        final['country_code'] = country_info[0]
        final['country_name'] = country_info[1]
        
        # Tags pour commentaires et grouping
        final['comment_tags'] = []
        final['grouping_tags'] = []
        
        return final
        
    def _format_tags_for_serato(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les tags spécifiquement pour Serato DJ"""
        
        # Générer les tags de commentaires (contextes + moments)
        comment_tags = []
        
        # Format : #[Context] #[Moment]
        if analysis.get('context_moment_pairs'):
            # Utiliser les paires de l'IA si disponibles
            for pair in analysis['context_moment_pairs']:
                if len(pair) >= 2:
                    comment_tags.append(f"{pair[0]} {pair[1]}")
        else:
            # Sinon créer des combinaisons
            contexts = analysis.get('contexts', ['Bar', 'Club'])
            moments = analysis.get('moments', ['Warmup'])
            
            for context in contexts[:3]:  # Max 3 contextes
                for moment in moments[:2]:  # Max 2 moments par contexte
                    comment_tags.append(f"#[{context}] #[{moment}]")
                    
        analysis['comment_tags'] = comment_tags[:6]  # Max 6 combinaisons
        
        # Générer les tags de grouping (styles)
        grouping_tags = []
        
        for style in analysis.get('styles', ['Commercial'])[:4]:  # Max 4 styles
            grouping_tags.append(f"#{style}")
            
        # Ajouter des tags spéciaux si pertinent
        if analysis.get('energy', 0) >= 8:
            grouping_tags.append('#Banger')
        if analysis.get('popularity', 0) >= 70:
            grouping_tags.append('#Popular')
        if int(analysis.get('year', 0)) < 2010:
            grouping_tags.append('#Classics')
            
        analysis['grouping_tags'] = list(set(grouping_tags))[:5]  # Max 5 tags
        
        # Formatter le label (pays + sample info)
        country_flag = {
            'US': '🇺🇸', 'GB': '🇬🇧', 'FR': '🇫🇷', 'ES': '🇪🇸',
            'DE': '🇩🇪', 'IT': '🇮🇹', 'PR': '🇵🇷', 'MX': '🇲🇽',
            'CO': '🇨🇴', 'AR': '🇦🇷', 'BR': '🇧🇷', 'CA': '🇨🇦'
        }.get(analysis.get('country_code', ''), '🌍')
        
        label_parts = [f"{country_flag} {analysis.get('country_name', 'International')}"]
        
        if analysis.get('sample_info'):
            label_parts.append(f"Sample: {analysis['sample_info']}")
            
        analysis['label'] = ' | '.join(label_parts)
        
        # Générer les strings finaux pour les tags
        analysis['comment'] = ' '.join(analysis['comment_tags'])
        analysis['grouping'] = ' '.join(analysis['grouping_tags'])
        
        return analysis
        
    def _print_analysis_summary(self, analysis: Dict[str, Any]):
        """Affiche un résumé de l'analyse"""
        print(f"\n🔍 Résultat de l'analyse :")
        print(f"  🎤 Artiste: {analysis.get('artist', 'Unknown')}")
        print(f"  🎵 Titre: {analysis.get('title', 'Unknown')}")
        print(f"  🎸 Genre: {analysis.get('genre', 'Unknown')}")
        
        # Infos techniques
        tempo = analysis.get('bpm') or analysis.get('tempo')
        if tempo:
            print(f"  🎹 BPM: {tempo:.0f} | Key: {analysis.get('key', 'Unknown')} | Energy: {analysis.get('energy', 5)}/10")
        
        # Contextes et styles
        if analysis.get('contexts'):
            print(f"  📍 Contextes: {analysis['contexts']}")
        if analysis.get('moments'):
            print(f"  ⏰ Moments: {analysis['moments']}")
        if analysis.get('styles'):
            print(f"  🎨 Styles: {analysis['styles']}")
            
        # Tags finaux
        print(f"\n🏷️ Tags finaux :")
        print(f"  📝 Comment: {analysis.get('comment', '')}")
        print(f"  🎯 Grouping: {analysis.get('grouping', '')}")
        print(f"  🌍 Label: {analysis.get('label', '')}")
        
    def _calculate_success_rate(self, analysis: Dict[str, Any]) -> float:
        """Calcule le taux de réussite de l'analyse"""
        fields = ['artist', 'title', 'genre', 'contexts', 'styles', 'energy']
        filled = sum(1 for field in fields if analysis.get(field))
        return (filled / len(fields)) * 100
        
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation"""
        stats = {
            'services_status': self.services_status,
            'cache_size': self.cache_manager.get_cache_size(),
            'corrections_count': len(self.corrections_db.corrections)
        }
        
        # Ajouter les stats de l'IA si disponible
        if hasattr(self.ai_service, 'get_usage_stats'):
            stats['ai_usage'] = self.ai_service.get_usage_stats()
            
        return stats