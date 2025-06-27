import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter
from FlowTag_Pro.ui.settings_dialog import SettingsDialog
import time

print("🚀 Test du dialogue de configuration...")

# Créer une fenêtre principale visible cette fois
root = customtkinter.CTk()
root.title("Test FloTag")
root.geometry("300x100")

# Créer un bouton pour ouvrir le dialogue
def open_dialog():
    print("📋 Ouverture du dialogue...")
    dialog = SettingsDialog(root)
    # Forcer la fenêtre au premier plan
    dialog.lift()
    dialog.attributes('-topmost', True)
    dialog.attributes('-topmost', False)
    dialog.focus_force()
    print("✅ Dialogue ouvert et forcé au premier plan")

button = customtkinter.CTkButton(
    root, 
    text="Cliquer ici pour ouvrir les paramètres", 
    command=open_dialog
)
button.pack(pady=20)

print("💡 Clique sur le bouton pour ouvrir le dialogue")
root.mainloop()
print("✅ Test terminé")
