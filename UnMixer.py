import os
import tkinter as tk

import unmix

create_console = True

root = tk.Tk()
root.my_gui = unmix.UnmixGUI(root)
if create_console:
    unmix.create_console(tk, root.my_gui)
print("yo baby yo baby yo")
print(f"current dir: {os.getcwd()}")
root.mainloop()
