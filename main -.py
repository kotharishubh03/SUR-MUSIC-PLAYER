# all imports
import os
import threading
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
from mutagen.mp3 import MP3
from pygame import mixer
from mutagen.easyid3 import EasyID3
from re import sub
# Global variables
queue = []
muted = FALSE
paused = FALSE
filename_path=""
play_song=""
current_time=0
t1=''
close=False
total_length=10
selected=0
i=0
abm=""
nextmusic=0
file='playlist/all.txt'
#initializing window 
root = tk.ThemedTk()
root.get_themes()# Returns a list of all themes that can be set
root.set_theme("breeze")  # Sets an available theme
root.geometry('585x400+200+200')  # window geometry
root.title("SUR MPlayer")
root.iconbitmap(r'images/sur.ico')
mixer.init()  # initializing the mixer

# functions
def on_closing():
    global paused
    global close
    paused = True
    close=True
    stop_music()
    root.destroy()
    
def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"
def rewind_music():
    global current_time
    global selected
    if current_time<=7:
        if selected==0:
            play_music()
        else:
            playlistbox.selection_clear(0, tkinter.END)
            playlistbox.select_set(selected-1)
            play_music()
    else:
        play_music()
        statusbar['text'] = "Music Rewinded"

def set_vol(val):
    
    volume = round(float(val),0)
    lowvol['text']=volume
    volume=volume / 100
    mixer.music.set_volume(volume)
    
def seek_play(val):
    global current_time
    global play_song
    val=int(round(float(val)))
    if val>current_time+2 or val<current_time-2:
        try:
            stop_music()
            mixer.music.play(loops=0, start=val)
            current_time=val
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_song)
        except:
            tkinter.messagebox.showerror('NO SONG SELECTED','PLZ Select a Song and try again')
            play_scale.set(0)
def mute_music():
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        volscale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        volscale.set(0)
        muted = TRUE

def show_details(play_song):
    global total_length
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    lengthlabel['text'] =timeformat
    play_scale['to']=total_length
    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    global current_time
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currenttimelabel['text'] =timeformat
            play_scale.set(current_time)
            time.sleep(1)
            current_time += 1

def play_music(x=0):
    global paused
    global queue
    global play_song
    global selected
    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0])
            selected_song = selected_song+x
            selected = selected_song
            play_it = queue[selected_song]
            play_song=play_it
            abtmusic = EasyID3(play_it)
            titletxt['text']=abtmusic['title'][0]
            albumtxt['text']=abtmusic['album'][0]
            artisttxt['text']=abtmusic['artist'][0]
            mixer.music.load(play_it)
            mixer.music.play()
            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            show_details(play_it)
        except:
            tkinter.messagebox.showerror('NO SONG SELECTED', 'PLZ Select a Song and try again')
            titletxt['text']='No title'
            albumtxt['text']='No album'
            artisttxt['text']='No artist'

def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"

def next_music():
    global current_time
    global total_length
    global nextmusic
    if nextmusic>2:
        current_time=total_length+10
        nextmusic=0
    else:
        mixer.music.stop()
        current_time+=10
        mixer.music.play(loops=0, start=current_time)
        nextmusic+=1
        print(nextmusic-1)
    

def del_song():
    global filename_path
    global queue
    global file
    try:
        selected_song = playlistbox.curselection()
        selected_song = int(selected_song[0])
        f=open(file,'r')
        c=open('playlist/all1.txt','a')
        var=f.read()
        for lines in var.split('\n'):
            if lines!=queue[selected_song]:
                if lines!="":
                    c.write(lines+"\n")
        f.close()
        c.close()
        os.remove(file)
        os.rename('playlist/all1.txt',file)
        
        playlistbox.delete(selected_song)
        queue.pop(selected_song)
        tkinter.messagebox.showinfo('Info','Deletion sucessfull')
    except:
        tkinter.messagebox.showerror('Error','Please Select A song from list to remove song')


