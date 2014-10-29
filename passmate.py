#!/usr/bin/python
import hashlib, Tkinter, math
from Tkinter import _tkinter

with open('diceware8k.txt', 'r') as file:
    WORDS = tuple([i.strip() for i in file.readlines()])

def take(count, generator):
    return [i for ni,i in zip(range(count), generator)]

def deephash(key):
    for i in range(100000):
        key = hashlib.sha256(key).digest()

    return key

def deephash64(key):
    hash = deephash(key)
    return hash.encode('base64')[:-2]

def bytestream(key):
    hash = deephash(key)
    while True:
        hash = hashlib.sha256(hash[:16]).digest()
        bytes = hash[16:]
        for c in bytes:
            yield c

def bitstream(key):
    bytegen = bytestream(key)
    for byte in bytegen:
        n = ord(byte)
        for shift in range(7, -1, -1):
            yield (n >> shift) & 1

def wordstream(key):
    bitgen = bitstream(key)
    while True:
        yield choose(WORDS, bitgen)

def dicephrase(key, wordcount):
    wordgen = wordstream(key)
    words = take(5, wordgen)
    return ' '.join(words)

def choose(p, bitgen):
    power = int(math.ceil((math.log(len(p), 2))))
    bits = take(power, bitgen)
    n = 0
    for bit in bits:
        n = n << 1
        n += bit

    return p[n]

class App(Tkinter.Frame):
    def __init__(self, master, defaultfiles=None):
        Tkinter.Frame.__init__(self, master)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)

        self.idlabel = Tkinter.Label(self, text='ID')
        self.idlabel.grid(row=0, column=0)

        self.identry = Tkinter.Entry(self)
        self.identry.grid(row=0, column=1, sticky='ew')

        self.passlabel1 = Tkinter.Label(self, text='Enter Passphrase')
        self.passlabel1.grid(row=1, column=0)

        self.passentry1 = Tkinter.Entry(self, show = '*', width=50)
        self.passentry1.grid(row=1, column=1, sticky='ew')

        self.passlabel2 = Tkinter.Label(self, text='Repeat Passphrase')
        self.passlabel2.grid(row=2, column=0)

        self.passentry2 = Tkinter.Entry(self, show = '*', width=50)
        self.passentry2.grid(row=2, column=1, sticky='ew')
        self.passentry2.bind('<Key-Return>', self.go)

        self.checktitlelabel = Tkinter.Label(self, text='Checksum:')
        self.checktitlelabel.grid(row=3, column=0)

        self.checksumlabel = Tkinter.Label(self, text='')
        self.checksumlabel.grid(row=3, column=1)

        self.modevar = Tkinter.IntVar(self, value=1)

        self.base64radio = Tkinter.Radiobutton(self, text='Base 64', variable=self.modevar, value=1)
        self.base64radio.grid(row=4, column=0)

        self.diceradio = Tkinter.Radiobutton(self, text='Diceware', variable=self.modevar, value=2)
        self.diceradio.grid(row=4, column=1)

        self.lengthlabel = Tkinter.Label(self, text='Max Length')
        self.lengthlabel.grid(row=5, column=0)

        self.lengthvar = Tkinter.IntVar(self, value=32)
        self.lengthentry = Tkinter.Entry(self, textvariable=self.lengthvar)
        self.lengthvar.set(50)
        self.lengthentry.grid(row=5, column=1, sticky='ew')
        self.lengthentry.bind('<Key-Return>', self.go)

        self.gobutton = Tkinter.Button(self, text='Go', command=self.go)
        self.gobutton.grid(row=6, column=0)

        self.resultvar = Tkinter.StringVar()
        self.resultentry = Tkinter.Entry(self, textvariable=self.resultvar, width=50)
        self.resultentry.grid(row=6, column=1, sticky='ew')

        self.savebutton = Tkinter.Button(self, text='Save Params', command=self.save_parameters)
        self.savebutton.grid(row=7, column=0)

    def go(self, event=None):
        pass1 = self.passentry1.get()
        pass2 = self.passentry2.get()
        if pass1 != pass2:
            result = "Passphrases don't match"
            checksum = result
        else:
            checksum = deephash64(pass1)[:8]
            id = self.identry.get()
            fullpass = id + pass1
            mode = self.modevar.get()
            if mode == 0:
                result = ''
            elif mode == 1:
                result = deephash64(fullpass)
            elif mode == 2:
                result = dicephrase(fullpass, 5)

        try:
            length = int(self.lengthvar.get())
        except ValueError:
            pass
        else:
            result = result[:length]

        self.checksumlabel['text'] = checksum
        self.resultvar.set(result)
        self.resultentry.focus_set()
        self.resultentry.selection_range(0, 'end')

    def save_parameters(self):
        id = self.identry.get()
        mode = str(self.modevar.get())
        length = str(self.lengthvar.get())
        string = ', '.join((id, mode, length))+'\n'
        with open('pass_parameters.txt', 'a') as file:
            file.write(string)

    def close_window(self):
        try:
            clipboard = self.selection_get(selection='CLIPBOARD')
        except _tkinter.TclError:
            clipboard = ''

        if clipboard and clipboard in self.resultvar.get():
            self.clipboard_clear()

        self.quit()


def main():
    rt = Tkinter.Tk()
    rt.title('Passmate')
    rt.grid_rowconfigure(0, weight = 1)
    rt.grid_columnconfigure(0, weight = 1)
    ui = App(rt)
    ui.grid(row = 0, column = 0, sticky = 'nsew')
    rt.protocol('WM_DELETE_WINDOW', ui.close_window)
    ui.mainloop()

if __name__ == '__main__':
    main()
