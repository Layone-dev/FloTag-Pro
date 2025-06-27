#!/usr/bin/env python3
"""
Dialog de configuration des APIs pour FloTag Pro
Version avec support Gemini AI (gratuit)
"""

import customtkinter
import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
from typing import Dict, Optional
import platform


class SettingsDialog(customtkinter.CTkToplevel):
    """Fenêtre de dialogue pour configurer les APIs."""
    
    def __init__(self, parent, current_config: Optional[Dict] = None):
        super().__init__(parent)
        
        self.parent = parent
        self.result = None
        self.current_config = current_config or {}
        
        # Configuration de la fenêtre
        self.title("⚙️ Configuration des APIs - FloTag Pro")
        self.geometry("650x600")
        self.resizable(False, False)
        
        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()
        
        # Style sombre
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        
        self._create_widgets()
        self._load_current_values()
        
        # Focus sur la fenêtre
        self.focus()
        
    def _create_widgets(self):
        """Crée les widgets de l'interface."""
        
        # Frame principal avec scrolling
        main_frame = customtkinter.CTkScrollableFrame(
            self, 
            label_text="🔑 Configuration des clés API"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Activer le défilement avec trackpad
        self._bind_mousewheel(main_frame)
        
        # Instructions
        instructions = customtkinter.CTkLabel(
            main_frame,
            text="📋 Configurez vos clés API pour activer toutes les fonctionnalités :",
            font=("Arial", 14),
            text_color="#CCCCCC"
        )
        instructions.pack(pady=(0, 20))
        
        # === SPOTIFY API ===
        spotify_frame = self._create_api_section(
            main_frame, 
            "🎵 Spotify Web API",
            "Pour l'enrichissement des métadonnées musicales"
        )
        
        self.spotify_client_id_entry = self._create_api_field(
            spotify_frame,
            "Client ID :",
            "Votre Spotify Client ID"
        )
        
        self.spotify_client_secret_entry = self._create_api_field(
            spotify_frame,
            "Client Secret :",
            "Votre Spotify Client Secret",
            show_chars=False
        )
        
        spotify_help = customtkinter.CTkLabel(
            spotify_frame,
            text="💡 Obtenez vos clés sur : https://developer.spotify.com/dashboard",
            font=("Arial", 11),
            text_color="#4ECDC4"
        )
        spotify_help.pack(pady=(5, 0))
        
        # === DISCOGS API ===
        discogs_frame = self._create_api_section(
            main_frame,
            "💿 Discogs API", 
            "Pour les informations détaillées sur les releases"
        )
        
        self.discogs_token_entry = self._create_api_field(
            discogs_frame,
            "Consumer Token :",
            "Votre Discogs Consumer Token",
            show_chars=False
        )
        
        discogs_help = customtkinter.CTkLabel(
            discogs_frame,
            text="💡 Obtenez votre token sur : https://www.discogs.com/settings/developers",
            font=("Arial", 11),
            text_color="#4ECDC4"
        )
        discogs_help.pack(pady=(5, 0))
        
        # === GEMINI API (NOUVEAU) ===
        gemini_frame = self._create_api_section(
            main_frame,
            "✨ Gemini AI (Google) - GRATUIT",
            "Pour l'analyse intelligente et le tagging automatique (1,500 req/jour)"
        )
        
        self.gemini_key_entry = self._create_api_field(
            gemini_frame,
            "API Key :",
            "AIzaSyA6DMicshRobtHKGQ272m9CSVXgNlZSgCY",
            show_chars=False
        )
        
        gemini_help = customtkinter.CTkLabel(
            gemini_frame,
            text="💡 Obtenez votre clé GRATUITE sur : https://makersuite.google.com/app/apikey",
            font=("Arial", 11),
            text_color="#00FF00"  # Vert pour indiquer que c'est gratuit
        )
        gemini_help.pack(pady=(5, 0))
        
        gemini_info = customtkinter.CTkLabel(
            gemini_frame,
            text="✅ 100% Gratuit - 1,500 analyses/jour - Qualité professionnelle",
            font=("Arial", 11, "bold"),
            text_color="#00FF00"
        )
        gemini_info.pack(pady=(5, 0))
        
        # === OPENAI API (OPTIONNEL) ===
        openai_frame = self._create_api_section(
            main_frame,
            "🤖 OpenAI API (Optionnel)",
            "Alternative payante à Gemini - Gardez vide si vous utilisez Gemini"
        )
        
        self.openai_key_entry = self._create_api_field(
            openai_frame,
            "API Key :",
            "Votre clé API OpenAI (sk-...)",
            show_chars=False
        )
        
        openai_help = customtkinter.CTkLabel(
            openai_frame,
            text="💡 Payant - Obtenez votre clé sur : https://platform.openai.com/account/api-keys",
            font=("Arial", 11),
            text_color="#FF9999"  # Rouge clair pour indiquer que c'est payant
        )
        openai_help.pack(pady=(5, 0))
        
        # === RECOMMANDATION ===
        recommendation_frame = customtkinter.CTkFrame(main_frame, fg_color="#1a1a1a")
        recommendation_frame.pack(fill="x", pady=15, padx=10)
        
        recommendation_label = customtkinter.CTkLabel(
            recommendation_frame,
            text="💡 Recommandation : Utilisez Gemini AI (gratuit) pour commencer !",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        recommendation_label.pack(pady=10)
        
        # === BOUTONS ===
        buttons_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        # Bouton Annuler
        cancel_btn = customtkinter.CTkButton(
            buttons_frame,
            text="❌ Annuler",
            command=self._cancel,
            fg_color="gray",
            width=120
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Bouton Test
        test_btn = customtkinter.CTkButton(
            buttons_frame,
            text="🔍 Tester les APIs",
            command=self._test_apis,
            fg_color="orange",
            width=140
        )
        test_btn.pack(side="left", padx=5)
        
        # Bouton Sauvegarder
        save_btn = customtkinter.CTkButton(
            buttons_frame,
            text="💾 Sauvegarder",
            command=self._save,
            fg_color="green",
            width=120
        )
        save_btn.pack(side="right", padx=5)
        
    def _create_api_section(self, parent, title: str, description: str):
        """Crée une section pour une API."""
        section_frame = customtkinter.CTkFrame(parent)
        section_frame.pack(fill="x", pady=10)
        
        # Titre de la section
        title_label = customtkinter.CTkLabel(
            section_frame,
            text=title,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Description
        desc_label = customtkinter.CTkLabel(
            section_frame,
            text=description,
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        desc_label.pack(pady=(0, 10))
        
        return section_frame
        
    def _create_api_field(self, parent, label: str, placeholder: str, show_chars: bool = True):
        """Crée un champ de saisie pour une clé API."""
        field_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=15, pady=5)
        
        # Label
        label_widget = customtkinter.CTkLabel(
            field_frame,
            text=label,
            width=120
        )
        label_widget.pack(side="left", padx=(0, 10))
        
        # Entry
        entry = customtkinter.CTkEntry(
            field_frame,
            placeholder_text=placeholder,
            width=350,
            show="*" if not show_chars else None
        )
        entry.pack(side="left", fill="x", expand=True)
        
        return entry
        
    def _load_current_values(self):
        """Charge les valeurs actuelles dans les champs."""
        # Charger depuis le fichier .env s'il existe
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                if key == 'SPOTIFY_CLIENT_ID':
                                    self.spotify_client_id_entry.insert(0, value)
                                elif key == 'SPOTIFY_CLIENT_SECRET':
                                    self.spotify_client_secret_entry.insert(0, value)
                                elif key == 'DISCOGS_TOKEN':
                                    self.discogs_token_entry.insert(0, value)
                                elif key == 'GEMINI_API_KEY':
                                    self.gemini_key_entry.insert(0, value)
                                elif key == 'OPENAI_API_KEY':
                                    self.openai_key_entry.insert(0, value)
            except Exception as e:
                print(f"Erreur lors du chargement du .env : {e}")
        
        # Charger aussi depuis current_config si fourni
        if self.current_config:
            if 'spotify_client_id' in self.current_config and not self.spotify_client_id_entry.get():
                self.spotify_client_id_entry.insert(0, self.current_config['spotify_client_id'])
            if 'spotify_client_secret' in self.current_config and not self.spotify_client_secret_entry.get():
                self.spotify_client_secret_entry.insert(0, self.current_config['spotify_client_secret'])
            if 'discogs_token' in self.current_config and not self.discogs_token_entry.get():
                self.discogs_token_entry.insert(0, self.current_config['discogs_token'])
            if 'gemini_api_key' in self.current_config and not self.gemini_key_entry.get():
                self.gemini_key_entry.insert(0, self.current_config['gemini_api_key'])
            if 'openai_api_key' in self.current_config and not self.openai_key_entry.get():
                self.openai_key_entry.insert(0, self.current_config['openai_api_key'])
    
    def _test_apis(self):
        """Teste les APIs avec les clés saisies."""
        config = self._get_form_values()
        
        # Test simple - vérification du format des clés
        tests_results = []
        
        # Test Spotify
        if config['spotify_client_id'] and config['spotify_client_secret']:
            if len(config['spotify_client_id']) >= 20 and len(config['spotify_client_secret']) >= 20:
                tests_results.append("✅ Spotify : Format des clés OK")
            else:
                tests_results.append("❌ Spotify : Format des clés incorrect")
        else:
            tests_results.append("⚠️ Spotify : Clés non renseignées")
            
        # Test Discogs
        if config['discogs_token']:
            if len(config['discogs_token']) >= 20:
                tests_results.append("✅ Discogs : Format du token OK")
            else:
                tests_results.append("❌ Discogs : Format du token incorrect")
        else:
            tests_results.append("⚠️ Discogs : Token non renseigné")
            
        # Test Gemini (NOUVEAU)
        if config['gemini_api_key']:
            if config['gemini_api_key'].startswith('AIza') and len(config['gemini_api_key']) >= 30:
                tests_results.append("✅ Gemini AI : Format de la clé OK (GRATUIT)")
            else:
                tests_results.append("❌ Gemini AI : Format de la clé incorrect (doit commencer par 'AIza')")
        else:
            tests_results.append("⚠️ Gemini AI : Clé non renseignée")
            
        # Test OpenAI
        if config['openai_api_key']:
            if config['openai_api_key'].startswith('sk-') and len(config['openai_api_key']) >= 40:
                tests_results.append("✅ OpenAI : Format de la clé OK (Payant)")
            else:
                tests_results.append("❌ OpenAI : Format de la clé incorrect (doit commencer par 'sk-')")
        else:
            tests_results.append("⚠️ OpenAI : Clé non renseignée (OK si vous utilisez Gemini)")
        
        # Vérifier qu'au moins une IA est configurée
        if not config['gemini_api_key'] and not config['openai_api_key']:
            tests_results.append("\n⚠️ ATTENTION : Aucune IA configurée !")
            tests_results.append("   Configurez Gemini (gratuit) ou OpenAI pour l'analyse intelligente")
        elif config['gemini_api_key'] and config['openai_api_key']:
            tests_results.append("\n💡 Info : Les deux IA sont configurées.")
            tests_results.append("   Gemini sera utilisé en priorité (gratuit)")
        
        # Afficher les résultats
        result_text = "🔍 Résultats des tests :\n\n" + "\n".join(tests_results)
        result_text += "\n\n💡 Note : Ces tests vérifient uniquement le format des clés."
        result_text += "\nPour tester la connectivité réelle, sauvegardez puis relancez l'application."
        
        messagebox.showinfo("Test des APIs", result_text)
    
    def _get_form_values(self) -> Dict:
        """Récupère les valeurs du formulaire."""
        return {
            'spotify_client_id': self.spotify_client_id_entry.get().strip(),
            'spotify_client_secret': self.spotify_client_secret_entry.get().strip(),
            'discogs_token': self.discogs_token_entry.get().strip(),
            'gemini_api_key': self.gemini_key_entry.get().strip(),
            'openai_api_key': self.openai_key_entry.get().strip()
        }
    
    def _save(self):
        """Sauvegarde la configuration."""
        config = self._get_form_values()
        
        # Vérifier qu'au moins une API est configurée
        if not any([config['spotify_client_id'], config['discogs_token'], 
                   config['gemini_api_key'], config['openai_api_key']]):
            messagebox.showwarning(
                "Configuration vide", 
                "Veuillez configurer au moins une API avant de sauvegarder.\n\n"
                "💡 Recommandé : Utilisez Gemini AI (gratuit) pour commencer !"
            )
            return
        
        # Créer le fichier .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        
        try:
            # Lire les lignes existantes pour préserver les commentaires et l'ordre
            existing_lines = []
            existing_keys = set()
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()
                    for line in existing_lines:
                        if '=' in line and not line.strip().startswith('#'):
                            key = line.split('=')[0].strip()
                            existing_keys.add(key)
            
            # Écrire le nouveau fichier
            with open(env_path, 'w', encoding='utf-8') as f:
                # En-tête
                if not existing_lines:
                    f.write("# Configuration des APIs pour FloTag Pro\n")
                    f.write("# Généré automatiquement - Ne pas partager ce fichier\n\n")
                
                # Fonction pour écrire ou mettre à jour une clé
                def write_or_update_key(key_name, value):
                    if value:
                        f.write(f"{key_name}={value}\n")
                
                # Si on a des lignes existantes, les parcourir et mettre à jour
                if existing_lines:
                    for line in existing_lines:
                        line_stripped = line.strip()
                        if not line_stripped or line_stripped.startswith('#'):
                            f.write(line)
                        elif '=' in line:
                            key = line.split('=')[0].strip()
                            if key == 'SPOTIFY_CLIENT_ID' and config['spotify_client_id']:
                                f.write(f"SPOTIFY_CLIENT_ID={config['spotify_client_id']}\n")
                            elif key == 'SPOTIFY_CLIENT_SECRET' and config['spotify_client_secret']:
                                f.write(f"SPOTIFY_CLIENT_SECRET={config['spotify_client_secret']}\n")
                            elif key == 'DISCOGS_TOKEN' and config['discogs_token']:
                                f.write(f"DISCOGS_TOKEN={config['discogs_token']}\n")
                            elif key == 'GEMINI_API_KEY' and config['gemini_api_key']:
                                f.write(f"GEMINI_API_KEY={config['gemini_api_key']}\n")
                            elif key == 'OPENAI_API_KEY' and config['openai_api_key']:
                                f.write(f"OPENAI_API_KEY={config['openai_api_key']}\n")
                            else:
                                f.write(line)
                        else:
                            f.write(line)
                
                # Ajouter les nouvelles clés qui n'existaient pas
                if 'SPOTIFY_CLIENT_ID' not in existing_keys and config['spotify_client_id']:
                    f.write(f"SPOTIFY_CLIENT_ID={config['spotify_client_id']}\n")
                if 'SPOTIFY_CLIENT_SECRET' not in existing_keys and config['spotify_client_secret']:
                    f.write(f"SPOTIFY_CLIENT_SECRET={config['spotify_client_secret']}\n")
                if 'DISCOGS_TOKEN' not in existing_keys and config['discogs_token']:
                    f.write(f"DISCOGS_TOKEN={config['discogs_token']}\n")
                if 'GEMINI_API_KEY' not in existing_keys and config['gemini_api_key']:
                    f.write(f"GEMINI_API_KEY={config['gemini_api_key']}\n")
                if 'OPENAI_API_KEY' not in existing_keys and config['openai_api_key']:
                    f.write(f"OPENAI_API_KEY={config['openai_api_key']}\n")
            
            self.result = config
            
            # Message de succès personnalisé
            success_msg = f"✅ Configuration sauvegardée dans {env_path}\n\n"
            
            if config['gemini_api_key']:
                success_msg += "🎉 Gemini AI configuré ! Vous avez 1,500 analyses gratuites par jour.\n\n"
            elif config['openai_api_key']:
                success_msg += "🤖 OpenAI configuré (payant à l'usage).\n\n"
            
            success_msg += "🔄 Relancez l'application pour appliquer les changements."
            
            messagebox.showinfo("Configuration sauvegardée", success_msg)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Erreur de sauvegarde", 
                f"Impossible de sauvegarder la configuration :\n{str(e)}"
            )
    
    def _cancel(self):
        """Annule et ferme la fenêtre."""
        self.result = None
        self.destroy()
        
    def get_result(self):
        """Retourne le résultat après fermeture de la fenêtre."""
        return self.result
    
    def _bind_mousewheel(self, widget):
        """Lie le défilement de la molette/trackpad à un widget (méthode finale)."""
        
        def on_scroll(event):
            # Sur macOS, le delta du trackpad peut être petit, on ajuste la vitesse.
            multiplier = 3 if abs(event.delta) <= 5 else 1
            scroll_amount = -event.delta * multiplier

            try:
                if hasattr(widget, '_parent_canvas'):
                    widget._parent_canvas.yview_scroll(int(scroll_amount), "units")
            except tk.TclError:
                # Ignore les erreurs si le widget est détruit pendant le défilement
                pass

        def on_enter(event):
            # Lier le défilement uniquement quand la souris est sur le widget
            widget.bind('<MouseWheel>', on_scroll)

        def on_leave(event):
            # Délier pour éviter les conflits avec d'autres widgets
            widget.unbind('<MouseWheel>')

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)