"""
Service OpenAI + Discogs pour FlowTag Pro
Prompt optimisé pour DJ événementiel
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from discogs_client import Client
from .cache_manager import CacheManager
from ..data.countries_db import detect_country
from ..data.genres_db import get_genre_contexts, FLOWTAG_AUTO_RULES


class OpenAIDiscogsService:
    """Service combiné OpenAI + Discogs pour analyse intelligente DJ"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.openai_client = None
        self.discogs_client = None
        self.setup_clients()
        
    def setup_clients(self):
        """Configuration des clients API"""
        # OpenAI - Configuration simplifiée pour Python 3.13
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                # Éviter le bug avec Python 3.13
                os.environ['HTTPX_DISABLE_PROXY'] = 'true'
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    http_client=None  # Forcer à ne pas utiliser de proxy
                )
                print("✅ Client OpenAI configuré")
            except Exception as e:
                print(f"⚠️ Erreur OpenAI: {e}")
                # Fallback : utiliser l'API key directement
                self.openai_client = None
                self.openai_api_key = openai_api_key
        else:
            self.openai_client = None
            self.openai_api_key = None
            
        # Discogs
        discogs_token = os.getenv('DISCOGS_TOKEN')
        if discogs_token:
            try:
                self.discogs_client = Client('FlowTagPro/1.0', user_token=discogs_token)
            except Exception as e:
                print(f"⚠️ Erreur Discogs: {e}")
                self.discogs_client = None
                
    async def analyze_track_dj(self, track_info: Dict[str, Any], spotify_analysis: Dict[str, Any], discogs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse DJ événementiel complète avec prompt optimisé et règles métier."""
        cache_key = f"openai_dj_analysis_v2_{track_info.get('title', '')}_{track_info.get('artist', '')}"
        cached_analysis = self.cache_manager.get_api_cache(cache_key, 'openai_dj_analysis')
        
        if cached_analysis:
            return cached_analysis['response_data']
            
        # Analyser avec OpenAI
        openai_analysis = {}
        if self.openai_client or hasattr(self, 'openai_api_key'):
            openai_analysis = await self._call_openai_api(track_info, spotify_analysis, discogs_data)
        
        # Sauvegarder l'analyse dans le cache
        self.cache_manager.save_api_cache(cache_key, 'openai_dj_analysis', openai_analysis)
        
        return openai_analysis
        
    async def _call_openai_api(self, track_info: Dict[str, Any], spotify_analysis: Dict[str, Any], discogs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le prompt et appelle l'API OpenAI."""
        try:
            # Enrichir le contexte
            genre = track_info.get('genre', '')
            subgenre = discogs_data.get('style', [''])[0] if discogs_data.get('style') else ''
            suggested_contexts = get_genre_contexts(genre, subgenre)
            country_info = detect_country(track_info.get('artist'))
            
            # Prompt optimisé pour DJ événementiel
            prompt = f"""
            Analyse pour DJ événementiel de la piste : '{track_info.get('artist', '')} - {track_info.get('title', '')}'.
            
            Artiste probablement de : {country_info[1]} ({country_info[0]})
            Genre Principal : {genre}
            Sous-Genre (Discogs) : {subgenre}
            Contextes Spotify détectés : {', '.join(spotify_analysis.get('contexts', []))}
            Contextes suggérés par genre : {', '.join(suggested_contexts)}
            
            Tu es un expert DJ événementiel. Ta mission est de déterminer où et quand jouer ce morceau.
            IMPORTANT : Le BPM est géré par Serato. Ne retourne PAS de valeur pour le champ 'bpm'.
            
            TACHES (Retourne UNIQUEMENT un JSON valide):
            1. bpm: null
            2. key: Tonalité au format Camelot (ex: 11B, 6A).
            3. energy: Note d'énergie sur 10 (1=très calme, 10=très intense).
            4. context_moment_pairs: Liste de paires [contexte, moment]. Sois créatif et pertinent.
               Exemple: [["#Bar", "#Warmup"], ["#Mariage", "#Peaktime"], ["#Club", "#Closing"]]
            5. additional_styles: Styles/caractéristiques additionnels. Choisis parmi : ["#Banger", "#Bootleg", "#Classics", "#Funky", "#Ladies", "#Mashup"].
            6. mood: Ambiance générale en 1 à 3 mots-clés.
            7. year_of_release: Année de sortie (nombre entier).
            8. sample_info: Si un sample est clairement identifié, retourne "Artiste - Titre". Sinon, retourne null.
            9. dj_tips: Un conseil de mix ou de placement pour un DJ.
            
            SYNTHÈSE : Combine les informations de Spotify, du genre, et du pays pour une analyse complète.
            Réponds UNIQUEMENT en JSON valide.
            """
            
            if not self.openai_client and not hasattr(self, 'openai_api_key'):
                print("⚠️ OpenAI non configuré")
                return {}

            try:
                # Essayer d'abord avec le client s'il existe
                if self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Tu es un expert DJ événementiel spécialisé dans l'analyse musicale pour Serato. Réponds UNIQUEMENT en JSON valide."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=800
                    )
                    analysis_text = response.choices[0].message.content
                else:
                    # Sinon utiliser directement avec l'API key
                    import openai
                    openai.api_key = self.openai_api_key
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "Tu es un expert DJ événementiel spécialisé dans l'analyse musicale pour Serato. Réponds UNIQUEMENT en JSON valide."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=800
                    )
                    analysis_text = response['choices'][0]['message']['content']
            
                # Parser la réponse JSON
                try:
                    if analysis_text:
                        analysis_json = json.loads(analysis_text)
                        return analysis_json
                    else:
                        print("⚠️ Réponse vide d'OpenAI")
                        return {}
                except json.JSONDecodeError:
                    print(f"⚠️ JSON mal formé, parsing manuel")
                    return self.parse_text_analysis_dj(analysis_text or "", spotify_analysis)
                    
            except Exception as e:
                print(f"❌ Erreur appel OpenAI : {e}")
                return self.parse_text_analysis_dj("", spotify_analysis)
                
        except Exception as e:
            print(f"❌ Erreur OpenAI générale : {e}")
            return self.parse_text_analysis_dj("", spotify_analysis)

    def parse_text_analysis_dj(self, analysis_text: str, spotify_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse l'analyse textuelle DJ si JSON échoue"""
        # Fallback intelligent basé sur l'analyse Spotify
        contexts = spotify_analysis.get('contexts', [])
        styles = spotify_analysis.get('styles', [])
        
        # Générer les paires contexte-moment
        context_moment_pairs = []
        moment_rules = {
            'Bar': ['Warmup', 'Closing'],
            'Club': ['Peaktime'],
            'Restaurant': ['Warmup'],
            'Mariage': ['Warmup', 'Peaktime', 'Closing'],
            'CorporateEvent': ['Warmup', 'Closing'],
            'Cocktail': ['Warmup', 'Closing'],
            'CocktailChic': ['Warmup'],
            'Festival': ['Peaktime'],
            'PoolParty': ['Peaktime'],
            'Anniversaire': ['Warmup', 'Peaktime', 'Closing']
        }
        
        for context in contexts:
            if context in moment_rules:
                for moment in moment_rules[context]:
                    context_moment_pairs.append([f"#{context}", f"#{moment}"])
                    
        # Styles supplémentaires
        additional_styles = []
        if 'Banger' in styles:
            additional_styles.append('#Banger')
        if 'Classics' in styles:
            additional_styles.append('#Classics')
        if 'Funky' in styles:
            additional_styles.append('#Funky')
        if 'Ladies' in styles:
            additional_styles.append('#Ladies')
            
        return {
            'bpm': None,
            'key': None,
            'energy': 7 if 'Club' in contexts else 5,
            'context_moment_pairs': context_moment_pairs,
            'additional_styles': additional_styles,
            'mood': 'festif' if 'Club' in contexts else 'ambiance',
            'year_of_release': None,
            'sample_info': None,
            'dj_tips': f"Adapté pour {', '.join(contexts)} - {', '.join(styles)}"
        }
        
    async def get_discogs_info(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """Récupération des informations Discogs"""
        if not self.discogs_client:
            print("⚠️ Client Discogs non configuré")
            return {}
            
        try:
            title = track_info.get('title', '')
            artist = track_info.get('artist', '')
            
            if not title or not artist:
                return {}
                
            # Recherche dans Discogs
            search_query = f"{artist} {title}"
            results = self.discogs_client.search(search_query, type='release')
            
            if results:
                release = results[0]
                return {
                    'release_id': release.id,
                    'title': release.title,
                    'artist': release.artists[0].name if release.artists else '',
                    'year': release.year,
                    'genre': release.genres,
                    'style': release.styles,
                    'cover_image': release.images[0]['uri'] if release.images else None
                }
        except Exception as e:
            print(f"Erreur Discogs : {e}")
            return {}
            
        return {}
        
    def learn_from_cache(self, track_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apprend des analyses précédentes stockées dans le cache pour améliorer
        la cohérence et la pertinence des nouvelles analyses.
        """
        # Fonctionnalité simplifiée pour le moment
        return {}
        
    def analyze_tag_patterns(self, similar_tracks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns de tags dans une liste de morceaux similaires"""
        context_counts = {}
        moment_counts = {}
        style_counts = {}
        
        for track in similar_tracks:
            # Paires contexte-moment
            for context, moment in track.get('context_moment_pairs', []):
                context_counts[context] = context_counts.get(context, 0) + 1
                moment_counts[moment] = moment_counts.get(moment, 0) + 1
                
            # Styles additionnels
            for style in track.get('additional_styles', []):
                style_counts[style] = style_counts.get(style, 0) + 1
                
        return {
            'common_contexts': sorted(context_counts, key=lambda k: context_counts[k], reverse=True),
            'common_moments': sorted(moment_counts, key=lambda k: moment_counts[k], reverse=True),
            'common_styles': sorted(style_counts, key=lambda k: style_counts[k], reverse=True),
        }