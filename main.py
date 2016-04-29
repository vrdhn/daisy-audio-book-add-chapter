
##
## daisy-tools  (C) Vardhan Varma <vardhanvarma@gmail.com>
##  LICENSE:  GPL3
##

import sys
import os
from Tkinter import *
import tkFileDialog
import tkFont
#from ttk import *
import json
import traceback

import time

from convert import convert

config_file = os.path.abspath(os.path.expanduser("~/.daisytool.json"))
outlog_file = os.path.abspath(os.path.expanduser("~/daisytool.log"))


    
path_prefix = sys._MEIPASS if getattr(sys, 'frozen', False) else "."


msg1 = """Welcome to Daisy Book Tool.\n
This tool adds a notice after first section"""


class Application(Frame):
    def __init__(self, master = None):
        self.logfile = open(outlog_file,"w")
        Frame.__init__(self,master)

        self.createWidgets()
        self.grid()
        self.log("Session starting " , time.asctime())
        self.log("Logfile saved at ", outlog_file)

        

    def createWidgets(self):
        ####
        try:
            self.config = json.load(open(config_file))
        except:
            self.config = json.loads('{ "lru": [] }')
        self.inputVar = StringVar()
        self.outputVar = StringVar()
        self.noticeVar = StringVar()
        self.durnVar = DoubleVar()
        if len(self.config["lru"]) > 0 :
            lru = self.config["lru"]
            self.inputVar.set(lru[0]["input"])
            self.outputVar.set(lru[0]["output"])
            self.noticeVar.set(lru[0]["notice"])
            self.durnVar.set(lru[0]["duration"])

                                   
            
        ####
        r = 0
        self.msg = Message(self, text = msg1,width=300)
        self.msg.grid(row=r,column=0,columnspan=5,sticky=W,pady=10)
        ####
        r  = r +  1
        self.inputLabel = Label(self, text = "Input Folder")
        self.inputEntry = Entry(self,width=80,textvariable=self.inputVar)
        self.inputButton = Button(self, text = "Select",command=self.btnInput)
        self.inputLabel.grid(row=r,column=0,sticky=E,pady=2)
        self.inputEntry.grid(row=r,column=1,columnspan=3,padx=3)
        self.inputButton.grid(row=r,column=4)
        #####
        r = r + 1        
        self.outputLabel = Label(self, text = "Output Folder")
        self.outputEntry = Entry(self,width=80,textvariable=self.outputVar)
        self.outputButton = Button(self, text = "Select",command=self.btnOutput)
        self.outputLabel.grid(row=r,column=0,padx=3,sticky=E,pady=2)
        self.outputEntry.grid(row=r,column=1,columnspan=3,padx=3)
        self.outputButton.grid(row=r,column=4,padx=3)
        #####
        r = r + 1        
        self.noticeLabel = Label(self, text = "Notice File")
        self.noticeEntry = Entry(self,width=80,textvariable=self.noticeVar)
        self.noticeButton = Button(self, text = "Select",command=self.btnNotice)
        self.noticeLabel.grid(row=r,column=0,padx=3,sticky=E,pady=2)
        self.noticeEntry.grid(row=r,column=1,columnspan=3,padx=3)
        self.noticeButton.grid(row=r,column=4,padx=3)
        #####
        r = r + 1        
        self.durnLabel = Label(self, text = "Duration ( seconds) ")
        self.durnEntry = Entry(self,width=10,textvariable=self.durnVar)
        self.durnLabel.grid(row=r,column=0,padx=3,sticky=E,pady=2)
        self.durnEntry.grid(row=r,column=1,padx=3,sticky=W)
        #####
        r  = r + 1
        self.startButton = Button(self,text='Start',command=self.start)
        self.startButton.grid(row=r,column=0,pady=20)
        #####
        r  = r + 1
        self.showOutput = Label(self,text="Output...")
        self.showOutput.grid(row=r,column=0,sticky=W,columnspan=3,padx=3)
        #####
        r  = r + 1
        self.showOutput = Text(self,width=80)
        self.showOutput.grid(row=r,column=0,columnspan=5,padx=3,pady=3)
        #####
        r  = r + 1
        self.quitButton = Button(self,text='Quit',command=self.quit)
        self.quitButton.grid(row=r,column=4,pady=20)

    def btnInput(self):
        x = tkFileDialog.askdirectory(
            mustexist = True,
            title = "Select Input Folder",
            initialdir = self.inputVar.get())
        if x:
            self.inputVar.set(x)

    def btnOutput(self):
        x = tkFileDialog.askdirectory(
            mustexist = True,
            title = "Select Output  Folder",
            initialdir = self.outputVar.get())
        if x:
            self.outputVar.set(x)

    def btnNotice(self):
        x = tkFileDialog.askopenfilename(
            title = "Select Notice File",
            filetypes = [('MP3 files', '.mp3')],
            initialdir = self.noticeVar.get())
        if x:
            self.noticeVar.set(x)

    def log(self,*x):
        o = self.showOutput
        o.config(state=NORMAL)
        res = ' '.join([str(y) for y in x])+'\n'
        o.insert(END,res)
        o.config(state="disable")
        self.logfile.write(res)
        self.logfile.flush()

    def start(self):
        o = self.log
        iv = self.inputVar.get()
        ov = self.outputVar.get()
        nv = self.noticeVar.get()
        dv = self.durnVar.get()        

        o("Settings:")
        o("  Input Directory  : ",iv)
        o("  Output Directory : ",ov)
        o("  Notice MP3 File  : ",nv)
        o("  Notice Duration  : ",dv)        
        try:
            ok = convert( input_dir = iv,
                          output_dir = ov,
                          notice_file = nv,
                          notice_durn = dv,
                          logfn = o)
            if ok :
                ## Save before exiting..
                self.config["lru"].insert(0,{ "input":    iv,
                                              "output":   ov,
                                              "notice":   nv,
                                              "duration": dv})
                with open(config_file, 'w') as outfile:
                    json.dump(self.config, outfile)
        except:
            o("**********************************************************")
            o(" AN INTERNAL ERROR HAS OCCURED ")
            o(" Please send content of this buffer to fix this issue")
            o(" Visit http://github.com/vrdhn/daisy-tool to submit issue")
            o(" Or email author at vardhanvarma@gmail.com with the file")
            o(" Logfile is saved at", outlog_file)
            o("**********************************************************")
            o(traceback.format_exc())
            o("**********************************************************")
        

        
root = Tk()

#default_font = tkFont.nametofont("TkDefaultFont")
#default_font.configure(size=16)

try:
    root.iconbitmap( os.path.abspath(os.path.join(path_prefix,'daisy.ico')))
except:
    pass

app = Application(master=root)
app.master.title("Daisy Audio Book Tools")
root.mainloop()
