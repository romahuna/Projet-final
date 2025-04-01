import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorateur de Fichiers")
        self.root.geometry("1000x600")
        self.root.config(bg="#f4f4f9")  # Fond clair pour toute l'application

        # Variables
        self.current_path = os.path.expanduser("~")
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Créer l'interface
        self.create_ui()

    def create_ui(self):
        # Barre de chemin
        self.path_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.path_entry = tk.Entry(self.path_frame, width=80, font=("Helvetica", 12), bg="#e2e2e2")
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Boutons de navigation
        nav_frame = tk.Frame(self.root, bg="#f4f4f9")
        nav_frame.pack(fill=tk.X, padx=10)
        
        buttons = [
            ("🏠", self.go_home),
            ("↑", self.go_parent),
            ("➕", self.create_folder),
            ("🔄", self.refresh_list)
        ]
        
        for label, command in buttons:
            btn = tk.Button(nav_frame, text=label, command=command, font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat")
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Cadre principal avec colonnes
        main_frame = tk.Frame(self.root, bg="#f4f4f9")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Colonne gauche pour les favoris
        favorites_frame = tk.Frame(main_frame, bg="#f4f4f9")
        favorites_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(favorites_frame, text="Favoris", font=("Helvetica", 14, "bold"), bg="#f4f4f9").pack()
        self.favorites_listbox = tk.Listbox(favorites_frame, width=20, font=("Helvetica", 12), height=15, bg="#e2e2e2", selectmode=tk.SINGLE)
        self.favorites_listbox.pack(expand=True, fill=tk.BOTH)
        self.favorites_listbox.bind('<Double-1>', self.open_favorite)  # Double-clic pour ouvrir un favori
        
        self.update_favorites_list()

        # Colonne droite pour la liste des fichiers
        files_frame = tk.Frame(main_frame, bg="#f4f4f9")
        files_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Barre de recherche
        search_frame = tk.Frame(files_frame, bg="#f4f4f9")
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="Recherche:", font=("Helvetica", 12), bg="#f4f4f9").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 12), bg="#e2e2e2")
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.filter_files)

        # Bouton réinitialiser la recherche
        self.reset_button = tk.Button(search_frame, text="Réinitialiser", command=self.reset_search, font=("Helvetica", 12), bg="#f44336", fg="white", relief="flat")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Liste des fichiers
        self.file_listbox = tk.Listbox(files_frame, selectmode=tk.EXTENDED, font=("Helvetica", 12), height=15, bg="#e2e2e2")
        self.file_listbox.pack(expand=True, fill=tk.BOTH)
        self.file_listbox.bind('<ButtonRelease-1>', self.show_details)  # Clic simple pour afficher les détails
        self.file_listbox.bind('<Double-1>', self.open_item)  # Double-clic pour ouvrir l'élément
        self.file_listbox.bind('<Button-3>', self.show_context_menu)

        # Détails du fichier
        details_frame = tk.Frame(self.root, bg="#f4f4f9")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.details_label = tk.Label(details_frame, text="Sélectionnez un fichier pour voir les détails", font=("Helvetica", 12), bg="#f4f4f9")
        self.details_label.pack()

        self.update_file_list()
        self.update_path_display()

    def update_file_list(self, path=None):
        if path:
            self.current_path = path
        
        try:
            files = os.listdir(self.current_path)
            self.file_listbox.delete(0, tk.END)
            
            for item in files:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    self.file_listbox.insert(tk.END, f"📁 {item}")
                else:
                    self.file_listbox.insert(tk.END, f"📄 {item}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def update_path_display(self):
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.current_path)

    def show_details(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])
        item_name = item[2:]  # Enlève l'emoji
        full_path = os.path.join(self.current_path, item_name)

        if os.path.exists(full_path):
            file_details = self.get_file_details(full_path)
            self.details_label.config(text=file_details)
        else:
            self.details_label.config(text="Erreur: Le fichier ou le dossier n'existe plus.")

    def get_file_details(self, file_path):
        try:
            # Récupérer la taille du fichier
            file_size = os.path.getsize(file_path)
            # Convertir la taille en Mo
            file_size_mb = file_size / (1024 * 1024)
            file_size_mb = round(file_size_mb, 2)
            
            # Récupérer la date de dernière modification
            modification_time = os.path.getmtime(file_path)
            mod_time = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')

            # Construction du texte des détails
            details = (
                f"Nom: {os.path.basename(file_path)}\n"
                f"Taille: {file_size_mb} MB\n"
                f"Modifié le: {mod_time}"
            )
            return details
        except Exception as e:
            return f"Erreur lors de la récupération des détails : {e}"

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Ouvrir", command=self.open_item)
        context_menu.add_command(label="Renommer", command=self.rename_item)
        context_menu.add_command(label="Supprimer", command=self.delete_item)
        context_menu.add_command(label="Ajouter aux favoris", command=self.add_to_favorites)
        context_menu.post(event.x_root, event.y_root)

    def open_item(self, event=None):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])[2:]  # Enlève l'emoji
        full_path = os.path.join(self.current_path, item)

        if os.path.isdir(full_path):
            self.update_file_list(full_path)  # Ouvre le dossier
            self.update_path_display()
        elif os.path.isfile(full_path):
            os.startfile(full_path)  # Ouvre le fichier dans son application par défaut

    def open_favorite(self, event=None):
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        
        favorite_name = self.favorites_listbox.get(selection[0])
        favorite_path = [path for path in self.favorites if os.path.basename(path) == favorite_name][0]

        if os.path.isdir(favorite_path):
            self.update_file_list(favorite_path)  # Ouvre le dossier
            self.update_path_display()
        elif os.path.isfile(favorite_path):
            os.startfile(favorite_path)  # Ouvre le fichier dans son application par défaut

    def go_home(self):
        self.update_file_list(os.path.expanduser("~"))
        self.update_path_display()

    def go_parent(self):
        parent_path = os.path.dirname(self.current_path)
        self.update_file_list(parent_path)
        self.update_path_display()

    def create_folder(self):
        folder_name = simpledialog.askstring("Nouveau dossier", "Nom du dossier:")
        if folder_name:
            try:
                new_folder_path = os.path.join(self.current_path, folder_name)
                os.mkdir(new_folder_path)
                self.update_file_list()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def rename_item(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        old_name = self.file_listbox.get(selection[0])[2:]
        new_name = simpledialog.askstring("Renommer", f"Nouveau nom pour {old_name}:")
        
        if new_name:
            try:
                old_path = os.path.join(self.current_path, old_name)
                new_path = os.path.join(self.current_path, new_name)
                os.rename(old_path, new_path)
                self.update_file_list()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def delete_item(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])[2:]
        full_path = os.path.join(self.current_path, item)
        
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous supprimer {item}?")
        if confirm:
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                self.update_file_list()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def filter_files(self, event):
        search_term = self.search_entry.get().lower()
        self.file_listbox.delete(0, tk.END)
        
        try:
            files = os.listdir(self.current_path)
            for item in files:
                if search_term in item.lower():
                    full_path = os.path.join(self.current_path, item)
                    if os.path.isdir(full_path):
                        self.file_listbox.insert(tk.END, f"📁 {item}")
                    else:
                        self.file_listbox.insert(tk.END, f"📄 {item}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def reset_search(self):
        self.search_entry.delete(0, tk.END)
        self.update_file_list()  # Réinitialise la liste des fichiers

    def refresh_list(self):
        self.update_file_list()

    def load_favorites(self):
        try:
            with open(self.favorites_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_favorites(self):
        with open(self.favorites_file, 'w') as f:
            json.dump(self.favorites, f)

    def add_to_favorites(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        item = self.file_listbox.get(selection[0])[2:]
        full_path = os.path.join(self.current_path, item)
        
        if full_path not in self.favorites:
            self.favorites.append(full_path)
            self.save_favorites()
            self.update_favorites_list()

    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for path in self.favorites:
            self.favorites_listbox.insert(tk.END, os.path.basename(path))

    def go_to_favorite(self, event):
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        
        favorite_name = self.favorites_listbox.get(selection[0])
        favorite_path = [path for path in self.favorites if os.path.basename(path) == favorite_name][0]
        
        if os.path.exists(favorite_path):
            self.update_file_list(os.path.dirname(favorite_path))
            self.update_path_display()

def main():
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
