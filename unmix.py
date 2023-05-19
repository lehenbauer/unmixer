import os
import subprocess
import sqlite3
import sys
import threading
import traceback

import lalalai_splitter


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area


class StdoutRedirector(IORedirector):
    def write(self, str):
        self.text_area.insert("end", str)
        self.text_area.see("end")


class StderrRedirector(IORedirector):
    def write(self, str):
        self.text_area.insert("end", str)
        self.text_area.see("end")


def create_console(tk):
    global console_widget

    root = tk.Tk()
    root.title("Unmix Debug Console")
    console_widget = tk.Text(root, wrap="word")
    console_widget.pack(expand=True, fill="both")

    sys.stdout = StdoutRedirector(console_widget)
    sys.stderr = StderrRedirector(console_widget)

    return console_widget

def run_lalal(input_file, stems, backing_tracks, which_filter, splitter):
    api_key = store.get("api_key")

    output_dir = store.get("output_dir")
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
    print('run_trapping_lalal is running in a thread')
    try:
        run_lalal(input_file, stems, backing_tracks, which_filter, splitter)
    except Exception as e:
        print(f'exception in thread: {e}')
        traceback.print_exc()
    print('run_trapping_lalal has finished')

def run_lalal_in_thread(input_file, stems, backing_tracks, which_filter, splitter):
    print('running lalal in thread')
    t = threading.Thread(target=run_trapping_lalal, args=(input_file, stems, backing_tracks, which_filter, splitter))
    t.daemon = True
    t.start()
    print('lalal thread started')


class KeyValueStore:
    def __init__(self, db_file):
        """initialize database connection and ensure the table exists"""
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