def moreabt_song():
    global abm
    global abtm
    global play_it
    selected_song = playlistbox.curselection()
    if not selected_song:
        tkinter.messagebox.showerror('Error','Please Select A song from list to display about song')
    else:
        selected_song = int(selected_song[0])
        play_it = queue[selected_song]
        try:
            abtmusic = EasyID3(play_it)
            filename = abtmusic['title'][0]
            abtm=tk.ThemedTk()
            abtm.geometry('300x280+200+200')
            abtm.title("About ~~ "+filename)
            abtm.iconbitmap(r'images/sur.ico')
            abm=Listbox(abtm,width=50,height=15)
            abm.place(x=0,y=0)
            for key in sorted(abtmusic.keys()):
                val = abtmusic[key]
                abm.insert(END,key+" : "+val[0])
            editBtn = ttk.Button(abtm,text="Edit Data" ,command=ed_gui)
            editBtn.place(x=10,y=250)
        except:
            tkinter.messagebox.showerror('File not found', 'play the song to get info')

def ed_gui():
    global abm
    global abtm
    global play_it
    global selected_song
    global entry_edval
    def edit_save():
        abtmusic = EasyID3(play_it)
        try:
            abtmusic[selected_song]==str(entry_edval.get())
            abtmusic.save()
        except:
            tkinter.messagebox.showerror('Error in Saving','Saving cannot be completed as\n 1)Your windows is trying to interfere the program as an security threats\n2) Your Anitvirus is trying to interfere the program as an security threats\n3)Sorry nothing can be done for that ')
            eabtm.destroy()
    selected_song=abm.curselection()
    if not selected_song:
        tkinter.messagebox.showerror('Error','Please Select A song from list to display about song')
    selected_song = int(selected_song[0])
    abtmusic = EasyID3(play_it)
    l1=list(abtmusic.keys())
    l1=sorted(l1)
    selected_song=l1[selected_song]
    eabtm=tk.ThemedTk()
    eabtm.geometry('300x100+200+200')
    eabtm.title("Edit Value")
    title = ttk.Label(eabtm, text=selected_song)
    title.pack()
    entry_edval=ttk.Entry(eabtm,)
    entry_edval.pack()
    saveBtn = ttk.Button(eabtm,text="SAVE" ,command=edit_save)
    saveBtn.pack()
    abtm.destroy()
        
def about_us():
    tkinter.messagebox.showinfo('About SUR','This is an open Source Music player build using Python Tkinter by \nSHUBHAM KOTHARI\nANIKET KURKUTE\nATUL GADEKAR')

def browse_file():
    global filename_path
    global queue
    global file
    def add_to_q():
        global queue
        add_to_playlist(filename_path)
        mixer.music.queue(filename_path)
    if filename_path=="":
        filename_path = filedialog.askopenfilename()
        if filename_path!="":
            f=open(file,'a')
            f.write(filename_path+"\n")
            f.close()
            add_to_q()
    else:
        add_to_q()
    filename_path=""

def add_to_playlist(filename):
    global queue
    file_data = os.path.splitext(filename)
    if file_data[1] == '.mp3':
        abtmusic = EasyID3(filename_path)
        filename = abtmusic['title'][0]
    else:
        filename = os.path.basename(filename)
    playlistbox.insert(END, filename)
    queue.append(filename_path)
    playlistbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=playlistbox.yview)
