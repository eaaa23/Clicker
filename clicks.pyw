## Clicker, author: @eason, github: eaaa23
## No license. Everyone can use it in any way.
## Just a tool while playing minecraft, and I'm afraid of the virus inside some `autoclicker` on the internet.

from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
from keyboard import is_pressed, wait
from pymouse import PyMouse
from multiprocessing import Process
from time import sleep
import os
import ctypes
import json

MODULE = [(LEFT, "Start click left by this key"),
          (RIGHT, "Start click right by this key")]
SIDE2MOUSE = {LEFT: 1, RIGHT: 2}
root = Tk()
if os.name == 'nt':
    from win32 import win32api, win32gui, win32print
    import win32con
    print("Debug: windows")
    hDC = win32gui.GetDC(0)
    screenwidth = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    screenheight = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
else:
    print("Debug: not windows")
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()

with open("conf.json") as fp:
    struct = json.load(fp)
    WINDOW_WIDTH = int(screenwidth * struct["WindowWidthRate"])
    WINDOW_HEIGHT = int(screenheight * struct["WindowHeightRate"])
    font_struct = struct["font"]
    DF_FONT = font_struct["DefaultFont"]
    FONT_SIZE = int(WINDOW_WIDTH * (font_struct["FontSizeRate"]))
    COMBOBOX_FONT_RATE = font_struct["ComboboxFontRate"]
    click_struct = struct["click"]
    CPS_MIN = click_struct["CPSMin"]
    CPS_MAX = click_struct["CPSMax"]
    CPS_INTERVAL = click_struct["CPSInterval"]
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.title("Quick Clicker")
global_mouse = PyMouse()

MAX_FN = 12
KEYS = []
KEYS.extend([f"F{i}" for i in range(1, MAX_FN+1)])
KEYS.extend([chr(i) for i in range(ord("A"), ord("A")+26)])
KEYS.extend(r"-=[]\;',./")
KEYS.extend(['tab', 'caps lock', 'shift', 'ctrl', 'alt', 'backspace'])
KEYS.extend(['left', 'right', 'up', 'down'])
if os.name == 'nt':
    KEYS.append('win')


def click_mouse(ms):
    global_mouse.click(*global_mouse.position(), ms)


class Presser:
    def __init__(self):
        self.running = False
        self.ps = Process()

    def is_running(self):
        return self.running

    def run(self, key, mouse, interval=0.0, long_press=True, limitless=False, priority=None):
        print(f"Debug: Call run() with {long_press=}")
        if self.running:
            self.stop()
        try:
            is_pressed(key)
        except ValueError:
            raise
        self.running = True
        self.ps = Process(target=self.do_press, args=(key, mouse, interval, long_press, limitless))
        self.ps.start()
        if priority:
            set_process_priority(self.ps.pid, priority-1)  # input priority is between 1-5 and we need to change it into 0-4

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.ps.terminate()

    def do_press(self, key, mouse, interval, long_press, limitless=False):
        if long_press:
            while True:
                wait(key)
                if limitless:
                    while is_pressed(key):
                        click_mouse(mouse)
                else:
                    while is_pressed(key):
                        click_mouse(mouse)
                        sleep(interval)
        else:
            while True:
                wait(key)
                if limitless:
                    while is_pressed(key): click_mouse(mouse)
                    while not is_pressed(key): click_mouse(mouse)
                else:
                    while is_pressed(key):
                        click_mouse(mouse)
                        sleep(interval)
                    while not is_pressed(key):
                        click_mouse(mouse)
                        sleep(interval)
                # next time press
                while is_pressed(key):
                    sleep(0.1)

    def __del__(self):
        self.stop()


