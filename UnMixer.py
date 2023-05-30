import os
import sys
import tkinter as tk

import unmix

create_console = True

def on_close():
    sys.exit(0)

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_close)

root.my_gui = unmix.UnmixGUI(root)

if create_console:
    unmix.create_console(tk, root.my_gui)
print("yo baby yo baby yo")
print(f"current dir: {os.getcwd()}")
root.mainloop()
