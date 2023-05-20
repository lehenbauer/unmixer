import os
import queue
import sqlite3
import subprocess
import sys
import threading
import traceback

import lalalai_splitter

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


def create_console(tk):
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
    root.after(100, check_output_queue)

    return console_widget


def check_output_queue():
    # Check if there's something in the queue
    while not output_queue.empty():
        # If there is, write it to the text widget
        message = output_queue.get()
        if message.startswith('%'):
            handle_progress_message(message)
        console_widget.insert("end", message)
        console_widget.see("end")

    # Schedule the next call to this function
    console_widget.after(100, check_output_queue)


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


def run_trapping_lalal(input_file, stems, backing_tracks, which_filter, splitter):
    """Invoke run_lalalai but trap any exceptions that occur and report them."""
    print("run_trapping_lalal is running in a thread")
    try:
        run_lalal(input_file, stems, backing_tracks, which_filter, splitter)
    except Exception as e:
        print(f"exception in thread: {e}")
        traceback.print_exc()
    print("run_trapping_lalal has finished")


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


store = KeyValueStore(os.path.expanduser("~/.unmixer.sqlite3"))
