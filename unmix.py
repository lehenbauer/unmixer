

import queue
import subprocess
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
        command = ["python",
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
            command.extend(*stems)

        if backing_tracks:
            command.append("--backing-tracks")
            command.extend(*backing_tracks)

        print(command)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        read_subprocess_output(proc, console_widget)

