import asyncio
import io
import os
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

import customtkinter
from PIL import Image, ImageTk
import platform

# Imports relatifs corrigés
from ..services.analysis_orchestrator import AnalysisOrchestrator
from ..services.tag_writer import TagWriter


class FloTagProApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration de la fenêtre ---
        self.title("FloTag Pro 🎵")
        self.geometry("1100x750")
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")

        # --- Initialisation des services ---
        self.orchestrator = AnalysisOrchestrator()
        self.tag_writer = TagWriter()

        # --- État de l'application (la mémoire de l'app) ---
        self.all_track_data: Dict[str, Dict[str, Any]] = {}
        self.file_paths: List[str] = []
        self.current_track_file_path: Optional[str] = None
        self.artwork_image = None  # Pour garder une référence à l'image

        # --- Construction de l'UI ---
        self._create_main_view()
        self._create_detail_view()

        # Afficher la vue principale au démarrage
        self._switch_to_main_view()

    # ===================================================================
    # 1. CRÉATION DE L'INTERFACE GRAPHIQUE
    # ===================================================================

    def _create_main_view(self):
        """Crée les widgets de la vue principale (liste de fichiers, boutons...)."""
        self.main_container = customtkinter.CTkFrame(self)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Barre du haut avec les boutons
        top_frame = customtkinter.CTkFrame(self.main_container)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_files_button = customtkinter.CTkButton(
            top_frame, 
            text="📁 Ajouter Fichiers", 
            command=self.add_files
        )
        self.add_files_button.pack(side="left", padx=5)

        self.analyze_all_button = customtkinter.CTkButton(
            top_frame, 
            text="🔍 Analyser TOUT", 
            command=self.analyze_all_tracks
        )
        self.analyze_all_button.pack(side="left", padx=5)
        
        # Bouton de test pour vérifier la navigation
        self.test_detail_button = customtkinter.CTkButton(
            top_frame, 
            text="🔧 Test Vue Détaillée", 
            command=self._test_detail_view,
            fg_color="orange"
        )
        self.test_detail_button.pack(side="left", padx=5)

        # Bouton de configuration des APIs
        self.settings_button = customtkinter.CTkButton(
            top_frame, 
            text="⚙️ Configurer APIs", 
            command=self._open_settings,
            fg_color="purple"
        )
        self.settings_button.pack(side="right", padx=5)

        # Liste des morceaux (utilisation de ttk.Treeview standard)
        list_frame = customtkinter.CTkFrame(self.main_container)
        list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Créer le Treeview avec un style sombre
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background="#2b2b2b", 
                       foreground="white", 
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", 
                       background="#1f1f1f", 
                       foreground="white")

        columns = ("STATUS", "FICHIER", "ARTISTE", "TITRE")
        self.track_list = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.track_list.heading("STATUS", text="Statut")
        self.track_list.heading("FICHIER", text="Fichier")
        self.track_list.heading("ARTISTE", text="Artiste")
        self.track_list.heading("TITRE", text="Titre")
        self.track_list.column("STATUS", width=100, anchor="center")
        self.track_list.column("FICHIER", width=350)
        self.track_list.column("ARTISTE", width=250)
        self.track_list.column("TITRE", width=350)
        self.track_list.grid(row=0, column=0, sticky="nsew")
        self.track_list.bind("<Double-1>", self._on_double_click_item)

        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.track_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.track_list.configure(yscrollcommand=scrollbar.set)

        # Barre de progression
        self.progress_bar = customtkinter.CTkProgressBar(self.main_container)
        self.progress_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

    def _create_detail_view(self):
        """Crée les widgets de la vue détaillée, initialement cachée."""
        self.detail_view = customtkinter.CTkFrame(self, fg_color="transparent")
        self.detail_view.grid_columnconfigure(1, weight=3)
        self.detail_view.grid_columnconfigure(0, weight=1)

        # --- Partie gauche : pochette et boutons ---
        left_frame = customtkinter.CTkFrame(self.detail_view)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        left_frame.grid_rowconfigure(0, weight=1)
        
        # Pochette
        self.artwork_label = customtkinter.CTkLabel(
            left_frame, 
            text="🎨 Pochette", 
            width=250, 
            height=250,
            fg_color="#1f1f1f"
        )
        self.artwork_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Boutons
        detail_buttons_frame = customtkinter.CTkFrame(left_frame, fg_color="transparent")
        detail_buttons_frame.grid(row=1, column=0, padx=10, pady=20, sticky="s")
        
        self.back_button = customtkinter.CTkButton(
            detail_buttons_frame, 
            text="⬅️ Retour à la liste", 
            command=self._switch_to_main_view
        )
        self.back_button.pack(pady=5)
        
        self.save_button = customtkinter.CTkButton(
            detail_buttons_frame, 
            text="💾 Sauvegarder & Écrire",
            fg_color="green",
            command=self._save_current_track
        )
        self.save_button.pack(pady=5)

        # Bouton pour éditer les tags
        self.edit_tags_button = customtkinter.CTkButton(
            detail_buttons_frame,
            text="✏️ Éditer les tags",
            fg_color="blue",
            command=self._open_tag_editor
        )
        self.edit_tags_button.pack(pady=5)

        # --- Partie droite : champs de détails ---
        right_frame = customtkinter.CTkFrame(self.detail_view)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(1, weight=1)

        # Champs de texte
        self.title_entry = self._create_detail_entry(right_frame, "🎵 Titre:", 0)
        self.artist_entry = self._create_detail_entry(right_frame, "🎤 Artiste:", 1)
        self.album_entry = self._create_detail_entry(right_frame, "💿 Album:", 2)
        self.year_entry = self._create_detail_entry(right_frame, "📅 Année:", 3)
        self.genre_entry = self._create_detail_entry(right_frame, "🎭 Genre:", 4)
        self.key_entry = self._create_detail_entry(right_frame, "🎹 Clé:", 5)
        self.bpm_entry = self._create_detail_entry(right_frame, "⏱️ BPM:", 6)

        # Slider énergie
        customtkinter.CTkLabel(right_frame, text="⚡ Énergie:").grid(
            row=7, column=0, padx=10, pady=5, sticky="w"
        )
        self.energy_slider = customtkinter.CTkSlider(
            right_frame, 
            from_=1, 
            to=10, 
            number_of_steps=9
        )
        self.energy_slider.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        self.energy_value_label = customtkinter.CTkLabel(right_frame, text="5", width=20)
        self.energy_value_label.grid(row=7, column=2, padx=(0, 10), pady=5, sticky="w")
        self.energy_slider.configure(
            command=lambda v: self.energy_value_label.configure(text=f"{int(v)}")
        )

        # Commentaires (contextes/moments)
        customtkinter.CTkLabel(
            right_frame, 
            text="💭 Commentaires (Contextes/Moments):"
        ).grid(row=8, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="w")
        
        self.comments_pills_container = customtkinter.CTkScrollableFrame(
            right_frame, 
            label_text="", 
            fg_color="transparent", 
            height=60
        )
        self.comments_pills_container.grid(
            row=9, column=0, columnspan=3, padx=5, pady=2, sticky="ew"
        )

        # Grouping (styles)
        customtkinter.CTkLabel(
            right_frame, 
            text="🎯 Grouping (Styles):"
        ).grid(row=10, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="w")
        
        self.grouping_pills_container = customtkinter.CTkScrollableFrame(
            right_frame, 
            label_text="", 
            fg_color="transparent", 
            height=60
        )
        self.grouping_pills_container.grid(
            row=11, column=0, columnspan=3, padx=5, pady=2, sticky="ew"
        )

        # Label info
        customtkinter.CTkLabel(
            right_frame,
            text="🏷️ Label (Pays | Sample):"
        ).grid(row=12, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="w")
        
        self.label_display = customtkinter.CTkLabel(
            right_frame,
            text="",
            fg_color="#1f1f1f",
            corner_radius=5,
            padx=10,
            pady=5
        )
        self.label_display.grid(row=13, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def _create_detail_entry(self, parent, label_text, row):
        """Crée un champ d'entrée avec label pour la vue détaillée."""
        customtkinter.CTkLabel(parent, text=label_text).grid(
            row=row, column=0, padx=10, pady=5, sticky="w"
        )
        entry = customtkinter.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def _switch_to_main_view(self):
        """Affiche la vue principale et cache la vue détaillée."""
        self.detail_view.grid_forget()
        self.main_container.grid(row=0, column=0, sticky="nsew")

    def _switch_to_detail_view(self):
        """Affiche la vue détaillée et cache la vue principale."""
        self.main_container.grid_forget()
        self.detail_view.grid(row=0, column=0, sticky="nsew")
    
    def _test_detail_view(self):
        """Méthode de test pour accéder directement à la vue détaillée."""
        # Créer des données de test
        test_data = {
            'title': 'Titre de Test',
            'artist': 'Artiste de Test', 
            'album': 'Album de Test',
            'year': '2024',
            'genre': 'Electronic',
            'key': 'C minor',
            'bpm': '128',
            'energy': 7,
            'comment_tags': ['#[Soirée]', '#[Dansant]', '#[Commercial]'],
            'grouping_tags': ['#House', '#Progressive'],
            'label': '🇫🇷 France | Sample: Daft Punk - One More Time',
            'artwork_bytes': None
        }
        
        # Simuler un fichier de test
        self.current_track_file_path = "/test/file.mp3"
        self.all_track_data[self.current_track_file_path] = test_data
        
        # Remplir et afficher la vue détaillée
        self.populate_detail_view(test_data)
        self._switch_to_detail_view()

    # ===================================================================
    # 2. GESTION DES FICHIERS ET ANALYSE
    # ===================================================================

    def add_files(self):
        """Ouvre un sélecteur de fichiers et ajoute les fichiers audio à la liste."""
        file_types = [
            ("Fichiers audio", "*.mp3 *.m4a *.flac *.wav *.aiff *.ogg"),
            ("Tous les fichiers", "*.*")
        ]
        
        new_files = filedialog.askopenfilenames(
            title="Sélectionnez les fichiers audio",
            filetypes=file_types
        )
        
        for file_path in new_files:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                filename = os.path.basename(file_path)
                
                # Tenter d'extraire artiste et titre du nom de fichier
                try:
                    artist, title = filename.rsplit(' - ', 1)
                    title = title.split('.')[0]  # Enlever l'extension
                except ValueError:
                    artist, title = "Inconnu", filename
                
                # Ajouter à la liste visuelle
                self.track_list.insert("", "end", values=(
                    "En attente", filename, artist, title
                ))

    def analyze_all_tracks(self):
        """Lance l'analyse de tous les morceaux dans un thread séparé."""
        if not self.file_paths:
            messagebox.showwarning("Aucun fichier", "Veuillez d'abord ajouter des fichiers à analyser.")
            return
            
        Thread(target=self._run_analysis_sync, daemon=True).start()

    def _run_analysis_sync(self):
        """Exécute l'analyse de manière synchrone dans un thread."""
        # Créer une nouvelle boucle d'événements pour ce thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._analyze_all_async())
        finally:
            loop.close()

    async def _analyze_all_async(self):
        """Analyse tous les morceaux de manière asynchrone."""
        total_files = len(self.file_paths)
        
        for i, file_path in enumerate(self.file_paths):
            try:
                # Mettre à jour le statut
                self.after(0, self.update_track_status_in_ui, file_path, "En cours...")
                
                # Analyser le fichier
                analysis_result = await self.orchestrator.analyze_file(file_path)
                
                # Stocker le résultat
                self.all_track_data[file_path] = analysis_result
                
                # Mettre à jour l'UI
                self.after(0, self.update_track_status_in_ui, file_path, "✅ Analysé", analysis_result)
                
                # Mettre à jour la barre de progression
                progress = (i + 1) / total_files
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                
            except Exception as e:
                print(f"Erreur analyse {file_path}: {e}")
                self.after(0, self.update_track_status_in_ui, file_path, f"❌ Erreur")

    def update_track_status_in_ui(self, file_path, status, analysis_result=None):
        """Met à jour le statut d'un morceau dans l'interface utilisateur."""
        filename = os.path.basename(file_path)
        
        # Trouver l'item dans la liste
        for item in self.track_list.get_children():
            values = self.track_list.item(item, "values")
            if values[1] == filename:  # Comparer par nom de fichier
                if analysis_result:
                    # Mettre à jour avec les données d'analyse
                    new_values = (
                        status,
                        values[1],  # Garder le nom de fichier
                        analysis_result.get('artist', values[2]),
                        analysis_result.get('title', values[3])
                    )
                else:
                    # Juste mettre à jour le statut
                    new_values = (status, values[1], values[2], values[3])
                
                self.track_list.item(item, values=new_values)
                break

    def _on_double_click_item(self, event):
        """Gère le double-clic sur un élément de la liste."""
        selection = self.track_list.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.track_list.item(item, "values")
        filename = values[1]
        
        # Trouver le chemin complet
        full_path = self.get_full_path_from_filename(filename)
        if not full_path:
            messagebox.showerror("Erreur", "Impossible de trouver le fichier.")
            return
        
        # Vérifier si le morceau a été analysé
        if full_path not in self.all_track_data:
            messagebox.showwarning(
                "Analyse requise", 
                "Ce morceau n'a pas encore été analysé. Veuillez d'abord lancer l'analyse."
            )
            return

        # Afficher la vue détaillée
        self.current_track_file_path = full_path
        self.populate_detail_view(self.all_track_data[full_path])
        self._switch_to_detail_view()

    def populate_detail_view(self, track_data: Dict[str, Any]):
        """Remplit la vue détaillée avec les données du morceau."""
        self._clear_detail_view()

        def safe_insert(entry_widget, data_key: str, default_value: str = ""):
            """Fonction sécurisée pour insérer du texte dans un widget."""
            value = track_data.get(data_key, default_value) 
            text_to_insert = str(value) if value is not None else default_value
            
            try:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, text_to_insert)
            except tk.TclError as e:
                print(f"Erreur insertion {data_key}: {e}")

        # Remplissage sécurisé des champs
        safe_insert(self.title_entry, 'title')
        safe_insert(self.artist_entry, 'artist')
        safe_insert(self.album_entry, 'album')
        safe_insert(self.year_entry, 'year')
        safe_insert(self.genre_entry, 'genre')
        safe_insert(self.key_entry, 'key')
        safe_insert(self.bpm_entry, 'bpm', '')

        # Slider énergie
        energy = 5
        try:
            energy_value = track_data.get('energy')
            if energy_value is not None:
                energy = int(float(energy_value))
                energy = max(1, min(10, energy))  # Clamp entre 1 et 10
        except (ValueError, TypeError):
            energy = 5
        
        self.energy_slider.set(energy)
        self.energy_value_label.configure(text=str(energy))
        
        # Tags
        comment_tags = track_data.get('comment_tags', [])
        self._populate_pill_box(self.comments_pills_container, comment_tags)
        
        grouping_tags = track_data.get('grouping_tags', [])
        self._populate_pill_box(self.grouping_pills_container, grouping_tags)
        
        # Label
        label_text = track_data.get('label', '')
        self.label_display.configure(text=label_text if label_text else "Pas de label")
        
        # Afficher la pochette si disponible
        artwork_bytes = track_data.get('artwork_bytes')
        if artwork_bytes:
            try:
                image = Image.open(io.BytesIO(artwork_bytes))
                image = image.resize((250, 250), Image.Resampling.LANCZOS)
                self.artwork_image = ImageTk.PhotoImage(image)
                self.artwork_label.configure(image=self.artwork_image, text="")
            except Exception as e:
                print(f"Erreur affichage pochette: {e}")
                self.artwork_label.configure(image=None, text="🎨 Pochette\n(Erreur)")
        else:
            self.artwork_label.configure(image=None, text="🎨 Pas de\npochette")

    def _save_current_track(self):
        """Sauvegarde les modifications du morceau actuel."""
        if not self.current_track_file_path:
            return
        
        try:
            # Récupérer les valeurs des champs
            track_data = self.all_track_data[self.current_track_file_path].copy()
            
            # Mettre à jour avec les valeurs de l'UI
            track_data.update({
                'title': self.title_entry.get(),
                'artist': self.artist_entry.get(),
                'album': self.album_entry.get(),
                'year': self.year_entry.get(),
                'genre': self.genre_entry.get(),
                'key': self.key_entry.get(),
                'bpm': self.bpm_entry.get(),
                'energy': int(self.energy_slider.get())
            })
            
            # Récupérer les tags des pilules
            comment_tags = self._get_tags_from_pills(self.comments_pills_container)
            grouping_tags = self._get_tags_from_pills(self.grouping_pills_container)
            
            track_data['comment_tags'] = comment_tags
            track_data['grouping_tags'] = grouping_tags
            
            # Convertir les listes de tags en strings
            track_data['comment'] = " ".join(comment_tags) if comment_tags else ""
            track_data['grouping'] = " ".join(grouping_tags) if grouping_tags else ""
            
            # Sauvegarder dans la mémoire
            self.all_track_data[self.current_track_file_path] = track_data
            
            # Créer le dictionnaire des tags pour TagWriter
            tags_to_write = {
                'TIT2': track_data.get('title', ''),        # Titre
                'TPE1': track_data.get('artist', ''),       # Artiste
                'TALB': track_data.get('album', ''),        # Album
                'TDRC': str(track_data.get('year', '')),    # Année
                'TCON': track_data.get('genre', ''),        # Genre
                'TKEY': track_data.get('key', ''),          # Clé
                'COMM': track_data.get('comment', ''),      # Commentaire
                'GRP1': track_data.get('grouping', ''),     # Grouping
                'TPUB': track_data.get('label', ''),        # Label
                'TBPM': str(track_data.get('bpm', ''))      # BPM
            }
            
            # Supprimer les tags vides
            tags_to_write = {k: v for k, v in tags_to_write.items() if v}
            
            # Écrire les tags dans le fichier
            success = self.tag_writer.write_tags(
                self.current_track_file_path,
                tags_to_write,
                track_data.get('artwork_bytes')
            )
            
            if success:
                messagebox.showinfo("Succès", "Tags sauvegardés avec succès!")
                self.update_track_status_in_ui(self.current_track_file_path, "💾 Sauvé")
            else:
                messagebox.showerror("Erreur", "Échec de la sauvegarde des tags.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

    def _clear_detail_view(self):
        """Vide tous les champs de la vue détaillée."""
        try:
            for entry in [self.title_entry, self.artist_entry, self.album_entry, 
                         self.year_entry, self.genre_entry, self.key_entry, self.bpm_entry]:
                entry.delete(0, tk.END)
            
            self.energy_slider.set(5)
            self.energy_value_label.configure(text="5")
            self._clear_pill_box(self.comments_pills_container)
            self._clear_pill_box(self.grouping_pills_container)
            self.artwork_label.configure(image="", text="🎨 Pochette")
            self.label_display.configure(text="")
        except Exception as e:
            print(f"Erreur nettoyage vue détaillée : {e}")

    def _populate_pill_box(self, parent_frame, tags: List[str]):
        """Remplit un conteneur avec des 'pilules' pour les tags."""
        self._clear_pill_box(parent_frame)
        
        for tag in tags:
            # Nettoyer le tag pour l'affichage
            display_tag = tag.replace('#[', '').replace(']', '').replace('#', '')
            
            pill_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
            pill_frame.pack(side="left", padx=2, pady=2)
            
            pill = customtkinter.CTkLabel(
                pill_frame,
                text=display_tag,
                fg_color="#4ECDC4",
                text_color="black",
                corner_radius=10,
                padx=8,
                pady=2
            )
            pill.pack(side="left")
            
            # Bouton de suppression
            delete_btn = customtkinter.CTkButton(
                pill_frame,
                text="×",
                width=20,
                height=20,
                fg_color="#FF6B6B",
                hover_color="#FF5252",
                command=lambda f=pill_frame: f.destroy()
            )
            delete_btn.pack(side="left", padx=2)
            
            # Stocker le tag original dans le frame
            pill_frame.tag_value = tag

    def _get_tags_from_pills(self, parent_frame) -> List[str]:
        """Récupère les tags depuis les pilules d'un conteneur."""
        tags = []
        for widget in parent_frame.winfo_children():
            if hasattr(widget, 'tag_value'):
                tags.append(widget.tag_value)
        return tags

    def _clear_pill_box(self, parent_frame):
        """Vide un conteneur de pilules."""
        for widget in parent_frame.winfo_children():
            widget.destroy()

    def get_full_path_from_filename(self, filename: str) -> Optional[str]:
        """Trouve le chemin complet à partir du nom de fichier."""
        for path in self.file_paths:
            if os.path.basename(path) == filename:
                return path
        return None

    def _open_tag_editor(self):
        """Ouvre un éditeur pour ajouter/modifier les tags."""
        if not self.current_track_file_path:
            return
            
        # Créer une fenêtre popup simple
        editor = tk.Toplevel(self)
        editor.title("Éditer les tags")
        editor.geometry("400x300")
        
        # Instructions
        tk.Label(editor, text="Entrez un nouveau tag:").pack(pady=10)
        
        # Champ de saisie
        tag_entry = tk.Entry(editor, width=30)
        tag_entry.pack(pady=5)
        
        # Type de tag
        tag_type = tk.StringVar(value="context")
        tk.Radiobutton(editor, text="Contexte/Moment", variable=tag_type, value="context").pack()
        tk.Radiobutton(editor, text="Style", variable=tag_type, value="style").pack()
        
        def add_tag():
            new_tag = tag_entry.get().strip()
            if new_tag:
                if tag_type.get() == "context":
                    # Format contexte : #[Tag]
                    formatted_tag = f"#[{new_tag}]" if not new_tag.startswith("#[") else new_tag
                    current_tags = self._get_tags_from_pills(self.comments_pills_container)
                    if formatted_tag not in current_tags:
                        current_tags.append(formatted_tag)
                        self._populate_pill_box(self.comments_pills_container, current_tags)
                else:
                    # Format style : #Tag
                    formatted_tag = f"#{new_tag}" if not new_tag.startswith("#") else new_tag
                    current_tags = self._get_tags_from_pills(self.grouping_pills_container)
                    if formatted_tag not in current_tags:
                        current_tags.append(formatted_tag)
                        self._populate_pill_box(self.grouping_pills_container, current_tags)
                
                tag_entry.delete(0, tk.END)
        
        tk.Button(editor, text="Ajouter", command=add_tag).pack(pady=10)
        tk.Button(editor, text="Fermer", command=editor.destroy).pack()

    def _open_settings(self):
        """Ouvre la fenêtre de configuration des APIs."""
        # Fenêtre simple de configuration
        settings = tk.Toplevel(self)
        settings.title("Configuration des APIs")
        settings.geometry("500x400")
        
        # Charger la config actuelle
        current_config = self._load_current_config()
        
        # Créer les champs
        fields = {
            'SPOTIFY_CLIENT_ID': tk.StringVar(value=current_config.get('spotify_client_id', '')),
            'SPOTIFY_CLIENT_SECRET': tk.StringVar(value=current_config.get('spotify_client_secret', '')),
            'DISCOGS_TOKEN': tk.StringVar(value=current_config.get('discogs_token', '')),
            'OPENAI_API_KEY': tk.StringVar(value=current_config.get('openai_api_key', ''))
        }
        
        row = 0
        for key, var in fields.items():
            tk.Label(settings, text=f"{key}:").grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(settings, textvariable=var, width=40)
            if 'SECRET' in key or 'KEY' in key or 'TOKEN' in key:
                entry.config(show="*")
            entry.grid(row=row, column=1, padx=10, pady=5)
            row += 1
        
        def save_config():
            # Sauvegarder dans .env
            env_path = Path(__file__).parent.parent / '.env'
            
            with open(env_path, 'w') as f:
                for key, var in fields.items():
                    value = var.get()
                    if value:
                        f.write(f"{key}={value}\n")
            
            messagebox.showinfo("Succès", "Configuration sauvegardée. Veuillez redémarrer l'application.")
            settings.destroy()
        
        tk.Button(settings, text="Sauvegarder", command=save_config).grid(row=row, column=0, columnspan=2, pady=20)

    def _load_current_config(self) -> Dict:
        """Charge la configuration actuelle depuis le fichier .env."""
        config = {}
        env_path = Path(__file__).parent.parent / '.env'
        
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key == 'SPOTIFY_CLIENT_ID':
                                config['spotify_client_id'] = value
                            elif key == 'SPOTIFY_CLIENT_SECRET':
                                config['spotify_client_secret'] = value
                            elif key == 'DISCOGS_TOKEN':
                                config['discogs_token'] = value
                            elif key == 'OPENAI_API_KEY':
                                config['openai_api_key'] = value
            except Exception as e:
                print(f"Erreur lecture .env : {e}")
        
        return config