def open_lyrics():
    play_it=''
    def edit_lyrics():
        def save_lyrics():
            val=display_label.get(1.0,END)
            play_it = queue[selected_song]
            abtmusic = EasyID3(play_it)
            var=abtmusic['title'][0]
            f=open("lyrics/"+var+".txt",'a')
            f.write(val)
            f.close()
            eabtm.destroy()
            open_lyrics()
        global display_label
        eabtm=tk.ThemedTk()
        eabtm.geometry('450x400+200+200')
        eabtm.title("ADD LYRICS")
        title = ttk.Label(eabtm, text="To Add Lyrics Copy Lyrics From Internet And Paste In Below text area")
        title.pack()
        display_label = Text(eabtm, width=50,height=20, font="ariel", fg="black", bg="white")
        display_label.pack()
        saveBtn = ttk.Button(eabtm,text="Save",command=save_lyrics)
        saveBtn.pack()
        lyrm.destroy()
    selected_song = playlistbox.curselection()
    if not selected_song:
        tkinter.messagebox.showerror('Error','Please Select A song from list to display about song')
    else:
        selected_song = int(selected_song[0])
        play_it = queue[selected_song]
        abtmusic = EasyID3(play_it)
        var=abtmusic['title'][0]
        lyrm=tk.ThemedTk()
        lyrm.title('LYRICS ~~'+var)
        lyrm.geometry('590x280+200+200')
        lyrm.iconbitmap(r'images/sur.ico')
        abm=Listbox(lyrm,width=100,height=15)
        abm.place(x=0,y=0)
        LYscrollbar = Scrollbar(lyrm)
        LYscrollbar.pack(side=RIGHT,fill=Y)
        try:
            f=open("lyrics/"+var+".txt",'r')
            for x in f:
                abm.insert(END,x.split())
            f.close()
            abm.config(yscrollcommand=LYscrollbar.set)
            LYscrollbar.config(command=abm.yview)
        except:
            abm.insert(END,"no lyrics")
            editBtn = ttk.Button(lyrm,text="Edit Data",command=edit_lyrics)
            editBtn.place(x=10,y=250)

def avplaylist(): 
    path = 'playlist/.'
    allplaylist=[]
    def add_playlist():
        def create_playlist():
            name=entry_edval.get()
            if name=="":
                tkinter.messagebox.showerror('Error','Name Is Not Valid')
            else:
                f=open('playlist/'+name+'.txt','a')
                tkinter.messagebox.showinfo('Info','Playlist created sucessfully')
                f.close()
            edwin.destroy()
            avplaylist()
        edwin=tk.ThemedTk()
        edwin.geometry('300x100+200+200')
        edwin.title("Edit Value")
        title = ttk.Label(edwin, text='Enter name for playlist')
        title.pack()
        entry_edval=ttk.Entry(edwin,)
        entry_edval.pack()
        saveBtn = ttk.Button(edwin,text="SAVE",command=create_playlist)
        saveBtn.pack()
        avplaylistgui.destroy()
    def play_playlist():
        global file
        global current_time
        global total_length
        global queue
        try:
            selected_playlist = avplaylist_listbox.curselection()
            selected_playlist = int(selected_playlist[0])
            play_it = allplaylist[selected_playlist]
            mixer.music.stop()
            playlistbox.delete(0,tkinter.END)
            queue.clear()
            file=play_it
            on_start(play_it)
            playlistbox.select_set(0)
            if not queue:
                titletxt['text']='No title'
                albumtxt['text']='No album'
                artisttxt['text']='No artist'
            else:    
                play_music()
            avplaylistgui.destroy()
        except:
            tkinter.messagebox.showerror('Error','Please Select A Playlist from list to play it')
    avplaylistgui=tk.ThemedTk()
    avplaylistgui.title('ALL PLAYLISTS')
    avplaylistgui.geometry('280x280+200+200')
    avplaylistgui.iconbitmap(r'images/sur.ico')
    avplaylist_listbox=Listbox(avplaylistgui,width=100,height=15)
    avplaylist_listbox.place(x=0,y=0)
    addBtn = ttk.Button(avplaylistgui,text="Add Playlist",command=add_playlist)
    addBtn.place(x=10,y=250)
    playplaylistBtn = ttk.Button(avplaylistgui,text="Play Playlist",command=play_playlist)
    playplaylistBtn.place(x=90,y=250)
    files = os.listdir(path)
    for name in files:
        allplaylist.append("playlist/"+name)
        name=name.split('.')
        avplaylist_listbox.insert(END,name[0])


def on_start(file='playlist/all.txt'):
    global filename_path
    f=open(file,'r')
    for x in f:
        filename_path=x.strip()
        browse_file()
        filename_path=""
    f.close()

