

import queue
import subprocess
import sqlite3
import sys
import threading

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
    console_widget.pack(expand=True, fill='both')

    sys.stdout = StdoutRedirector(console_widget)
    sys.stderr = StderrRedirector(console_widget)

    return console_widget


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line.decode('utf-8'))
    out.close()

def read_subprocess_output(proc, console_widget):
    q = queue.Queue()
    t = threading.Thread(target=enqueue_output, args=(proc.stdout, q))
    t.daemon = True
    t.start()

    # Now we need to check the queue periodically and update the text widget
    def check_queue():
        while not q.empty():
            line = q.get_nowait()
            console_widget.insert('end', line)
        console_widget.after(100, check_queue)  # Check again after 100ms

    console_widget.after(100, check_queue)

def run_lalal(input_file, stems, backing_tracks, filter, splitter):
        command = [sys.executable,
                   "lalalai_splitter.py",
                   "--input",
                   input_file,
                   "--filter",
                   str(filter),
                   "--splitter",
                   splitter,
                   "--help"]

        if stems:
            command.append("--stems")
            command.extend(stems)

        if backing_tracks:
            command.append("--backing-tracks")
            command.extend(backing_tracks)

        print(command)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        read_subprocess_output(proc, console_widget)

class KeyValueStore:
    def __init__(self, db_file):
        """ initialize database connection and ensure the table exists """
        self.conn = self.create_connection(db_file)
        self.create_table()

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        conn = sqlite3.connect(db_file)
        return conn

    def create_table(self):
        """ create the key-value table if it doesn't exist """
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key text PRIMARY KEY,
                value text NOT NULL
            );
        """)

    def get(self, key):
        """ get a value by key, return None if not found """
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set(self, key, value):
        """ set a value by key, update if already exists """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO kv_store
            (key, value) VALUES (?, ?)
        """, (key, value))
        self.conn.commit()

