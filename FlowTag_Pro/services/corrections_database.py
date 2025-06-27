"""
Système de base de données locale pour FlowTag Pro
Permet de sauvegarder les corrections et d'apprendre des erreurs
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class CorrectionsDatabase:
    """
    Base de données locale pour stocker les corrections manuelles
    et améliorer la précision du système.
    """
    
    def __init__(self, db_path: str = "flowtag_corrections.json"):
        self.db_path = db_path
        self.corrections = self._load_database()
        self.genre_aliases = self._load_genre_aliases()
        self.artist_database = self._load_artist_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Charge la base de données des corrections."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_database(self):
        """Sauvegarde la base de données."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.corrections, f, indent=2, ensure_ascii=False)
    
    def _load_genre_aliases(self) -> Dict[str, str]:
        """Charge les alias de genres pour normalisation."""
        return {
            # Reggaeton variations
            'regueton': 'Reggaeton',
            'reggeaton': 'Reggaeton',
            'reggaetón': 'Reggaeton',
            'dembow': 'Reggaeton',
            
            # Latin variations
            'latino': 'Latin',
            'latina': 'Latin',
            'tropical': 'Latin',
            
            # Electronic variations
            'edm': 'Electronic',
            'electro': 'Electronic',
            'electronica': 'Electronic',
            'dance': 'Electronic',
            
            # House variations
            'deep house': 'House',
            'tech house': 'House',
            'progressive house': 'House',
            'funky house': 'House',
            'tribal house': 'House',
            
            # Hip-Hop variations
            'hip hop': 'Hip-Hop',
            'hiphop': 'Hip-Hop',
            'rap': 'Hip-Hop',
            'trap': 'Hip-Hop',
            'drill': 'Hip-Hop',
            
            # R&B variations
            'r&b': 'R&B',
            'rnb': 'R&B',
            'rhythm and blues': 'R&B',
            'soul': 'R&B',
            'neo soul': 'R&B',
            
            # DnB variations
            'drum and bass': 'Drum & Bass',
            'drum & bass': 'Drum & Bass',
            'dnb': 'Drum & Bass',
            'd&b': 'Drum & Bass',
            'jungle': 'Drum & Bass'
        }
    
    def _load_artist_database(self) -> Dict[str, Dict[str, Any]]:
        """Base de données des artistes connus avec leur genre principal."""
        return {
            # Reggaeton
            'don omar': {'genre': 'Reggaeton', 'country': 'PR 🇵🇷'},
            'daddy yankee': {'genre': 'Reggaeton', 'country': 'PR 🇵🇷'},
            'bad bunny': {'genre': 'Reggaeton', 'country': 'PR 🇵🇷'},
            'j balvin': {'genre': 'Reggaeton', 'country': 'CO 🇨🇴'},
            'maluma': {'genre': 'Reggaeton', 'country': 'CO 🇨🇴'},
            'ozuna': {'genre': 'Reggaeton', 'country': 'PR 🇵🇷'},
            'anuel aa': {'genre': 'Reggaeton', 'country': 'PR 🇵🇷'},
            
            # Electronic/House
            'david guetta': {'genre': 'House', 'country': 'FR 🇫🇷'},
            'calvin harris': {'genre': 'House', 'country': 'GB 🇬🇧'},
            'martin garrix': {'genre': 'House', 'country': 'NL 🇳🇱'},
            'swedish house mafia': {'genre': 'House', 'country': 'SE 🇸🇪'},
            'deadmau5': {'genre': 'House', 'country': 'CA 🇨🇦'},
            'carl cox': {'genre': 'Techno', 'country': 'GB 🇬🇧'},
            
            # Hip-Hop
            'drake': {'genre': 'Hip-Hop', 'country': 'CA 🇨🇦'},
            'kendrick lamar': {'genre': 'Hip-Hop', 'country': 'US 🇺🇸'},
            'j. cole': {'genre': 'Hip-Hop', 'country': 'US 🇺🇸'},
            'travis scott': {'genre': 'Hip-Hop', 'country': 'US 🇺🇸'},
            'migos': {'genre': 'Hip-Hop', 'country': 'US 🇺🇸'},
            
            # Pop
            'taylor swift': {'genre': 'Pop', 'country': 'US 🇺🇸'},
            'ed sheeran': {'genre': 'Pop', 'country': 'GB 🇬🇧'},
            'bruno mars': {'genre': 'Pop', 'country': 'US 🇺🇸'},
            'the weeknd': {'genre': 'Pop', 'country': 'CA 🇨🇦'},
            'dua lipa': {'genre': 'Pop', 'country': 'GB 🇬🇧'},
            
            # Latin
            'shakira': {'genre': 'Latin', 'country': 'CO 🇨🇴'},
            'marc anthony': {'genre': 'Latin', 'country': 'US 🇺🇸'},
            'enrique iglesias': {'genre': 'Latin', 'country': 'ES 🇪🇸'},
            'luis fonsi': {'genre': 'Latin', 'country': 'PR 🇵🇷'},
            
            # Afrobeat
            'burna boy': {'genre': 'Afrobeat', 'country': 'NG 🇳🇬'},
            'wizkid': {'genre': 'Afrobeat', 'country': 'NG 🇳🇬'},
            'davido': {'genre': 'Afrobeat', 'country': 'NG 🇳🇬'},
            
            # French
            'stromae': {'genre': 'Pop', 'country': 'BE 🇧🇪'},
            'maitre gims': {'genre': 'Hip-Hop', 'country': 'FR 🇫🇷'},
            'aya nakamura': {'genre': 'Pop', 'country': 'FR 🇫🇷'}
        }
    
    def get_correction(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Récupère une correction sauvegardée si elle existe."""
        key = self._make_key(artist, title)
        return self.corrections.get(key)
    
    def save_correction(self, artist: str, title: str, correction_data: Dict[str, Any]):
        """
        Sauvegarde une correction manuelle.
        
        Args:
            artist: Nom de l'artiste
            title: Titre du morceau
            correction_data: Données corrigées (genre, contexts, moments, styles, etc.)
        """
        key = self._make_key(artist, title)
        
        self.corrections[key] = {
            'artist': artist,
            'title': title,
            'genre': correction_data.get('genre'),
            'contexts': correction_data.get('contexts', []),
            'moments': correction_data.get('moments', []),
            'styles': correction_data.get('styles', []),
            'bpm': correction_data.get('bpm'),
            'key': correction_data.get('key'),
            'energy': correction_data.get('energy'),
            'verified': True,
            'last_updated': datetime.now().isoformat(),
            'correction_count': self.corrections.get(key, {}).get('correction_count', 0) + 1
        }
        
        self._save_database()
        print(f"✅ Correction sauvegardée pour {artist} - {title}")
    
    def _make_key(self, artist: str, title: str) -> str:
        """Crée une clé unique pour la base de données."""
        # Normaliser pour éviter les doublons
        artist_clean = artist.lower().strip()
        title_clean = title.lower().strip()
        # Enlever les caractères spéciaux communs
        for char in ['(', ')', '[', ']', '-', '_', '.', ',']:
            artist_clean = artist_clean.replace(char, ' ')
            title_clean = title_clean.replace(char, ' ')
        # Enlever les espaces multiples
        artist_clean = ' '.join(artist_clean.split())
        title_clean = ' '.join(title_clean.split())
        
        return f"{artist_clean}::{title_clean}"
    
    def normalize_genre(self, genre: str) -> str:
        """Normalise un genre en utilisant les alias."""
        genre_lower = genre.lower().strip()
        return self.genre_aliases.get(genre_lower, genre)
    
    def get_artist_info(self, artist: str) -> Optional[Dict[str, Any]]:
        """Récupère les infos d'un artiste depuis la base de données."""
        artist_lower = artist.lower().strip()
        return self.artist_database.get(artist_lower)
    
    def add_artist(self, artist: str, genre: str, country: str):
        """Ajoute un artiste à la base de données."""
        artist_lower = artist.lower().strip()
        self.artist_database[artist_lower] = {
            'genre': self.normalize_genre(genre),
            'country': country
        }
    
    def get_similar_tracks(self, genre: str, energy: int) -> List[Dict[str, Any]]:
        """
        Trouve des morceaux similaires dans les corrections.
        Utile pour suggérer des tags.
        """
        similar = []
        genre_normalized = self.normalize_genre(genre)
        
        for key, track_data in self.corrections.items():
            track_genre = self.normalize_genre(track_data.get('genre', ''))
            track_energy = track_data.get('energy', 5)
            
            # Critères de similarité
            if (track_genre == genre_normalized and 
                abs(track_energy - energy) <= 2 and
                track_data.get('verified')):
                
                similar.append({
                    'artist': track_data['artist'],
                    'title': track_data['title'],
                    'contexts': track_data.get('contexts', []),
                    'moments': track_data.get('moments', []),
                    'styles': track_data.get('styles', [])
                })
        
        return similar[:5]  # Retourner max 5 suggestions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base de données."""
        total_corrections = len(self.corrections)
        genres = {}
        verified_count = 0
        
        for track_data in self.corrections.values():
            # Compter les genres
            genre = track_data.get('genre', 'Unknown')
            genres[genre] = genres.get(genre, 0) + 1
            
            # Compter les vérifiés
            if track_data.get('verified'):
                verified_count += 1
        
        return {
            'total_corrections': total_corrections,
            'verified_tracks': verified_count,
            'genres_distribution': genres,
            'artists_in_db': len(self.artist_database),
            'most_corrected_genre': max(genres.items(), key=lambda x: x[1])[0] if genres else None
        }


class SmartFallback:
    """
    Système de fallback intelligent utilisant la base de corrections
    et des heuristiques avancées.
    """
    
    def __init__(self, corrections_db: CorrectionsDatabase):
        self.corrections_db = corrections_db
        self.remix_patterns = [
            'remix', 'edit', 'bootleg', 'rework', 'vip',
            'extended', 'radio edit', 'club mix', 'dub mix',
            'instrumental', 'acapella', 'mashup'
        ]
    
    def analyze_with_corrections(self, artist: str, title: str, 
                                existing_metadata: Dict) -> Optional[Dict[str, Any]]:
        """
        Analyse en utilisant d'abord la base de corrections.
        """
        # 1. Vérifier si on a une correction exacte
        correction = self.corrections_db.get_correction(artist, title)
        if correction and correction.get('verified'):
            print(f"✅ Trouvé dans la base de corrections!")
            return {
                'source': 'corrections_db',
                'confidence': 1.0,
                'data': correction
            }
        
        # 2. Vérifier si on connaît l'artiste
        artist_info = self.corrections_db.get_artist_info(artist)
        if artist_info:
            print(f"✅ Artiste connu : {artist} ({artist_info['genre']})")
            
            # Chercher des morceaux similaires
            similar_tracks = self.corrections_db.get_similar_tracks(
                artist_info['genre'], 
                existing_metadata.get('energy', 7)
            )
            
            if similar_tracks:
                # Moyenner les tags des morceaux similaires
                all_contexts = []
                all_moments = []
                all_styles = []
                
                for track in similar_tracks:
                    all_contexts.extend(track['contexts'])
                    all_moments.extend(track['moments'])
                    all_styles.extend(track['styles'])
                
                # Prendre les plus fréquents
                from collections import Counter
                context_counts = Counter(all_contexts)
                moment_counts = Counter(all_moments)
                style_counts = Counter(all_styles)
                
                return {
                    'source': 'artist_similarity',
                    'confidence': 0.7,
                    'data': {
                        'genre': artist_info['genre'],
                        'contexts': [c for c, _ in context_counts.most_common(3)],
                        'moments': [m for m, _ in moment_counts.most_common(2)],
                        'styles': [s for s, _ in style_counts.most_common(3)],
                        'country': artist_info.get('country', '')
                    }
                }
        
        # 3. Analyse du titre pour détecter les remixes
        title_lower = title.lower()
        for pattern in self.remix_patterns:
            if pattern in title_lower:
                print(f"🎛️ Remix/Edit détecté : {pattern}")
                # Extraire le titre original si possible
                original_title = title_lower.split(pattern)[0].strip()
                
                # Essayer de trouver l'original
                potential_original = self.corrections_db.get_correction(artist, original_title)
                if potential_original:
                    # Adapter les tags pour un remix
                    return {
                        'source': 'remix_detection',
                        'confidence': 0.6,
                        'data': {
                            'genre': potential_original.get('genre'),
                            'contexts': potential_original.get('contexts', []) + ['Club'],
                            'moments': ['Peaktime'],  # Les remixes sont souvent peaktime
                            'styles': potential_original.get('styles', []) + ['Remix'],
                            'is_remix': True
                        }
                    }
        
        return None


def integrate_corrections_system(orchestrator):
    """
    Intègre le système de corrections dans l'orchestrateur existant.
    À ajouter dans analysis_orchestrator.py
    """
    # Initialiser la base de corrections
    corrections_db = CorrectionsDatabase()
    smart_fallback = SmartFallback(corrections_db)
    
    # Ajouter à l'orchestrateur
    orchestrator.corrections_db = corrections_db
    orchestrator.smart_fallback = smart_fallback
    
    # Modifier la méthode analyze_file pour utiliser les corrections
    original_analyze = orchestrator.analyze_file
    
    async def enhanced_analyze_file(file_path: str) -> Dict[str, Any]:
        # Parser le fichier
        filename = os.path.basename(file_path)
        parsed = orchestrator._parse_filename(filename, {})
        
        # Vérifier d'abord la base de corrections
        correction_result = smart_fallback.analyze_with_corrections(
            parsed['artist'], 
            parsed['title'],
            orchestrator._extract_existing_metadata(file_path)
        )
        
        if correction_result and correction_result['confidence'] >= 0.7:
            print(f"🎯 Utilisation des données de correction (confiance: {correction_result['confidence']})")
            # Construire le résultat final avec les données de correction
            return orchestrator._build_result_from_correction(
                file_path, 
                parsed,
                correction_result['data']
            )
        
        # Sinon, analyse normale
        result = await original_analyze(file_path)
        
        # Proposer de sauvegarder si confiance faible
        if result.get('confidence_score', 0) < 0.7:
            print(f"\n⚠️ Confiance faible ({result.get('confidence_score', 0):.2f})")
            print("💡 Vérifiez les tags et sauvegardez la correction si nécessaire")
        
        return result
    
    orchestrator.analyze_file = enhanced_analyze_file
    
    return orchestrator


# Exemple d'utilisation
if __name__ == "__main__":
    # Test du système de corrections
    db = CorrectionsDatabase()
    
    # Ajouter une correction
    db.save_correction(
        "Don Omar & Lucenzo",
        "Danza Kuduro",
        {
            'genre': 'Reggaeton',
            'contexts': ['Club', 'Mariage', 'Generaliste', 'PoolParty'],
            'moments': ['Warmup', 'Peaktime'],
            'styles': ['Latino', 'Banger', 'Commercial', 'Classics'],
            'bpm': '130',
            'key': '11A',
            'energy': 9
        }
    )
    
    # Tester la récupération
    correction = db.get_correction("Don Omar & Lucenzo", "Danza Kuduro")
    if correction:
        print(f"Correction trouvée : {correction}")
    
    # Afficher les stats
    stats = db.get_statistics()
    print(f"\nStatistiques : {stats}")