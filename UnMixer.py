

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

import unmix

class MyGUI:
    def __init__(self, root):
        self.root = root
        self.stem_vars = {}
        self.backing_track_vars = {}
        self.elements = ['vocals', 'drum', 'bass', 'piano', 'electric_guitar', 'acoustic_guitar', 'synthesizer', 'voice', 'strings', 'wind']
        self.api_key = tk.StringVar()
        self.setup_gui()


    def setup_gui(self):
        self.root.title("Unmixer - Stem and Backing Track Extractor")

        tk.Label(self.root, text="Stems", font=("Helvetica", 14, "bold")).grid(row=0, column=0, sticky='w')
        tk.Label(self.root, text="Backing Tracks", font=("Helvetica", 14, "bold")).grid(row=0, column=1, sticky='w')

        for i, element in enumerate(self.elements):
            self.stem_vars[element] = tk.BooleanVar()
            tk.Checkbutton(self.root, text=element, variable=self.stem_vars[element]).grid(row=i+1, column=0, sticky='w')

        for i, element in enumerate(self.elements):
            self.backing_track_vars[element] = tk.BooleanVar()
            tk.Checkbutton(self.root, text=element, variable=self.backing_track_vars[element]).grid(row=i+1, column=1, sticky='w')

        self.filter = tk.IntVar()  # Initialize filter variable
        self.splitter = tk.StringVar()  # Initialize splitter variable

        # Filter options
        tk.Label(self.root, text="Filter", font=("Helvetica", 14, "bold")).grid(row=len(self.elements)+2, column=0, sticky='w')
        tk.Radiobutton(self.root, text="Mild", variable=self.filter, value=0).grid(row=len(self.elements)+3, column=0, sticky='w')
        tk.Radiobutton(self.root, text="Normal", variable=self.filter, value=1).grid(row=len(self.elements)+4, column=0, sticky='w')
        tk.Radiobutton(self.root, text="Aggressive", variable=self.filter, value=2).grid(row=len(self.elements)+5, column=0, sticky='w')

        # Splitter options
        tk.Label(self.root, text="Splitter", font=("Helvetica", 14, "bold")).grid(row=len(self.elements)+2, column=1, sticky='w')
        tk.Radiobutton(self.root, text="Phoenix", variable=self.splitter, value="phoenix").grid(row=len(self.elements)+3, column=1, sticky='w')
        tk.Radiobutton(self.root, text="Cassiopeia", variable=self.splitter, value="cassiopeia").grid(row=len(self.elements)+4, column=1, sticky='w')

        # API Key
        tk.Label(self.root, text="API Key", font=("Helvetica", 14, "bold")).grid(row=len(self.elements)+6, column=0, sticky='w')
        tk.Entry(self.root, textvariable=self.api_key, width=16).grid(row=len(self.elements)+6, column=1, sticky='w')
        tk.Button(self.root, text='Save', command=self.save_api_key).grid(row=len(self.elements)+6, column=2)

        # Set default values
        self.api_key.set(self.fetch_api_key())
        self.filter.set(1)  # Default filter value
        self.splitter.set("phoenix")  # Default splitter value

        tk.Button(self.root, text='Run', command=self.run_program).grid(row=len(self.elements)+7, column=0, columnspan=2)

    def save_api_key(self):
        key = self.api_key.get().strip()
        if len(key) != 16 or not all(c in '0123456789abcdefABCDEF' for c in key):
            messagebox.showerror("Invalid API Key", "API Key must be 16 hexadecimal characters")
            return
        with open(".apikey", "w") as file:
            file.write(key)

    def fetch_api_key(self):
        if os.path.exists(".apikey"):
            with open(".apikey", "r") as file:
                return file.read().strip()
        return ""

    def run_program(self):
        stems = [stem for stem, var in self.stem_vars.items() if var.get()]
        backing_tracks = [track for track, var in self.backing_track_vars.items() if var.get()]
        filter = self.filter.get()
        splitter = self.splitter.get()
        api_key = self.api_key.get().strip()
        if api_key == '':
            messagebox.showerror("No API Key", "Please set an API Key")
            return

        if len(stems) == 0 and len(backing_tracks) == 0:
            messagebox.showerror("No Stems", "Please select at least one stem or backing track")
            return
        file_path = filedialog.askopenfilename()

        print(f'PATH: {os.environ.get("PATH")}')
        print(f'sys.executable: {sys.executable}')
        print(f'"{file_path}"')
        print("Stems: ", stems)
        print("Backing Tracks: ", backing_tracks)
        print("Filter: ", filter)
        print("Splitter: ", splitter)
        unmix.run_lalal(input_file=file_path, stems=stems, backing_tracks=backing_tracks, filter=filter, splitter=splitter)
        #self.root.quit()

root = tk.Tk()
root.my_gui = MyGUI(root)
unmix.create_console(tk)
print("yo baby yo baby yo")
print(f"current dir: {os.getcwd()}")
root.mainloop()
