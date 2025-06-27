"""
Service Gemini (Google AI) + Discogs pour FlowTag Pro
Version gratuite avec 1,500 requêtes/jour
Remplace complètement OpenAI
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from discogs_client import Client
import google.generativeai as genai
from .cache_manager import CacheManager
from ..data.countries_db import detect_country
from ..data.genres_db import get_genre_contexts, FLOWTAG_AUTO_RULES


class GeminiDiscogsService:
    """Service combiné Gemini + Discogs pour analyse intelligente DJ"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.gemini_model = None
        self.discogs_client = None
        self.setup_clients()
        
        # Statistiques d'utilisation
        self.daily_requests = 0
        self.daily_limit = 1500  # Limite gratuite Gemini
        
    def setup_clients(self):
        """Configuration des clients API"""
        # Gemini (Google AI) - GRATUIT
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI configuré avec succès (1,500 req/jour gratuits)")
            except Exception as e:
                print(f"⚠️ Erreur Gemini: {e}")
                self.gemini_model = None
        else:
            print("⚠️ GEMINI_API_KEY non configurée")
            print("💡 Obtenez une clé gratuite sur: https://makersuite.google.com/app/apikey")
            self.gemini_model = None
            
        # Discogs
        discogs_token = os.getenv('DISCOGS_TOKEN')
        if discogs_token:
            try:
                self.discogs_client = Client('FlowTagPro/1.0', user_token=discogs_token)
                print("✅ Client Discogs configuré")
            except Exception as e:
                print(f"⚠️ Erreur Discogs: {e}")
                self.discogs_client = None
                
    async def analyze_track_dj(self, track_info: Dict[str, Any], 
                             spotify_analysis: Dict[str, Any], 
                             discogs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse DJ événementiel complète avec Gemini AI."""
        # Vérifier le cache d'abord
        cache_key = f"gemini_dj_analysis_v1_{track_info.get('title', '')}_{track_info.get('artist', '')}"
        cached_analysis = self.cache_manager.get_api_cache(cache_key, 'gemini_dj_analysis')
        
        if cached_analysis:
            print("  ✅ Analyse trouvée dans le cache")
            return cached_analysis['response_data']
            
        # Vérifier la limite quotidienne
        if self.daily_requests >= self.daily_limit:
            print(f"⚠️ Limite Gemini atteinte ({self.daily_limit}/jour)")
            return self._fallback_analysis(track_info, spotify_analysis)
            
        # Analyser avec Gemini
        gemini_analysis = {}
        if self.gemini_model:
            gemini_analysis = await self._call_gemini_api(track_info, spotify_analysis, discogs_data)
            self.daily_requests += 1
            print(f"  📊 Requêtes Gemini aujourd'hui: {self.daily_requests}/{self.daily_limit}")
        else:
            print("  ⚠️ Gemini non disponible, utilisation du fallback")
            gemini_analysis = self._fallback_analysis(track_info, spotify_analysis)
        
        # Sauvegarder l'analyse dans le cache
        if gemini_analysis:
            self.cache_manager.save_api_cache(cache_key, 'gemini_dj_analysis', gemini_analysis)
        
        return gemini_analysis
        
    async def _call_gemini_api(self, track_info: Dict[str, Any], 
                               spotify_analysis: Dict[str, Any], 
                               discogs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le prompt et appelle l'API Gemini."""
        try:
            # Enrichir le contexte
            genre = track_info.get('genre', '')
            subgenre = discogs_data.get('style', [''])[0] if discogs_data.get('style') else ''
            suggested_contexts = get_genre_contexts(genre, subgenre)
            country_info = detect_country(track_info.get('artist'))
            
            # Récupérer les infos Spotify
            spotify_track = spotify_analysis.get('spotify_track', {})
            tempo = spotify_track.get('tempo', 'Inconnu')
            energy = spotify_track.get('energy', 0)
            danceability = spotify_track.get('danceability', 0)
            valence = spotify_track.get('valence', 0)
            
            # Prompt optimisé pour Gemini
            prompt = f"""Tu es un expert DJ événementiel. Analyse ce morceau pour Serato DJ:

**Morceau**: {track_info.get('artist', '')} - {track_info.get('title', '')}
**Pays artiste**: {country_info[1]} ({country_info[0]})
**Genre principal**: {genre or 'Non défini'}
**Sous-genre Discogs**: {subgenre or 'Non défini'}

**Données Spotify**:
- Tempo: {tempo} BPM
- Énergie: {energy:.2f}/1
- Dansabilité: {danceability:.2f}/1
- Positivité: {valence:.2f}/1

**Contextes détectés**: {', '.join(spotify_analysis.get('contexts', ['Non défini']))}
**Contextes suggérés**: {', '.join(suggested_contexts)}

**IMPORTANT**: Retourne UNIQUEMENT un JSON valide avec cette structure EXACTE:
{{
    "genre": "Genre musical précis (Reggaeton, House, Pop, etc)",
    "bpm": null,
    "key": "Tonalité Camelot (ex: 11B, 6A) ou null",
    "energy": 7,
    "context_moment_pairs": [
        ["Bar", "Warmup"],
        ["Club", "Peaktime"],
        ["Mariage", "Closing"]
    ],
    "additional_styles": ["Banger", "Commercial", "Latino"],
    "mood": "festif énergique",
    "year_of_release": 2010,
    "sample_info": null,
    "dj_tips": "Parfait pour faire monter l'énergie en club"
}}

**Règles**:
- Le genre doit être précis (pas "Latin" mais "Reggaeton", "Salsa", etc)
- context_moment_pairs: minimum 2, maximum 6 paires
- Contextes possibles: Bar, Club, Mariage, CorporateEvent, Restaurant, Generaliste, CocktailChic, PoolParty
- Moments possibles: Warmup, Peaktime, Closing
- Styles possibles: Banger, Bootleg, Classics, Funky, Ladies, Mashup, Commercial, Latino, HipHop, House, Deep, Tech, Vocal, Disco, Progressive
- energy: nombre entier de 1 à 10
- Ne PAS mettre de hashtags # dans le JSON

Retourne UNIQUEMENT le JSON, rien d'autre."""

            # Appel à Gemini
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                # Parser la réponse
                return self._parse_gemini_response(response.text, spotify_analysis)
            else:
                print("⚠️ Réponse Gemini vide")
                return self._fallback_analysis(track_info, spotify_analysis)
                
        except Exception as e:
            print(f"❌ Erreur Gemini API : {e}")
            return self._fallback_analysis(track_info, spotify_analysis)

    def _parse_gemini_response(self, response_text: str, spotify_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse la réponse de Gemini et assure la validité du JSON."""
        try:
            # Nettoyer la réponse
            cleaned = response_text.strip()
            
            # Extraire le JSON s'il est entouré de texte
            if '{' in cleaned and '}' in cleaned:
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                json_str = cleaned[start:end]
            else:
                json_str = cleaned
            
            # Parser le JSON
            result = json.loads(json_str)
            
            # Valider et nettoyer le résultat
            cleaned_result = {
                'genre': result.get('genre', ''),
                'bpm': None,  # Toujours null comme demandé
                'key': result.get('key'),
                'energy': int(result.get('energy', 5)),
                'context_moment_pairs': [],
                'additional_styles': [],
                'mood': result.get('mood', ''),
                'year_of_release': result.get('year_of_release'),
                'sample_info': result.get('sample_info'),
                'dj_tips': result.get('dj_tips', '')
            }
            
            # Nettoyer les paires contexte-moment
            for pair in result.get('context_moment_pairs', []):
                if isinstance(pair, list) and len(pair) == 2:
                    context = pair[0].replace('#', '').replace('[', '').replace(']', '')
                    moment = pair[1].replace('#', '').replace('[', '').replace(']', '')
                    cleaned_result['context_moment_pairs'].append([f"#{context}", f"#{moment}"])
            
            # Nettoyer les styles additionnels
            for style in result.get('additional_styles', []):
                clean_style = style.replace('#', '').strip()
                if clean_style:
                    cleaned_result['additional_styles'].append(f"#{clean_style}")
            
            return cleaned_result
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️ Erreur parsing JSON Gemini: {e}")
            print(f"Réponse reçue: {response_text[:200]}...")
            return self._fallback_analysis({}, spotify_analysis)

    def _fallback_analysis(self, track_info: Dict[str, Any], spotify_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse de secours basée sur les données Spotify et les règles métier."""
        contexts = spotify_analysis.get('contexts', ['Bar', 'Club'])
        styles = spotify_analysis.get('styles', ['Commercial'])
        
        # Règles intelligentes pour les paires contexte-moment
        context_moment_rules = {
            'Bar': ['Warmup', 'Closing'],
            'Club': ['Warmup', 'Peaktime'],
            'Restaurant': ['Warmup'],
            'Mariage': ['Warmup', 'Peaktime', 'Closing'],
            'CorporateEvent': ['Warmup', 'Closing'],
            'CocktailChic': ['Warmup'],
            'Generaliste': ['Warmup', 'Peaktime'],
            'PoolParty': ['Peaktime'],
        }
        
        # Générer les paires
        context_moment_pairs = []
        for context in contexts[:3]:  # Limiter à 3 contextes
            if context in context_moment_rules:
                for moment in context_moment_rules[context][:2]:  # Max 2 moments par contexte
                    context_moment_pairs.append([f"#{context}", f"#{moment}"])
        
        # Si pas assez de paires, ajouter des défauts
        if len(context_moment_pairs) < 2:
            context_moment_pairs = [
                ["#Bar", "#Warmup"],
                ["#Club", "#Peaktime"]
            ]
        
        # Styles additionnels basés sur l'analyse
        additional_styles = []
        for style in styles:
            if style in ['Banger', 'Classics', 'Funky', 'Ladies', 'Commercial', 'Latino']:
                additional_styles.append(f"#{style}")
        
        # Estimation de l'énergie basée sur les contextes
        energy = 7  # Défaut
        if 'Club' in contexts or 'Festival' in contexts:
            energy = 8
        elif 'Restaurant' in contexts or 'CocktailChic' in contexts:
            energy = 4
        elif 'Mariage' in contexts:
            energy = 6
        
        return {
            'genre': track_info.get('genre', ''),
            'bpm': None,
            'key': None,
            'energy': energy,
            'context_moment_pairs': context_moment_pairs,
            'additional_styles': additional_styles[:3],  # Max 3 styles
            'mood': 'festif' if energy > 6 else 'ambiance',
            'year_of_release': None,
            'sample_info': None,
            'dj_tips': f"Adapté pour {', '.join(contexts[:2])}"
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
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation Gemini."""
        return {
            'service': 'Gemini (Google AI)',
            'daily_requests': self.daily_requests,
            'daily_limit': self.daily_limit,
            'requests_remaining': self.daily_limit - self.daily_requests,
            'cost': 'GRATUIT',
            'reset_time': 'Minuit PST'
        }
    
    def reset_daily_counter(self):
        """Réinitialise le compteur quotidien (à appeler à minuit)."""
        self.daily_requests = 0
        print("✅ Compteur Gemini réinitialisé : 1,500 requêtes disponibles")


# Alias pour la compatibilité (remplace OpenAIDiscogsService)
OpenAIDiscogsService = GeminiDiscogsService