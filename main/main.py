# -*- coding: utf-8 -*-
# 2020/11 by Sryml

from tkinter import *
from tkinter.messagebox import showinfo
from tkinter import colorchooser

import tkinter.font as tkFont
import struct
import os

# pip
import windnd


def ByteToHex(bins):
    return ''.join(["%02X" % x for x in bins])


def HexToByte(hexStr):
    return bytes.fromhex(hexStr)


def DefArgWrapper(Function, *args):
    def wrapper(func=Function, args=args):
        return func(*args)

    return wrapper


def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):

    points = [
        x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2,
        y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
        x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius,
        y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1,
        y1 + radius, x1, y1
    ]

    return canvas.create_polygon(points, **kwargs, smooth=True)


# round_rectangle(canvas, 50, 50, 150, 100, radius=20, fill="#F0F0F0",outline="#a0a0a0")


####
class GUI:
    def __init__(self, window):
        self.win = window
        self.widget_data = {}

        self.font_1 = tkFont.Font(font="TkDefaultFont")
        # {'family': 'Microsoft YaHei UI', 'size': 9, 'weight': 'normal', 'slant': 'roman', 'underline': 0, 'overstrike': 0}
        self.font_1.config(size=-17)
        self.font_2 = tkFont.Font(font="TkDefaultFont")
        self.font_2.config(size=-12, slant=tkFont.ITALIC)
        self.font_3 = tkFont.Font(font="TkDefaultFont")
        self.font_3.config(size=-15)

        self.title = "BW editor"
        self.version = 'v0.1'
        self.size = 350, 270

        sw = window.winfo_screenwidth()
        sh = window.winfo_screenheight()
        x = (sw - self.size[0]) / 2
        y = (sh - self.size[1]) / 2
        window.title(self.title)
        window.iconbitmap("./bw.ico")
        window.geometry("{}x{}+{:.0f}+{:.0f}".format(self.size[0],
                                                     self.size[1], x, y))
        window.resizable(width=False, height=False)

        window.attributes("-topmost", True)
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(0, weight=1)

        #
        self.start = start = Button(window,
                                    text="Drag to open the bw file",
                                    relief=GROOVE,
                                    font=self.font_1)
        start["state"] = DISABLED
        start.place(relx=0.5, rely=0.5, anchor=CENTER)
        # window.update_idletasks()
        # start.place(
        # x=(self.size[0] - start.winfo_width()) / 2,
        # y=(self.size[1] - start.winfo_height()) / 2)

        #
        self.main_frame = main_frame = Frame(window,
                                             width=self.size[0],
                                             height=self.size[1])
        # main_frame.grid()
        main_frame.grid_propagate(0)
        main_frame.grid_columnconfigure(0, weight=1)
        # main_frame.grid_columnconfigure(1, weight=1)
        # main_frame.grid_rowconfigure(0, weight=1)
        # main_frame.grid_rowconfigure(1, weight=1)

        #
        h = 30
        self.frame_1 = frame_1 = Frame(main_frame,
                                       width=self.size[0],
                                       height=h)
        self.frame_2 = frame_2 = LabelFrame(main_frame,
                                            text="Atmospheres: 0",
                                            fg="#808080",
                                            labelanchor=SW,
                                            width=self.size[0],
                                            height=self.size[1] - h - 60,
                                            bd=2,
                                            relief=GROOVE)
        self.apply = apply = Button(main_frame,
                                    width=30,
                                    text="Apply",
                                    font=self.font_3,
                                    takefocus=False,
                                    state=DISABLED,
                                    bg="#E6E6E6",
                                    disabledforeground="#B4B4B4",
                                    relief=GROOVE,
                                    command=self.applyCMD)

        self.canvas = canvas = Canvas(frame_2, highlightthickness=0)
        self.sbar = sbar = Scrollbar(frame_2)

        frame_1.grid_propagate(0)
        frame_2.grid_propagate(0)

        frame_1.grid_columnconfigure(0, weight=1)
        frame_1.grid_columnconfigure(2, weight=1)
        frame_2.grid_rowconfigure(0, weight=1)
        frame_2.grid_columnconfigure(0, weight=1)

        frame_1.grid(row=0, column=0)
        frame_2.grid(row=1, column=0, padx=15)
        apply.grid(row=2, pady=8)

        canvas.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        sbar.grid(row=0, column=1, sticky=NS)

        sbar.config(command=canvas.yview)
        canvas.config(yscrollcommand=sbar.set)

        window.update_idletasks()
        self.frame_in_canvas = frame_in_canvas = Frame(
            canvas,
            bd=0,
            width=self.size[0],
            height=frame_2.winfo_height(),
            relief=GROOVE)
        canvas.create_window((-20, 1), anchor=NW, window=frame_in_canvas)

        # frame_in_canvas.grid_propagate(0)
        frame_in_canvas.grid_columnconfigure(0, weight=1, pad=79)
        frame_in_canvas.grid_columnconfigure(1, weight=1, pad=13)
        frame_in_canvas.grid_columnconfigure(2, weight=1, pad=79)

        frame_in_canvas.bind("<MouseWheel>", self.processWheel)
        frame_in_canvas.bind("<ButtonPress-1>", self.focus_set)
        canvas.bind("<ButtonPress-1>", self.focus_set)
        # frame_in_canvas.bind("<B1-Motion>", self.scroll_move)

        self.line_1 = line_1 = Frame(frame_1,
                                     width=self.size[0],
                                     height=2,
                                     bd=2,
                                     relief=SUNKEN)
        # line_1.pack(fill=X, padx=5, pady=5)
        line_1.grid(row=0, columnspan=3, padx=15)

        text = ("name", "color", "density")
        for i in range(3):
            frame = Frame(frame_1, height=26, width=47, bd=0, relief=GROOVE)
            if i == 2:
                frame['width'] = 49
            label = Label(
                frame,
                text=text[i],
                fg="#747474",
                # fg="#%02X%02X%02X" % (116, 116, 116),
                font=self.font_2)
            frame.pack_propagate(0)
            frame.grid(row=0, column=i)
            label.pack(fill=BOTH, expand=1)

        #
        menubar = Menu(window)
        # filemenu = Menu(menubar, tearoff=0)
        # menubar.add_cascade(label="About", menu=filemenu, command=self.foo)
        menubar.add_command(label="About", command=self.about)
        window.config(menu=menubar)

        self.validateCMD = window.register(self.validate_fn)

        windnd.hook_dropfiles(window,
                              func=self.dragged_files,
                              force_unicode=True)

    def about(self):
        showinfo(self.title,
                 "%s %s\n\n2020-11\nby sryml" % (self.title, self.version))

    def focus_set(self, event):
        event.widget.focus_set()

    def scroll_start(self, event):
        self.canvas.scan_mark(20, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(20, event.y, gain=1)

    def processWheel(self, event):
        delta = event.delta
        b = self.sbar.get()
        if (delta > 0 and b[0] != 0) or (delta < 0 and b[1] != 1):
            self.canvas.yview_scroll(-event.delta // 30, UNITS)
            # self.canvas.scan_dragto(0, event.delta, gain=1)

    def applyCMD(self):
        widget_data = self.widget_data

        with open(self.file_path, 'rb+') as f:
            for id_ in range(widget_data['maxAtmospheres']):
                widget = widget_data[id_]
                pos = widget['pos']

                color = widget['color']
                if color['val_o'] != color['val_n']:
                    byte = struct.pack('<3B', *color['val_n'])
                    f.seek(pos)
                    f.write(byte)
                    color['val_o'] = color['val_n']

                fog = widget['fog']
                val_n = float(fog['widget'].get())
                if fog['val_o'] != val_n:
                    byte = struct.pack('<f', val_n)
                    f.seek(pos + 3)
                    f.write(byte)
                    fog['val_o'] = val_n

        self.apply['state'] = DISABLED
        self.win.focus_set()

    def dragged_files(self, files):
        file_ = files[0]
        file_name = os.path.split(file_)[1]
        ext = os.path.splitext(file_)[1]
        if ext.lower() != ".bw":
            return

        h = 26
        w = (80, h, 64)
        pady = 9
        widget_data = self.widget_data
        P = 5

        with open(file_, 'rb') as f:
            maximum = struct.unpack('<I', f.read(4))[0]
            for i in range(maximum):
                if i not in widget_data:
                    frames = []
                    for n in range(3):
                        frame = Frame(self.frame_in_canvas,
                                      width=w[n],
                                      height=h,
                                      bd=0,
                                      relief=GROOVE)
                        frame.pack_propagate(0)
                        frame.grid(row=i, column=n, pady=pady)
                        frames.append(frame)

                    e1 = Entry(frames[0], takefocus=False)
                    e1.pack(fill=BOTH, expand=1)

                    frames[1]['bd'] = 2
                    b1 = Button(frames[1], relief=GROOVE, takefocus=False)
                    b1['command'] = DefArgWrapper(self.colorchooser, b1, i)
                    b1.pack(fill=BOTH, expand=1)

                    e2 = Entry(
                        frames[2],
                        bd=2,
                        highlightthickness=0,
                        #    validate='all',
                        validatecommand=(self.validateCMD, '%P', '%V', '%W'),
                        takefocus=False)
                    e2.pack(fill=BOTH, expand=1)

                    widget_data[i] = {
                        'parent': frames,
                        'name': {
                            'widget': e1
                        },
                        'color': {
                            'widget': b1,
                            'val_o': (),
                            'val_n': ()
                        },
                        'fog': {
                            'widget': e2,
                            'val_o': 0.0
                        },
                        # 'pos': 0,
                    }

                name_len = struct.unpack('<I', f.read(4))[0]
                name = f.read(name_len).decode('utf8')
                pos = f.tell()
                r, g, b, fog = struct.unpack('<3Bf', f.read(7))
                fog = round(fog, P)

                widget = widget_data[i]
                widget['pos'] = pos

                widget['name']['widget']['state'] = NORMAL
                widget['name']['widget'].delete(0, END)
                widget['name']['widget'].insert(0, name)
                widget['name']['widget']['state'] = 'readonly'

                widget['color']['widget']['bg'] = "#%02X%02X%02X" % (r, g, b)
                widget['color']['val_o'] = (r, g, b)
                widget['color']['val_n'] = (r, g, b)

                widget['fog']['widget']['validate'] = 'none'
                widget['fog']['widget'].delete(0, END)
                widget['fog']['widget'].insert(0, fog)
                widget['fog']['widget']['validate'] = 'all'
                widget['fog']['val_o'] = fog

                for i in widget['parent']:
                    i.grid()

        widget_data['maxAtmospheres'] = maximum
        for n in range(maximum, len(widget_data) - 1):
            for i in widget_data[n]['parent']:
                i.grid_remove()

        self.main_frame.grid()
        self.win.update_idletasks()
        self.canvas['scrollregion'] = (0, 0, 0,
                                       self.frame_in_canvas.winfo_height())
        self.win.focus_force()
        self.win.update()
        # self.win.update_idletasks()

        self.win.title('{} - {}'.format(self.title, file_name))
        self.frame_2['text'] = "Atmospheres: %d" % maximum
        self.apply['state'] = DISABLED

        self.file_path = file_

    def validate_fn(self, content, mode, widget_name):
        if ' ' in content:
            return False

        widget = self.win.nametowidget(widget_name)
        if not content:
            if mode == "focusout":
                widget['validate'] = 'none'
                widget.insert(0, "0")
                widget['validate'] = 'all'
                self.apply['state'] = NORMAL
            return True

        try:
            float(content)
            if mode == "key":
                self.apply['state'] = NORMAL
        except:
            return False

        if '.' in content and len(content.split('.')[1]) > 5:
            return False
        return True

    def colorchooser(self, button, id_):
        c = colorchooser.askcolor(button['bg'])
        if c[1]:
            button['bg'] = c[1]
            self.widget_data[id_]['color']['val_n'] = tuple(
                [int(i) for i in c[0]])
            self.apply['state'] = NORMAL
        self.win.focus_set()


# def main():
root = Tk()
gui = GUI(root)
root.mainloop()

# main()

