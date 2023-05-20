import os
import queue
import sqlite3
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

import lalalai_splitter

create_console = True
hide_api_key = False


# Create a global queue for the threads to write their output to
output_queue = queue.Queue()


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area


class QueuedOutputRedirector(IORedirector):
    """A general class for redirecting I/O a python queue."""

    def write(self, str):
        # Write output to the queue instead of directly to the text area
        output_queue.put(str)

    def flush(self):
        # fake flush because we're not actually buffering anything
        pass


def create_console(tk, gui):
    """Create a console widget that will display stdout and stderr
    of this app including its child threads."""
    global console_widget

    root = tk.Tk()
    root.title("Unmix Debug Console")
    console_widget = tk.Text(root, wrap="word")
    console_widget.pack(expand=True, fill="both")

    sys.stdout = QueuedOutputRedirector(console_widget)
    sys.stderr = QueuedOutputRedirector(console_widget)

    # Schedule the first call to the function that checks the queue
    root.after(100, check_output_queue, gui)

    return console_widget


def check_output_queue(gui):
    # Schedule the next call to this function
    console_widget.after(100, check_output_queue, gui)

    # Check if there's something in the queue
    while not output_queue.empty():
        # If there is, write it to the text widget
        message = output_queue.get()
        console_widget.insert("end", message)

        try:
            if message.startswith("%"):
                handle_progress_message(gui, message)
        except Exception as e:
            console_widget.insert(f"exception handling progress message: {e}")
            console.widget.insert(traceback.format_exc())

        console_widget.see("end")


