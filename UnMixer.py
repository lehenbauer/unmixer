import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

import unmix
from unmix import store

create_console = True


class MyGUI:
    def __init__(self, root):
        self.root = root
        self.stem_vars = {}
        self.backing_track_vars = {}
        self.elements = [
            "vocals",
            "drum",
            "bass",
            "piano",
            "electric_guitar",
            "acoustic_guitar",
            "synthesizer",
            "voice",
            "strings",
            "wind",
        ]
        self.api_key = tk.StringVar()
        self.tk_output_dir = tk.StringVar()

        store = unmix.KeyValueStore(os.path.expanduser("~/.unmixer.sqlite3"))

        # Get output directory or set to default
        self.output_dir = store.get("output_dir")
        if not self.output_dir:
            self.output_dir = os.path.expanduser("~/Downloads")
            store.set("output_dir", self.output_dir)

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Unmixer - Stem and Backing Track Extractor")

        next_row = 0  # Variable to track the next row position

        tk.Label(self.root, text="Stems", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Label(self.root, text="Backing Tracks", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=1, sticky="w"
        )
        next_row += 1  # Increment the row position

        for i, element in enumerate(self.elements):
            self.stem_vars[element] = tk.BooleanVar()
            tk.Checkbutton(
                self.root, text=element, variable=self.stem_vars[element]
            ).grid(row=next_row, column=0, sticky="w")

            self.backing_track_vars[element] = tk.BooleanVar()
            tk.Checkbutton(
                self.root, text=element, variable=self.backing_track_vars[element]
            ).grid(row=next_row, column=1, sticky="w")

            next_row += 1

        self.filter = tk.IntVar()  # Initialize filter variable
        self.splitter = tk.StringVar()  # Initialize splitter variable

        # Filter and Splitter options
        tk.Label(self.root, text="Filter", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Label(self.root, text="Splitter", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=1, sticky="w"
        )
        next_row += 1

        tk.Radiobutton(self.root, text="Mild", variable=self.filter, value=0).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Radiobutton(
            self.root, text="Phoenix", variable=self.splitter, value="phoenix"
        ).grid(row=next_row, column=1, sticky="w")
        next_row += 1

        tk.Radiobutton(self.root, text="Normal", variable=self.filter, value=1).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Radiobutton(
            self.root, text="Cassiopeia", variable=self.splitter, value="cassiopeia"
        ).grid(row=next_row, column=1, sticky="w")
        next_row += 1

        tk.Radiobutton(
            self.root, text="Aggressive", variable=self.filter, value=2
        ).grid(row=next_row, column=0, sticky="w")
        next_row += 1

        # API Key
        tk.Label(self.root, text="API Key", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.api_key, width=16).grid(
            row=next_row, column=1, sticky="we"
        )
        tk.Button(self.root, text="Save", command=self.save_api_key).grid(
            row=next_row, column=2
        )
        next_row += 1

        # Output dir
        tk.Label(self.root, text="Save to", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Entry(self.root, textvariable=self.tk_output_dir, width=16).grid(
            row=next_row, column=1, sticky="we"
        )
        tk.Button(self.root, text="Change", command=self.set_output_dir).grid(
            row=next_row, column=2
        )
        next_row += 1

        # Set default values
        self.api_key.set(self.fetch_api_key())
        self.filter.set(1)  # Default filter value
        self.splitter.set("phoenix")  # Default splitter value
        self.stem_vars["vocals"].set(True)
        self.backing_track_vars["vocals"].set(True)
        self.tk_output_dir.set(self.output_dir)

        tk.Button(self.root, text="Run", command=self.run_program).grid(
            row=next_row, column=0, columnspan=2
        )

        # Configure grid to resize properly
        self.root.grid_rowconfigure(
            next_row + 1, weight=1
        )  # Add row configuration for resizing
        self.root.grid_columnconfigure(
            0, weight=1
        )  # Allow column 0 to resize horizontally
        self.root.grid_columnconfigure(
            1, weight=1
        )  # Allow column 1 to resize horizontally
        self.root.grid_columnconfigure(
            2, weight=1
        )  # Allow column 2 to resize horizontally

    def save_api_key(self):
        key = self.api_key.get().strip()
        if len(key) != 16 or not all(c in "0123456789abcdefABCDEF" for c in key):
            messagebox.showerror(
                "Invalid API Key", "API Key must be 16 hexadecimal characters"
            )
            return
        store.set("api_key", key)

    def fetch_api_key(self):
        api_key = store.get("api_key")
        if not api_key:
            api_key = ""
        return api_key

    def set_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            store.set("output_dir", self.output_dir)
            self.tk_output_dir.set(self.output_dir)

    def run_program(self):
        stems = [stem for stem, var in self.stem_vars.items() if var.get()]
        backing_tracks = [
            track for track, var in self.backing_track_vars.items() if var.get()
        ]
        which_filter = self.filter.get()
        splitter = self.splitter.get()
        api_key = self.api_key.get().strip()
        if api_key == "":
            messagebox.showerror("No API Key", "Please set an API Key")
            return

        if len(stems) == 0 and len(backing_tracks) == 0:
            messagebox.showerror(
                "No Stems", "Please select at least one stem or backing track"
            )
            return
        file_path = filedialog.askopenfilename()

        # print(f'PATH: {os.environ.get("PATH")}')
        # print(f"environ: {os.environ}")
        # print(f"sys.executable: {sys.executable}")
        # print(f'"{file_path}"')
        # print("Stems: ", stems)
        # print("Backing Tracks: ", backing_tracks)
        # print("Filter: ", which_filter)
        # print("Splitter: ", splitter)
        unmix.run_lalal_in_thread(
            input_file=file_path,
            stems=stems,
            backing_tracks=backing_tracks,
            which_filter=which_filter,
            splitter=splitter,
        )
        # self.root.quit()


root = tk.Tk()
root.my_gui = MyGUI(root)
if create_console:
    unmix.create_console(tk)
print("yo baby yo baby yo")
print(f"current dir: {os.getcwd()}")
root.mainloop()
