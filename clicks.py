from tkinter import *
from tkinter import messagebox
from keyboard import *
from pymouse import *
from multiprocessing import *
from time import sleep

MODULE = [(LEFT, "Start click left by this key"),
          (RIGHT, "Start click right by this key")]
SIDE2MOUSE = {LEFT: 1, RIGHT: 2}
root = Tk()
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
WINDOW_WIDTH = screenwidth // 3
WINDOW_HEIGHT = screenheight // 2
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.title("Quick Clicker")
global_mouse = PyMouse()


def click_mouse(ms):
    global_mouse.press(*global_mouse.position(), ms)


class Presser:
    def __init__(self):
        self.running = False
        self.ps = Process()

    def is_running(self):
        return self.running

    def run(self, key, mouse, interval=0.0, long_press=True):
        if self.running:
            self.stop()
        try:
            is_pressed(key)
        except ValueError:
            raise
        self.running = True
        self.ps = Process(target=self.do_press, args=(key, mouse, interval, long_press))
        self.ps.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.ps.terminate()

    def do_press(self, key, mouse, interval, long_press):
        if long_press:
            while True:
                if is_pressed(key):
                    click_mouse(mouse)
                    sleep(interval)
        else:
            while True:
                wait(key)
                while is_pressed(key):
                    click_mouse(mouse)
                    sleep(interval)

    def __del__(self):
        self.stop()


class Side:
    def __init__(self, side, text, button_text=("start", "stop"), font=("Arial", 20)):
        self.frame = Frame(root)
        self.running_tip = Label(self.frame, text="", font=font, fg='red')
        self.running_tip.pack()
        self.base_text_obj = Label(self.frame, text=text, font=font)
        self.base_text_obj.pack()
        self.key_entry_obj = Entry(self.frame)
        self.key_entry_obj.pack()
        self.cps_text_obj = Label(self.frame, text="CPS:", font=font)
        self.cps_text_obj.pack()
        self.cps_entry_obj = Entry(self.frame)
        self.cps_entry_obj.pack()
        self.stop_btn_obj = Button(self.frame, text=button_text[1], font=font, command=self.handle_button_stop)
        self.stop_btn_obj.pack(side=BOTTOM)
        self.start_btn_obj = Button(self.frame, text=button_text[0], font=font, command=self.handle_button_start)
        self.start_btn_obj.pack(side=BOTTOM)
        self.SIDE = side
        self.presser = Presser()

    def pack(self):
        self.frame.pack(side=self.SIDE)

    def handle_button_start(self):
        cps_msg = self.cps_entry_obj.get().strip()
        try:
            int(cps_msg)
        except ValueError:
            messagebox.showerror("Not a number", f"{cps_msg} is not a number; please input an integer")
            return
        cps = int(cps_msg)
        if cps <= 0:
            messagebox.showerror("Zero", f"Must bigger than 0")
            return
        input_msg = self.key_entry_obj.get().strip()
        try:
            self.presser.run(input_msg, SIDE2MOUSE[self.SIDE], 1/cps)
        except ValueError:
            if input_msg:
                messagebox.showerror("Invalid key", f"`{input_msg}` is not a valid key")
            else:
                messagebox.showerror("Empty input", f"Cannot use empty key")
            return
        self.running_tip["text"] = f"Running {input_msg}"
        root.update()

    def handle_button_stop(self):
        if not self.presser.is_running():
            messagebox.showerror("Program not start", "Please start it first")
            return
        self.running_tip["text"] = ""
        root.update()
        self.presser.stop()


def fix_scaling(rt):
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    root.tk.call('tk', 'scaling', scaleFactor / 75)


def main():
    sides = [Side(*par) for par in MODULE]
    for sd in sides: sd.pack()
    fix_scaling(root)
    root.mainloop()


if __name__ == '__main__':
    main()
