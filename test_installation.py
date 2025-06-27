#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation de FloTag Pro
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Teste que tous les modules peuvent être importés"""
    print("🧪 Test des imports...")
    
    modules = [
        ("customtkinter", "Interface graphique"),
        ("mutagen", "Lecture/écriture tags audio"),
        ("spotipy", "API Spotify"),
        ("openai", "API OpenAI"),
        ("aiohttp", "Requêtes asynchrones"),
        ("PIL", "Traitement d'images")
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} ({description})")
        except ImportError as e:
            print(f"  ❌ {module_name} ({description}): {e}")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Vérifie que la structure du projet est correcte"""
    print("\n📁 Test de la structure...")
    
    # Adapter selon ta structure
    base_dir = "FlowTag_Pro"
    
    required_files = [
        "main.py",
        "requirements.txt",
        f"{base_dir}/README.md",
        f"{base_dir}/ui/__init__.py",
        f"{base_dir}/ui/flotag_pro_app.py",
        f"{base_dir}/services/__init__.py",
        f"{base_dir}/services/tag_writer.py",
        f"{base_dir}/services/cache_manager.py",
        f"{base_dir}/services/analysis_orchestrator.py",
        f"{base_dir}/data/__init__.py",
        f"{base_dir}/data/countries_db.py",
        f"{base_dir}/data/genres_db.py"
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} manquant")
            all_ok = False
    
    return all_ok

def test_env_variables():
    """Vérifie les variables d'environnement"""
    print("\n🔑 Test des variables d'environnement...")
    
    # Charger le .env si disponible
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("  ⚠️  python-dotenv non installé")
    
    env_vars = {
        "SPOTIFY_CLIENT_ID": "API Spotify",
        "SPOTIFY_CLIENT_SECRET": "API Spotify",
        "DISCOGS_TOKEN": "API Discogs",
        "OPENAI_API_KEY": "API OpenAI"
    }
    
    configured = []
    not_configured = []
    
    for var, api in env_vars.items():
        if os.getenv(var):
            configured.append(api)
        else:
            not_configured.append(api)
    
    # Afficher le résultat
    unique_configured = list(set(configured))
    unique_not_configured = list(set(not_configured))
    
    for api in unique_configured:
        if api not in unique_not_configured:
            print(f"  ✅ {api}")
    
    for api in unique_not_configured:
        print(f"  ⚠️  {api} non configuré")
    
    return True

def test_tag_writer():
    """Test basique du TagWriter"""
    print("\n🏷️  Test du TagWriter...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FlowTag_Pro'))
        from services.tag_writer import TagWriter
        writer = TagWriter()
        print("  ✅ TagWriter initialisé")
        return True
    except Exception as e:
        print(f"  ❌ Erreur TagWriter: {e}")
        return False

def test_cache_manager():
    """Test basique du CacheManager"""
    print("\n💾 Test du CacheManager...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FlowTag_Pro'))
        from services.cache_manager import CacheManager
        cache = CacheManager()
        
        # Test écriture/lecture
        test_data = {"test": "data"}
        cache.save_api_cache("test_key", "full_analysis", test_data)
        retrieved = cache.get_api_cache("test_key", "full_analysis")
        
        if retrieved and retrieved.get('response_data') == test_data:
            print("  ✅ Cache fonctionnel")
            
            # Afficher les stats
            stats = cache.get_cache_stats()
            print(f"  📊 Fichiers en cache: {stats['total_files']}")
            print(f"  📊 Taille totale: {stats['total_size_mb']} MB")
            return True
        else:
            print("  ❌ Erreur cache")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur CacheManager: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=== Test d'installation FloTag Pro ===\n")
    
    # Exécuter tous les tests
    tests = [
        test_imports(),
        test_project_structure(),
        test_env_variables(),
        test_tag_writer(),
        test_cache_manager()
    ]
    
    # Résumé
    print("\n=== Résumé ===")
    if all(tests):
        print("✅ Tous les tests sont passés !")
        print("🎵 FloTag Pro est prêt à être utilisé.")
        print("\nPour lancer l'application: python main.py")
    else:
        print("❌ Certains tests ont échoué.")
        print("Vérifiez les erreurs ci-dessus et relancez l'installation.")
    
    return 0 if all(tests) else 1

if __name__ == "__main__":
    sys.exit(main()) 