

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
    console_output.grid(row=0, column=0)

    sys.stdout = StdoutRedirector(console_output)
    sys.stderr = StderrRedirector(console_output)

    return console_output