class Side:
    def __init__(self, side, text, button_text=("start", "stop"), font=("Arial", FONT_SIZE)):
        combobox_font = list(font)
        combobox_font[1] = int(combobox_font[1] * COMBOBOX_FONT_RATE)
        combobox_font = tuple(combobox_font)
        self.frame = Frame(root)
        self.running_tip = Label(self.frame, text="\n\n", font=font, fg='red')
        self.running_tip.pack()
        
        self.base_text_obj = Label(self.frame, text=text, font=font)
        self.base_text_obj.pack()
        
        self.key_choose_obj = Combobox(self.frame, value=KEYS, font=combobox_font)
        self.key_choose_obj.pack()
        
        self.cps_text_obj = Label(self.frame, text="CPS:", font=font)
        self.cps_text_obj.pack()

        self.cps = IntVar()
        self.cps_scale_obj = Scale(self.frame, from_=CPS_MIN, to=CPS_MAX, resolution=CPS_INTERVAL, orient=HORIZONTAL,
                                   font=combobox_font, variable=self.cps)
        self.cps_scale_obj.pack()

        self.cps_text_obj = Label(self.frame, text="Priority:", font=font)
        self.cps_text_obj.pack()
        
        self.priority = IntVar()
        self.priority_scale_obj = Scale(self.frame, from_=1, to=5, resolution=1, orient=HORIZONTAL,
                                        font=combobox_font, variable=self.priority)
        self.priority_scale_obj.pack()
        
        self.mod = BooleanVar()
        self.changemod_obj = Checkbutton(self.frame, text="Long press to click", variable=self.mod,
                                         font=combobox_font,
                                         onvalue=True, offvalue=False)
        self.changemod_obj.pack(side=BOTTOM)
        
        self.do_inf = BooleanVar()
        self.change_do_inf_obj = Checkbutton(self.frame, text="Ignore CPS setting and make best", variable=self.do_inf,
                                             font=combobox_font,
                                             onvalue=True, offvalue=False)
        self.change_do_inf_obj.pack(side=BOTTOM)
        
        self.stop_btn_obj = Button(self.frame, text=button_text[1], font=font, command=self.handle_button_stop)
        self.stop_btn_obj.pack(side=BOTTOM)
        
        self.start_btn_obj = Button(self.frame, text=button_text[0], font=font, command=self.handle_button_start)
        self.start_btn_obj.pack(side=BOTTOM)
        
        self.SIDE = side
        self.presser = Presser()

    def pack(self):
        self.frame.pack(side=self.SIDE)

    def handle_button_start(self):
        cps = self.cps_scale_obj.get()
        input_msg = self.key_choose_obj.get().strip()
        do_inf = self.do_inf.get()
        mod = self.mod.get()
        priority = self.priority.get()
        try:
            self.presser.run(input_msg, SIDE2MOUSE[self.SIDE], 1/cps, mod, do_inf, priority)
        except ValueError:
            self.running_tip["text"] = "\n"
            if input_msg:
                messagebox.showerror("Invalid key", f"`{input_msg}` is not a valid key")
            else:
                messagebox.showerror("Empty input", f"Cannot use empty key")
            return
        self.running_tip["text"] = f"Running key {input_msg} ({'inf' if do_inf else cps} CPS)\n"+\
                                   ("[Long press]" if mod else "[Click to start or stop]")+\
                                   f"\nPriority={priority}"
        root.update()

    def handle_button_stop(self):
        if not self.presser.is_running():
            messagebox.showerror("Program not start", "Please start it first")
            return
        self.running_tip["text"] = "\n"
        root.update()
        self.presser.stop()


def fix_scaling():
    if os.name == 'nt':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        root.tk.call('tk', 'scaling', scaleFactor / 75)


def set_process_priority(pid, priority):
    """set_process_priority(pid, priority)
    For Windows: Set The Priority of a Windows Process.  Priority is a value between 0-5 where
    2 is normal priority, higher value means higher priority.
    For UNIX:    Set The Priority of a UNIX Process. Priority is a value between 0-5 which will
    be translated to 19~-20, higher value means higher priority."""
    if os.name == 'nt':
        import win32api,win32process,win32con
        priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                           win32process.BELOW_NORMAL_PRIORITY_CLASS,
                           win32process.NORMAL_PRIORITY_CLASS,
                           win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                           win32process.HIGH_PRIORITY_CLASS,
                           win32process.REALTIME_PRIORITY_CLASS]
        if pid == None:
            pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, priorityclasses[priority])
    else:
        messagebox.showerror("Not Implemented", "Sorry. Changing priority only supports Windows system.")
        


def main():
    sides = [Side(*par) for par in MODULE]
    for sd in sides: sd.pack()
    fix_scaling()
    root.mainloop()


if __name__ == '__main__':
    main()
