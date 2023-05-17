

import subprocess
import sys

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
    root = tk.Tk()
    root.title("Unmix Debug Console")
    console_output = tk.Text(root, wrap="word")
    console_output.pack(expand=True, fill='both')

    sys.stdout = StdoutRedirector(console_output)
    sys.stderr = StderrRedirector(console_output)

    return console_output


def run_lalal(input_file, stems, backing_tracks, filter, splitter):
        command = ["python",
                   "lalalai_splitter.py",
                   "--input",
                   input_file,
                   "--stems",
                   *stems,
                   "--backingtracks",
                   *backing_tracks,
                   "--filter",
                   str(filter),
                   "--splitter",
                   splitter,
                   "--help"]

        print(command)
        subprocess.run(command)

