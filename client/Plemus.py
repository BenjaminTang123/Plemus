from network import Network
import pickle
import json

from tkinter import *
from mutagen.mp3 import MP3 # pip install mutagen
import pygame # pip install pygame
from PIL import Image, ImageTk # pip install pillow

import asyncio

import os

class Windows:
    def __init__(self) -> None:
        self.root = Tk()

        self.tk_image = self.openImage("./resource/favicon.png")
        
        self.mainFrame = Frame(self.root)

        self.playFrame = Frame(self.mainFrame)
        self.coverLabel = Label(
            self.playFrame, width=310, height=310, 
            borderwidth=3, relief="groove", 
            image=self.tk_image
        )
        self.titileLabel = Label(self.playFrame, text="No songs available", font=("Microsoft Yahei", 20))
        self.authorLabel = Label(self.playFrame, text="Unknown artist")

        self.settingFrame = Frame(self.mainFrame)

        self.playListFrame = Frame(self.settingFrame)
        self.listScrollbar = Scrollbar(self.playListFrame, orient="vertical", command=self.ScrollCommand)
        self.musicList = Listbox(self.playListFrame, height=19, width=25, yscrollcommand=self.listScrollbar.set)
        self.authorList = Listbox(self.playListFrame, height=19, width=25, yscrollcommand=self.listScrollbar.set)

        self.loopPlaybackButton = Button(self.settingFrame, text="Single loop playback", command=self.loopPlayback)
        self.playOrStopButton = Button(self.settingFrame, text="Play", command=self.stopOrPlay)
        self.valumeScale = Scale(self.settingFrame, from_=0, to=10, orient=HORIZONTAL)

        self.timeFrame = Frame(self.root)
        self.nowTimeLabel = Label(self.timeFrame, text="00:00")
        self.timeScale = Scale(self.timeFrame, from_=0, to=0, length=680, showvalue=False, orient=HORIZONTAL)
        self.endTimeLabel = Label(self.timeFrame, text="00:00")

        self.loopPlaybackMessageFrame = Frame(self.root, borderwidth=3, relief="groove")
        self.loopPlaybackMessage = Label(self.loopPlaybackMessageFrame, 
            font=("Microsoft Yahei", 20)
        )
        self.loopPlaybackMessageShow = 0

        self.songsTable = {}
        self.index = None
        self.playOrStop = False # play: True; stop: False
        with open("./resource/music.info", "rb") as f:
            self.volume = pickle.load(f)["volume"]

        self.timeSeconds = 0
        self.songSeconds = 0
        self.changingTime = False
        self.starting = False
        self.musicloopPlayback = 0 # 0: No cycle; 1: Single cycle; 2: List cycle

    def Wheel(self, event):
        self.musicList.yview_scroll(int(-1*(event.delta/120)), "units")
        self.authorList.yview_scroll(int(-1*(event.delta/120)), "units")

        return "break"

    def ScrollCommand(self, *xx):
        self.musicList.yview(*xx)
        self.authorList.yview(*xx)

    def create(self):
        self.root.title("Plemus - Music Software")
        self.root.iconphoto(True, self.tk_image)
        self.root.resizable(0, 0)
        
        self.mainFrame.pack()

        self.playFrame.pack(padx=20, pady=20, side=LEFT)
        self.coverLabel.pack()
        self.titileLabel.pack()
        self.authorLabel.pack()

        self.settingFrame.pack(padx=20, pady=10, side=RIGHT)

        self.playListFrame.pack(pady=5)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.authorList.pack(side=RIGHT)
        self.musicList.pack(side=RIGHT)

        self.valumeScale.pack(padx=10, pady=5, side=RIGHT)
        self.playOrStopButton.pack(padx=10, pady=5, side=RIGHT)
        self.loopPlaybackButton.pack(padx=10, pady=5, side=RIGHT)
        
        self.timeFrame.pack(pady=10)
        self.nowTimeLabel.pack(side=LEFT)
        self.timeScale.pack(side=LEFT)
        self.endTimeLabel.pack(side=LEFT)

        self.loopPlaybackMessage.pack(padx=15, pady=15)

        self.root.update()
        self.xLength = int(self.root.winfo_screenwidth()/2 - self.root.winfo_width()/2)
        self.yLength = int(self.root.winfo_screenheight()/2 - self.root.winfo_height()/2)
        self.root.geometry(f"+{self.xLength}+{self.yLength}")

        self.valumeScale.set(self.volume*10)
        
        self.musicList.bind("<MouseWheel>", self.Wheel)
        self.authorList.bind("<MouseWheel>", self.Wheel)
        self.listScrollbar.bind("<MouseWheel>", self.Wheel)

        self.musicList.bind("<Double-Button-1>", self.chooseMusic)
        self.authorList.bind("<Double-Button-1>", self.chooseMusic)

        self.valumeScale.bind("<Motion>", self.setVolume)
        self.timeScale.bind("<ButtonPress-1>", lambda non: self.changingTimeSet(True))
        self.timeScale.bind("<ButtonRelease-1>", lambda non: self.changingTimeSet(False))
    
    def changingTimeSet(self, pressOrDown):
        self.changingTime = pressOrDown

    def timePlus(self):
        if self.changingTime == False and self.playOrStop == True: 
            self.timeSeconds += 1
            self.timeScale.set(self.timeSeconds)

            if self.timeSeconds >= self.songSeconds:
                if self.musicloopPlayback == 1:
                    self.playSong("./resource/music")
                elif self.musicloopPlayback == 2: 
                    self.index += 1
                    if self.index >= len(self.songsTable.keys()): self.index = 0
                    asyncio.run(self.playMusic(list(self.songsTable.keys())[self.index]))
                else: 
                    self.stopSong()

        self.root.after(1000, self.timePlus)
    
    def timeScaleSet(self):
        if self.changingTime == True:
            self.timeSeconds = self.timeScale.get()
            try:
                pygame.mixer.music.set_pos(self.timeSeconds)
            except pygame.error: ...
        
        m, s = divmod(self.timeSeconds, 60)
        timeShow = "%02d:%02d" % (m, s)
        self.nowTimeLabel["text"] = timeShow

        self.root.after(10, self.timeScaleSet)
    
    def setVolume(self, none):
        volume = self.valumeScale.get()/10
        if volume != self.volume:
            self.volume = volume
            try:
                pygame.mixer.music.set_volume(self.volume)
            except pygame.error: ...
            with open("./resource/music.info", "wb") as f:
                pickle.dump({"volume": self.volume}, f)
    
    def loopPlayback(self):
        self.musicloopPlayback += 1
        if self.musicloopPlayback == 3: self.musicloopPlayback = 0

        self.loopPlaybackMessageShow = 6
        if self.musicloopPlayback == 0:
            self.loopPlaybackMessage["text"] = "Loop playback canceled"
            self.loopPlaybackButton["text"] = "Single loop playback"
        elif self.musicloopPlayback == 1:
            self.loopPlaybackMessage["text"] = "Switched to single loop"
            self.loopPlaybackButton["text"] = "List looping"
        elif self.musicloopPlayback == 2:
            self.loopPlaybackMessage["text"] = "Switched to list loop"
            self.loopPlaybackButton["text"] = "Cancel loop playback"
    
    def showLoopPlaybackMessage(self):
        if self.loopPlaybackMessageShow != 0:
            self.loopPlaybackMessageFrame.place(x=self.xLength/2)
            self.loopPlaybackMessageShow -= 1
        else: self.loopPlaybackMessageFrame.place_forget()

        self.root.after(200, self.showLoopPlaybackMessage)

    def playSong(self, path):
        self.timeSeconds = 0
        self.songSeconds = 0
        self.changingTime = False
        
        try:
            song = MP3(path)
        except: return
        self.songSeconds = song.info.length

        self.timeScale["to"] = self.songSeconds

        m, s = divmod(self.songSeconds, 60)
        timeShow = "%02d:%02d" % (m, s)
        self.endTimeLabel["text"] = timeShow

        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.load(path) 
        pygame.mixer.music.play()

        if self.starting == False:
            self.timePlus()

        self.starting = True
    
    def stopSong(self):
        self.playOrStop = False
        self.playOrStopButton["text"] = "Play"

        try:
            pygame.mixer.music.fadeout(1000)
        except pygame.error: return

    def stopOrPlay(self):
        if self.playOrStop == True:
            self.stopSong()
        else:
            if self.timeSeconds >= self.songSeconds:
                self.playSong("./resource/music")
            try:
                pygame.mixer.music.play(0, self.timeSeconds, fade_ms=1000)
            except pygame.error: return

            self.playOrStop = True
            self.playOrStopButton["text"] = "Pause"
    
    def resize(self, w, h, w_box, h_box, pil_image):  
        """
        resize a pil_image object so it will fit into 
        a box of size w_box times h_box, but retain aspect ratio
        """  
        f1 = 1.0*w_box/w # 1.0 forces float division in Python2
        f2 = 1.0*h_box/h  
        factor = min([f1, f2])
        # use best down-sizing filter  
        width = int(w*factor)  
        height = int(h*factor)  
        return pil_image.resize((width, height), Image.Resampling.LANCZOS)
    
    def openImage(self, path):
        pil_image = Image.open(path)
        pil_image_resized = self.resize(pil_image.size[0], pil_image.size[1], 310, 310, pil_image)  
        tk_image = ImageTk.PhotoImage(pil_image_resized)

        return tk_image
    
    async def playMusic(self, songName):
        try:
            pygame.mixer.quit()
        except pygame.error: ...

        net = Network()
        net.send(json.dumps(["get", songName]))
        self.songsInformation = json.loads(net.get())
        net.send("cover")
        cover = net.get(usingEncoding=False)
        net.send("music")
        music = net.get(usingEncoding=False)
        net.close()

        with open("./resource/cover.png", "wb") as f:
            f.write(cover)
        
        with open("./resource/music", "wb") as f:
            f.write(music)

        self.titileLabel["text"] = self.songsInformation[0]
        self.authorLabel["text"] = self.songsInformation[1]

        self.tk_image = self.openImage("./resource/cover.png")
        self.coverLabel["image"] = self.tk_image

        self.playOrStop = True
        self.playOrStopButton["text"] = "Pause"

        self.playSong("./resource/music")
        
        os.remove("./resource/cover.png")
        
    def chooseMusic(self, none):
        musicListGetting = self.musicList.curselection()
        authorListGetting = self.authorList.curselection()
        if musicListGetting == () and authorListGetting == (): return
        self.index = musicListGetting[0] if musicListGetting != () else authorListGetting[0]
        
        asyncio.run(self.playMusic(list(self.songsTable.keys())[self.index]))
    
    async def getMusicList(self):
        net = Network()
        net.send(json.dumps(["MusicList"]))
        self.songsTable = json.loads(net.get())
        net.close()

        for i in self.songsTable.keys():
            self.musicList.insert(END, i)
            self.authorList.insert(END, self.songsTable[i]["artist"])
    
    def run(self):
        try:
            os.remove("./resource/music")
        except os.error: ...

        asyncio.run(self.getMusicList())

if __name__ == "__main__":
    win = Windows()
    win.create()
    win.run()
    win.timeScaleSet()
    win.showLoopPlaybackMessage()

    mainloop()
