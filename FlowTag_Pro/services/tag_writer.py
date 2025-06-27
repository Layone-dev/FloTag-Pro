"""
Service d'écriture des tags ID3 dans les fichiers audio
Utilise mutagen pour écrire les métadonnées
"""

import os
from typing import Dict, Optional, Any, Union
from mutagen import File
from mutagen.id3 import (
    ID3, TIT2, TPE1, TALB, TDRC, TCON, TKEY, 
    COMM, GRP1, TPUB, APIC, ID3NoHeaderError
)
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


class TagWriter:
    """
    Écrit les tags ID3 dans les fichiers audio.
    Supporte MP3, FLAC, etc.
    """
    
    def __init__(self):
        """Initialise le writer."""
        self.supported_formats = ['.mp3', '.flac', '.aiff', '.wav']
    
    def write_tags(
        self, 
        file_path: str, 
        tags: Dict[str, str], 
        artwork_bytes: Optional[bytes] = None
    ) -> bool:
        """
        Écrit les tags dans un fichier audio.
        
        Args:
            file_path: Chemin vers le fichier
            tags: Dictionnaire des tags à écrire (format ID3)
            artwork_bytes: Données de l'image de pochette (optionnel)
            
        Returns:
            True si succès, False sinon
        """
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
        
        # Vérifier le format
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Format non supporté: {ext}")
        
        try:
            # Charger le fichier avec mutagen
            audio = File(file_path)
            
            if audio is None:
                # Si mutagen ne peut pas charger, essayer de créer les tags
                if ext == '.mp3':
                    audio = MP3(file_path)
                    audio.tags = ID3()
                else:
                    raise Exception("Impossible de charger le fichier audio")
            
            # S'assurer que les tags ID3 existent
            if not hasattr(audio, 'tags') or audio.tags is None:
                audio.add_tags()
            
            # Écrire les tags textuels
            if tags.get('TIT2'):  # Titre
                audio.tags['TIT2'] = TIT2(encoding=3, text=tags['TIT2'])
            
            if tags.get('TPE1'):  # Artiste
                audio.tags['TPE1'] = TPE1(encoding=3, text=tags['TPE1'])
            
            if tags.get('TALB'):  # Album
                audio.tags['TALB'] = TALB(encoding=3, text=tags['TALB'])
            
            if tags.get('TDRC'):  # Année
                audio.tags['TDRC'] = TDRC(encoding=3, text=str(tags['TDRC']))
            
            if tags.get('TCON'):  # Genre
                audio.tags['TCON'] = TCON(encoding=3, text=tags['TCON'])
            
            if tags.get('TKEY'):  # Clé
                audio.tags['TKEY'] = TKEY(encoding=3, text=tags['TKEY'])
            
            if tags.get('COMM'):  # Commentaire
                # COMM a une structure spéciale
                audio.tags['COMM'] = COMM(
                    encoding=3, 
                    lang='fra', 
                    desc='', 
                    text=tags['COMM']
                )
            
            if tags.get('GRP1'):  # Grouping
                audio.tags['GRP1'] = GRP1(encoding=3, text=tags['GRP1'])
            
            if tags.get('TPUB'):  # Label/Publisher
                audio.tags['TPUB'] = TPUB(encoding=3, text=tags['TPUB'])
            
            # Écrire la pochette si fournie
            if artwork_bytes:
                # Supprimer les anciennes pochettes
                audio.tags.delall('APIC')
                
                # Ajouter la nouvelle
                audio.tags['APIC'] = APIC(
                    encoding=3,
                    mime='image/jpeg',  # Supposer JPEG, ajuster si nécessaire
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=artwork_bytes
                )
            
            # Sauvegarder les modifications
            audio.save()
            
            print(f"✅ Tags écrits avec succès dans {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture des tags: {e}")
            raise
    
    def read_tags(self, file_path: str) -> Dict[str, Any]:
        """
        Lit les tags d'un fichier audio.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            Dictionnaire des tags lus
        """
        tags = {}
        
        try:
            audio = File(file_path)
            
            if audio is not None and audio.tags is not None:
                # Lire les tags textuels
                for tag_id, tag_name in [
                    ('TIT2', 'title'),
                    ('TPE1', 'artist'),
                    ('TALB', 'album'),
                    ('TDRC', 'year'),
                    ('TCON', 'genre'),
                    ('TKEY', 'key'),
                    ('GRP1', 'grouping'),
                    ('TPUB', 'label')
                ]:
                    if tag_id in audio.tags:
                        tags[tag_name] = str(audio.tags[tag_id])
                
                # Lire le commentaire
                if 'COMM' in audio.tags:
                    tags['comment'] = str(audio.tags['COMM'])
                
                # Vérifier la présence d'une pochette
                if 'APIC:' in audio.tags:
                    tags['has_artwork'] = True
                    
        except Exception as e:
            print(f"Erreur lors de la lecture des tags: {e}")
            
        return tags
    
    def remove_all_tags(self, file_path: str) -> bool:
        """
        Supprime tous les tags d'un fichier audio.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            True si succès, False sinon
        """
        try:
            audio = File(file_path)
            if audio is not None:
                audio.delete()
                audio.save()
                print(f"✅ Tous les tags supprimés de {os.path.basename(file_path)}")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression des tags: {e}")
            return False