class UnmixGUI:
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
        self.overall_status = tk.StringVar()
        self.status_messages = {}

        store = KeyValueStore(os.path.expanduser("~/.unmixer.sqlite3"))

        self.tk_input_file = tk.StringVar()
        self.input_file = None

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
            self.status_messages[element] = tk.StringVar()
            status_label = tk.Label(
                self.frame1,
                textvariable=self.status_messages[element],
                font=("Helvetica", 12),
                width=20,
                relief="ridge",
                padx=10,
            )
            status_label.grid(row=next_row, column=2, sticky="ew")

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
        # Status, API Key, Save to, Run

        next_row = 0

        # Overall Status
        tk.Label(self.frame2, text="Status", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        status_label = tk.Label(
            self.frame2,
            textvariable=self.overall_status,
            font=("Courier", 14),
            width=40,
            relief="ridge",
            padx=10,
        ).grid(row=next_row, column=1, sticky="we")
        next_row += 1

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

        # Input file
        tk.Label(self.frame2, text="Input File", font=("Helvetica", 14, "bold")).grid(
            row=next_row, column=0, sticky="w"
        )
        tk.Entry(self.frame2, textvariable=self.tk_input_file, width=16).grid(
            row=next_row, column=1, sticky="we"
        )
        tk.Button(self.frame2, text="Pick", command=self.set_input_file).grid(
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
        tk.Button(self.frame2, text="Pick", command=self.set_output_dir).grid(
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
        self.tk_output_dir.set(store.get("output_dir"))

        if hide_api_key:
            self.api_key.set("0123456789abcdef")
        else:
            self.api_key.set(self.fetch_api_key())

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

    def set_stem_status(self, stem, message):
        self.status_messages[stem].set(message)

    def set_overall_status(self, message):
        self.overall_status.set(message)

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

    def set_input_file(self):
        self.input_file = filedialog.askopenfilename()
        self.tk_input_file.set(self.input_file if self.input_file else "")

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

        if not self.input_file or self.input_file == "":
            messagebox.showerror("No Input File", "Please select an input file")
            return

        if not os.path.isfile(self.input_file):
            messagebox.showerror("No Input File", "Input file doesn't exist.")
            return

        if len(stems) == 0 and len(backing_tracks) == 0:
            messagebox.showerror(
                "No Stems", "Please select at least one stem or backing track"
            )
            return

        # print(f'PATH: {os.environ.get("PATH")}')
        # print(f"environ: {os.environ}")
        # print(f"sys.executable: {sys.executable}")
        # print(f'"{file_path}"')
        # print("Stems: ", stems)
        # print("Backing Tracks: ", backing_tracks)
        # print("Filter: ", which_filter)
        # print("Splitter: ", splitter)
        run_lalal_in_thread(
            input_file=self.input_file,
            stems=stems,
            backing_tracks=backing_tracks,
            which_filter=which_filter,
            splitter=splitter,
        )
        # self.root.quit()


def run_lalal_in_thread(input_file, stems, backing_tracks, which_filter, splitter):
    """Run lalalai extractor in a separate thread so that the GUI doesn't block."""
    print("running lalal in thread")
    t = threading.Thread(
        target=run_trapping_lalal,
        args=(input_file, stems, backing_tracks, which_filter, splitter),
    )
    t.daemon = True
    t.start()
    print("lalal thread started")


def run_trapping_lalal(input_file, stems, backing_tracks, which_filter, splitter):
    """Invoke run_lalalai but trap any exceptions that occur and report them."""
    print("run_trapping_lalal is running in a thread")
    try:
        run_lalal(input_file, stems, backing_tracks, which_filter, splitter)
    except Exception as e:
        print(f"exception in thread: {e}")
        traceback.print_exc()
    print("run_trapping_lalal has finished")


def run_lalal(input_file, stems, backing_tracks, which_filter, splitter):
    # the thread needs its own KeyValueStore object so that it
    # has its own connection to the database as SQLite doesn't
    # allow multiple threads to use the same connection
    thread_store = KeyValueStore(store.db_file)

    api_key = thread_store.get("api_key")

    output_dir = thread_store.get("output_dir")
    os.makedirs(output_dir, exist_ok=True)

    lalalai_splitter.batch_process_multiple_stems(
        api_key,
        input_file,
        output_dir,
        stems,
        backing_tracks,
        which_filter,
        splitter,
    )


class KeyValueStore:
    """A simple key-value store backed by an SQLite database."""

    def __init__(self, db_file):
        """initialize database connection and ensure the table exists"""
        self.db_file = db_file
        self.conn = self.create_connection(db_file)
        self.create_table()

    def create_connection(self, db_file):
        """create a database connection to a SQLite database"""
        conn = sqlite3.connect(db_file)
        return conn

    def create_table(self):
        """create the key-value table if it doesn't exist"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_store (
                key text PRIMARY KEY,
                value text NOT NULL
            );
        """
        )

    def get(self, key):
        """get a value by key, return None if not found"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set(self, key, value):
        """set a value by key, update if already exists"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO kv_store
            (key, value) VALUES (?, ?)
        """,
            (key, value),
        )
        self.conn.commit()


def handle_progress_message(gui, message):
    """Handle a progress message from lalalai_splitter."""
    msg = message.split()
    match msg[0]:
        case "%uploading":
            gui.set_overall_status("Uploading...")
            return
        case "%uploaded":
            gui.set_overall_status("Upload complete.")
            return
        case "%split_start":
            gui.set_stem_status(msg[1], "Splitting requested...")
            gui.set_overall_status("Processing...")
            return
        case "%split_waiting":
            gui.set_stem_status(msg[1], "Waiting for split to start...")
            return
        case "%split_progress":
            gui.set_stem_status(msg[1], f"Splitting: {msg[2]}%")
            return
        case "%download_start":
            gui.set_stem_status(msg[2], f"Downloading {msg[1]}...")
            return
        case "%download_complete":
            gui.set_stem_status(msg[2], f"{msg[1]} downloading complete.")
            return
        case "%split_complete":
            gui.set_stem_status(msg[1], "Split and download complete.")
            return
        case "%unmixing_complete":
            gui.set_overall_status("All Done.")
            return
        case _:
            print(f"unhandled progress message: {message}")


store = KeyValueStore(os.path.expanduser("~/.unmixer.sqlite3"))
