import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter
from FlowTag_Pro.ui.settings_dialog import SettingsDialog

print("🚀 Test du dialogue de configuration...")

# Créer une fenêtre principale temporaire
root = customtkinter.CTk()
root.withdraw()  # La cacher

# Ouvrir le dialogue
print("📋 Ouverture du dialogue...")
dialog = SettingsDialog(root)
root.wait_window(dialog)

print("✅ Test terminé")
root.destroy()