def main_thread():
    global queue
    global close
    global current_time
    global total_length
    global selected
    while close==False:
        i=0
        if current_time+3>total_length:
            if selected==len(queue)-1:
                i=0-selected
                playlistbox.selection_clear(0, tkinter.END)
                playlistbox.select_set(0)
            else:    
                i=1+selected
                playlistbox.selection_clear(0, tkinter.END)
                playlistbox.select_set(i)
            stop_music()
            play_music()
        else:
            continue
    print("break")

    

# menu bar
menubar = Menu(root)
root.config(menu=menubar)
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)
# widgets
playlistbox = Listbox(root,yscrollcommand='yes',width=78)
playlistbox.place(x=10,y=10)
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT,fill=Y)
moreBtn = ttk.Button(root, text="More About Song", command=moreabt_song)
moreBtn.place(x=25,y=190)
lyricsBtn = ttk.Button(root, text="LYRICS", command=open_lyrics)
lyricsBtn.place(x=155,y=190)
addBtn = ttk.Button(root, text="+ Add", command=browse_file)
addBtn.place(x=255,y=190)
delBtn = ttk.Button(root, text="- Remove", command=del_song)
delBtn.place(x=355,y=190)
playlistBtn = ttk.Button(root, text="Playlist", command=avplaylist)
playlistBtn.place(x=455,y=190)
titlelab= ttk.Label(root, text="Title : ",font='Times 12 bold')
titlelab.place(x=10,y=225)
titletxt= ttk.Label(root, text="No Title",font='Times 12 bold')
titletxt.place(x=55,y=225)
albumlab= ttk.Label(root, text="Album : ",font='Times 11')
albumlab.place(x=10,y=245)
albumtxt= ttk.Label(root, text="No Album",font='Times 11')
albumtxt.place(x=60,y=245)
artistlab= ttk.Label(root, text="Artist : ",font='Times 11')
artistlab.place(x=10,y=265)
artisttxt= ttk.Label(root, text="No Artist",font='Times 11')
artisttxt.place(x=55,y=265)
currenttimelabel = ttk.Label(root, text='--:--')
currenttimelabel.place(x=2,y=285)
play_scale = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL,length=500,command=seek_play)
play_scale.place(x=35,y=285)
lengthlabel = ttk.Label(root, text='--:--')
lengthlabel.place(x=538,y=285)
prevPhoto = PhotoImage(file='images/previous.png').subsample(3,3)
prevBtn = ttk.Button(root, image=prevPhoto, command=rewind_music)
prevBtn.place(x=10,y=315)
playPhoto = PhotoImage(file='images/play.png').subsample(2,2)
playBtn = ttk.Button(root, image=playPhoto, command=play_music)
playBtn.place(x=60,y=310)
pausePhoto = PhotoImage(file='images/pause.png').subsample(2,2)
pauseBtn = ttk.Button(root, image=pausePhoto, command=pause_music)
pauseBtn.place(x=120,y=310)
nextPhoto = PhotoImage(file='images/next.png').subsample(3,3)
nextBtn = ttk.Button(root, image=nextPhoto, command=next_music)
nextBtn.place(x=180,y=315)
stopPhoto = PhotoImage(file='images/stop.png').subsample(3,3)
stopBtn = ttk.Button(root, image=stopPhoto, command=stop_music)
stopBtn.place(x=230,y=315)
mutePhoto = PhotoImage(file='images/mute.png').subsample(2,2)
volumePhoto = PhotoImage(file='images/volume.png').subsample(2,2)
volumeBtn = ttk.Button(root, image=volumePhoto, command=mute_music)
volumeBtn.place(x=380,y=320)
lowvol = ttk.Label(root, text="0")
lowvol.place(x=420,y=325)
volscale = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
volscale.set(70)
set_vol('70')  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
volscale.place(x=445,y=325)
highvol = ttk.Label(root, text="100")
highvol.place(x=545,y=325)

# status bar
statusbar = ttk.Label(root, text="Welcome to SUR MPlayer", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)

# end
root.protocol("WM_DELETE_WINDOW", on_closing)
on_start()
tm = threading.Thread(target=main_thread,)
tm.start()
root.mainloop()
