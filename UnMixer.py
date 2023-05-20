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
        self.status_message = {}

        store = unmix.KeyValueStore(os.path.expanduser("~/.unmixer.sqlite3"))

        # Get output directory or set to default
        self.output_dir = store.get("output_dir")
        if not self.output_dir:
            self.output_dir = os.path.expanduser("~/Downloads")
            store.set("output_dir", self.output_dir)

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Unmixer - Stem and Backing Track Extractor")

        self.frame1 = tk.Frame(self.root)
        self.frame1.grid(row=0, column=0, sticky="nsew")

        self.frame2 = tk.Frame(self.root)
        self.frame2.grid(row=1, column=0, sticky="nsew")

        # GUI elements for frame1
        # Stems, Backing Tracks, Labels, Filter, and Splitter

        next_row = 0  # Variable to track the next row position in frame 1

        tk.Label(self.frame1, text="Stems", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Label(
            self.frame1, text="Backing Tracks", font=("Helvetica", 14, "bold")
        ).grid(row=next_row, column=1, sticky="w")
        next_row += 1  # Increment the row position

        for i, element in enumerate(self.elements):
            self.stem_vars[element] = tk.BooleanVar()
            tk.Checkbutton(
                self.frame1, text=element, variable=self.stem_vars[element]
            ).grid(row=next_row, column=0, sticky="w")

            self.backing_track_vars[element] = tk.BooleanVar()
            tk.Checkbutton(
                self.frame1, text=element, variable=self.backing_track_vars[element]
            ).grid(row=next_row, column=1, sticky="w")

            # Status message label for each stem and backing track
            status_label = tk.Label(
                self.frame1,
                text="",
                font=("Helvetica", 12),
                width=20,
                relief="ridge",
                padx=10,
            )
            status_label.grid(row=next_row, column=2, sticky="ew")
            self.status_message[element] = status_label

            next_row += 1

        self.filter = tk.IntVar()  # Initialize filter variable
        self.splitter = tk.StringVar()  # Initialize splitter variable

        # Filter and Splitter options
        tk.Label(self.frame1, text="Filter", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Label(self.frame1, text="Splitter", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=1, sticky="w"
        )
        next_row += 1

        tk.Radiobutton(self.frame1, text="Mild", variable=self.filter, value=0).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Radiobutton(
            self.frame1, text="Phoenix", variable=self.splitter, value="phoenix"
        ).grid(row=next_row, column=1, sticky="w")
        next_row += 1

        tk.Radiobutton(self.frame1, text="Normal", variable=self.filter, value=1).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Radiobutton(
            self.frame1, text="Cassiopeia", variable=self.splitter, value="cassiopeia"
        ).grid(row=next_row, column=1, sticky="w")
        next_row += 1

        tk.Radiobutton(
            self.frame1, text="Aggressive", variable=self.filter, value=2
        ).grid(row=next_row, column=0, sticky="w")
        next_row += 1

        # GUI elements for frame2
        # API Key, Save to, Run

        next_row = 0

        # API Key
        tk.Label(self.frame2, text="API Key", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Entry(self.frame2, textvariable=self.api_key, width=16).grid(
            row=next_row, column=1, sticky="we"
        )
        tk.Button(self.frame2, text="Save", command=self.save_api_key).grid(
            row=next_row, column=2
        )
        next_row += 1

        # Output dir
        tk.Label(self.frame2, text="Save to", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Entry(self.frame2, textvariable=self.tk_output_dir, width=16).grid(
            row=next_row, column=1, sticky="we"
        )
        tk.Button(self.frame2, text="Change", command=self.set_output_dir).grid(
            row=next_row, column=2
        )
        next_row += 1

        tk.Button(self.root, text="Run", command=self.run_program).grid(
            row=next_row, column=0, columnspan=2
        )
        next_row += 1

        self.filter.set(1)
        self.splitter.set("phoenix")
        self.stem_vars["vocals"].set(True)
        self.backing_track_vars["vocals"].set(True)

        # Grid column configurations for frame1
        self.frame1.grid_columnconfigure(0, weight=0)  # Column 0 not resizable
        self.frame1.grid_columnconfigure(1, weight=0)  # Column 1 not resizable
        self.frame1.grid_columnconfigure(2, weight=1)  # Column 2 resizable

        # Grid column configurations for frame2
        self.frame2.grid_columnconfigure(0, weight=0)  # Column 0 not resizable
        self.frame2.grid_columnconfigure(1, weight=1)  # Column 1 resizable
        self.frame2.grid_columnconfigure(2, weight=0)  # Column 2 not resizable

        # Configure grid to resize properly
        self.root.grid_rowconfigure(0, weight=1)  # Allow frame1 to resize vertically
        self.root.grid_rowconfigure(1, weight=1)  # Allow frame2 to resize vertically
        self.root.grid_columnconfigure(0, weight=1)  # Allow root to resize horizontally

        self.root.update()  # Force update for the window to calculate its size

        # set the minimum window size to the original size
        width_height = self.root.geometry().split("+")[0]
        width, height = map(int, width_height.split("x"))
        self.root.minsize(width, height)

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
