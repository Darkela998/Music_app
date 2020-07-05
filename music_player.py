from tkinter import *
from tkinter import font, messagebox
from tkinter.ttk import Notebook, Combobox
from tkinter.filedialog import askopenfilename
from duration import *
from socket import socket, gethostname
import threading
import time
from pygame import mixer
import json
from re import match
from itertools import compress
from functools import reduce


class Muzika:
    def __init__(self, id_muzike, naziv, ime_autora, datum_azuriranja, link, featuring, broj_slusanja):
        self.id_muzike = id_muzike
        self.naziv = naziv
        self.ime_autora = ime_autora
        self.datum_azuriranja = datum_azuriranja
        self.link = link
        self.featuring = featuring
        self.broj_slusanja = broj_slusanja

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

    def __str__(self):
        ispis = str.title(self.naziv) + " by " + self.ime_autora.title() + (
            f" ft. {self.featuring}" if (self.featuring != 0 and self.featuring is not None) else "")
        return ispis


class Korisnik:
    def __init__(self, id_osobe, status, username, password):
        self.id_osobe = id_osobe
        self.status = status
        self.username = username
        self.password = password

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

    def __str__(self):
        return f'Username: {self.username}, Status: {self.status}'


b = True
b1 = True
start = 0
prethodnaPesma = -1

korisnici = []
pesme = []
ulogovan = None
nowPlaying = None
favorites = []
autori = []
imenaAutora = []

host = gethostname()
port = 1234

pozadina = 'gray15'
pozadina2 = 'gray25'
fgWhite = 'white'


def startUp(strVar):
    try:
        request = {'korisnici': korisnici, 'pesme': pesme, 'autori': autori}
        for i in request:
            res = json.loads(requestToServer(i))
            if not str.strip(str(res)):
                strVar.set("Aplikacija ne moze da upostavi konekciju sa bazom, molimo vas pokusajte kasnije.")
            else:
                for o in res:
                    request[i].append(
                        o if i == 'autori' else (Korisnik if i == 'korisnici' else Muzika).from_json(json.dumps(o)))
    except Exception as ex:
        print(ex)
        strVar.set('Doslo je do greske prilikom konekcije, molimo Vas pokusajte kasnije')


def requestToServer(req):
    try:
        sock = socket()
        sock.connect((host, port))
        sock.send(str(req).encode())
        buffer = "["
        while True:
            res = sock.recv(1024).decode()
            if "#" in res:
                break
            else:
                buffer += res
        sock.close()
        buffer += "]"
        return buffer
    except Exception as e:
        print("Request greska: ", e)
        return None


def login():
    r = Tk()
    pocetniError = StringVar()
    pocetniError.set("")
    r.resizable(0, 0)

    tabs1 = Notebook(r)

    if len(korisnici) == 0 and len(pesme) == 0:
        t1 = threading.Thread(target=startUp, args=(pocetniError,))
        t1.start()

    def provera_unosa(*a):
        global ulogovan, boolProveraUnosa
        req = list(filter(lambda x: x.username == varUser.get() and x.password == varPasswd.get(), korisnici))
        if len(req) != 0:
            ulogovan = req[0]
            r.destroy()
        else:
            pocetniError.set("Pogrešan username ili password")
            lblLogStatus['fg'] = 'red'

    def guest(*a):
        global ulogovan
        ulogovan = Korisnik(-1, 'gost', 'Guest', '')
        r.destroy()

    def register(*a):

        def provera_unosa_reg():
            def aw():
                res = requestToServer(
                    f"register#{Korisnik.to_json(Korisnik(0, 'korisnik'.strip(), varUserReg.get(), varRePassw.get()))}")

                if res is None:
                    errorReg.set("Greska sa konekcijom, molimo vas pokusajte kasnije")
                    return False

                obj = json.loads(res)
                tabs1.select(frame)
                lblLogStatus['fg'] = 'green2'
                pocetniError.set("Uspesno ste se registrovali")
                korisnici.append(Korisnik.from_json(json.dumps(obj[0])))
                tabRegister.destroy()
                return True

            try:
                username = varUserReg.get().strip()
                passw = varPasswdReg.get().strip()
                repassw = varRePassw.get().strip()
                poruka = ""
                if username and passw and repassw:
                    if varUserReg.get() not in [x.username for x in korisnici]:
                        if varPasswdReg.get() == varRePassw.get():
                            if match(r'^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{8,}$', varRePassw.get()):
                                threading.Thread(target=aw).start()
                            else:
                                poruka = "Sfire mora da sadrzi minimum 8 karaktera i makar jedan numericki karakter"
                        else:
                            poruka = "Sifre se ne podudaraju"
                    else:
                        poruka = "Zauzet username"
                else:
                    poruka = "Sva polja su obavezna"
            except:
                poruka = "Greska sa konekcijom, molimo vas pokusajte kasnije"

            errorReg.set(poruka)

        tabRegister = Frame(tabs1, bg=pozadina, pady=50, padx=30)

        lblUsernameReg = Label(tabRegister, text='username'.capitalize(), font=fontLogin, bg=pozadina, fg=fgWhite)
        lblUsernameReg.grid(row=0, column=0, columnspan=2)

        varUserReg = StringVar()
        entUsernameReg = Entry(tabRegister, font=fontLogin, textvariable=varUserReg)
        entUsernameReg.grid(row=1, column=0, pady=10, columnspan=2)

        lblPasswordReg = Label(tabRegister, text='Password'.capitalize(), font=fontLogin, bg=pozadina, fg=fgWhite)
        lblPasswordReg.grid(row=2, column=0, columnspan=2)

        varPasswdReg = StringVar()
        entPasswordReg = Entry(tabRegister, font=fontLogin, textvariable=varPasswdReg, show='*')
        entPasswordReg.grid(row=3, column=0, pady=10, columnspan=2)

        lblRePassw = Label(tabRegister, text='Repeat Password'.capitalize(), font=fontLogin, bg=pozadina, fg=fgWhite)
        lblRePassw.grid(row=4, column=0, columnspan=2)

        varRePassw = StringVar()
        entlblRePassw = Entry(tabRegister, font=fontLogin, textvariable=varRePassw, show='*')
        entlblRePassw.grid(row=5, column=0, pady=10, columnspan=2)

        errorReg = StringVar()
        lblRegStatus = Label(tabRegister, fg='red', bg=pozadina, textvariable=errorReg)
        lblRegStatus.grid(row=6, column=0, columnspan=2)

        r.bind('<Return>', lambda x: threading.Thread(target=provera_unosa_reg).start())

        btnReg = Button(tabRegister, text='Register', font=fontLogin, width=entPassword['width'],
                        command=provera_unosa_reg)
        btnReg.grid(row=7, column=0, pady=10, padx=100, columnspan=2)
        tabs1.add(tabRegister, text='Register')
        tabs1.select(tabRegister)

    r.configure(background=pozadina)
    r.resizable(0, 0)
    r.title("Socijalni deezer - Login")

    frame = Frame(r, bg=pozadina, pady=50, padx=30)
    fontLogin = font.Font(family="Helvetica", size=18)

    lblUsername = Label(frame, text='username'.capitalize(), font=fontLogin, bg=pozadina, fg=fgWhite)
    lblUsername.grid(row=0, column=0, columnspan=2)

    varUser = StringVar()
    entUsername = Entry(frame, font=fontLogin, textvariable=varUser)
    entUsername.grid(row=1, column=0, pady=10, columnspan=2)

    lblPassword = Label(frame, text='Password'.capitalize(), font=fontLogin, bg=pozadina, fg=fgWhite)
    lblPassword.grid(row=2, column=0, columnspan=2)

    varPasswd = StringVar()
    entPassword = Entry(frame, font=fontLogin, textvariable=varPasswd, show='*')
    entPassword.grid(row=3, column=0, pady=10, columnspan=2)

    lblLogStatus = Label(frame, fg='red', bg=pozadina, textvariable=pocetniError)
    lblLogStatus.grid(row=4, column=0, columnspan=2)
    r.bind('<Return>', provera_unosa)
    btnLogin = Button(frame, text='Login', font=fontLogin, width=entPassword['width'],
                      command=provera_unosa)
    btnLogin.grid(row=5, column=0, pady=10, padx=100, columnspan=2)

    lblRegister = Label(frame, text='Register', font=fontLogin, bg=pozadina, fg=fgWhite)
    lblRegister.bind('<Button>', register)
    lblRegister.grid(row=6, column=1, sticky=W)

    lblGuest = Label(frame, text='Guest', font=fontLogin, bg=pozadina, fg=fgWhite)
    lblGuest.bind('<Button>', guest)
    lblGuest.grid(row=6, column=0, sticky=E, padx=(0, 30))

    tabs1.add(frame, text='Login')
    tabs1.pack()
    r.mainloop()

    if ulogovan is not None:
        program()


def program():
    def ispis(link):
        try:
            global b
            b = False
            for i in range(int(duration(link)) + 12):
                time.sleep(1)
                lblPlaying['text'] = minutes(int(mixer.music.get_pos() / 1000))
                if b:
                    break
            else:
                changeSong(1)
        except:
            pass

    def onselect(*a):
        frameBtns.pack(side=BOTTOM)
        frame2.pack(side=BOTTOM, fill=BOTH, expand=TRUE)
        global b, b1, nowPlaying, prethodnaPesma
        b, b1 = True, True
        nowPlaying = pesme[listaPesama.curselection()[0]]
        mixer.music.load('music\\' + nowPlaying.link)
        mixer.music.play()
        lblSong['text'] = str(nowPlaying)
        t = threading.Thread(target=ispis, args=(nowPlaying.link,), name='ThreadIspis')
        t.setDaemon(True)
        t.start()
        changeFav()
        if prethodnaPesma != nowPlaying.id_muzike:
            nowPlaying.broj_slusanja += 1
        prethodnaPesma = nowPlaying.id_muzike

    def changeFav():
        photoFav.config(file=r'img\favorite1.png' if True in list(
            map(lambda x: x == nowPlaying.id_muzike, favorites)) else r'img\favorite.png')

    def PlayOrPause():
        global b1
        if b1:
            mixer.music.pause()
        else:
            mixer.music.unpause()
        b1 = not b1

    def volume(a):
        vol = int(a) / 100
        mixer.music.set_volume(vol)

    def changeSong(a):
        if len(listaPesama.curselection()) == 0:
            return

        curr = listaPesama.curselection()[0]

        if (a < 0 and curr == 0) or (a > 0 and curr == (listaPesama.size() - 1)):
            return

        listaPesama.selection_clear(0, END)
        listaPesama.selection_set(curr + a)
        listaPesama.activate(curr)
        onselect()

    def addToFav():
        if True in list(map(lambda x: x == nowPlaying.id_muzike, favorites)):
            favorites.remove(nowPlaying.id_muzike)
        else:
            favorites.append(nowPlaying.id_muzike)
        changeFav()

    def ucitajFav():
        sock = socket()
        sock.connect((host, port))
        sock.send(f'favorites#{ulogovan.id_osobe}'.encode())
        res = json.loads((sock.recv(1024)).decode())
        for o in res:
            favorites.append(o['id_muzike'])
        sock.close()

    def logout(*a):
        global ulogovan, b
        favorites.insert(0, ulogovan.id_osobe)
        ulogovan = None
        b = True
        requestToServer(f"writeFav#{json.dumps(favorites)}")
        mixer.music.stop()
        root.destroy()
        login()

    global favorites
    favorites = []

    tUcitajFavorites = threading.Thread(target=ucitajFav, name='threadFavorites')
    tUcitajFavorites.start()

    root = Tk()
    tabs = Notebook(root)
    tabStart = Frame(tabs, bg=pozadina)

    mixer.init()
    root.resizable(0, 0)

    font1 = font.Font(family="Helvetica", size=36, weight="bold")
    font2 = font.Font(family="Helvetica", size=18)
    font3 = font.Font(family="Helvetica", size=12)

    root.configure(background=pozadina)

    lblUlogvan = Label(tabStart, text=ulogovan.username, font=font2, fg=fgWhite, bg=pozadina)
    lblUlogvan.pack(side=TOP, anchor=E)
    lblUlogvan.bind("<Double-Button>", logout)

    lblFrame = LabelFrame(tabStart, text="Socijalni deezer", font=font1, labelanchor=N, fg=fgWhite, bg="gray25",
                          pady=50)
    lblFrame.pack(fill=BOTH, expand=True)

    frame1 = Frame(lblFrame, bg=pozadina2)
    frame1.pack(fill=BOTH, expand=True)

    lblVolume = Label(frame1, text='Volume', fg=fgWhite, bg=pozadina2)
    lblVolume.pack(anchor=E)
    frame11 = Frame(frame1, padx=30, bg=pozadina2)
    frame11.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame11)
    scrollbar.pack(side=RIGHT, fill=Y)
    varListaPesama = StringVar()
    listaPesama = Listbox(frame11, yscrollcommand=scrollbar.set, font=font2, width=50, listvariable=varListaPesama)
    listaPesama.bind('<Double-Button>', onselect)
    listaPesama.pack(fill=BOTH, expand=True)

    frameBtns1 = Frame(lblFrame, bg=pozadina2)
    varCheckFav = IntVar()
    chkFav = Checkbutton(frameBtns1, text='Favorites', variable=varCheckFav, onvalue=1, offvalue=0, font=font2,
                         bg=pozadina2, bd=3, fg=fgWhite, selectcolor='black', command=lambda: varListaPesama.set(list(
            compress(pesme, list(map(lambda x: x.id_muzike in favorites, pesme)))) if varCheckFav.get() else pesme))

    chkFav.grid(row=0, column=0, pady=(10, 0))

    btnSort = Button(frameBtns1, text='Sort', bg='gold', font=font2)
    # btnSort.grid(row=0, column=1, padx=20, pady=(10, 0))

    frameBtns1.pack(side=BOTTOM, anchor=S)

    varListaPesama.set(
        list([str(x) + " " * (58 - len(str(x).strip())) + str(minutes(int(duration(x.link)))) for x in pesme]))

    var = DoubleVar()
    scale = Scale(frame1, variable=var, bg=pozadina2, command=volume, from_='100', to='0', fg=fgWhite,
                  activebackground='gold', length=300, sliderlength=15)
    scale.pack(side=RIGHT)
    scale.set(70)

    scrollbar.config(command=listaPesama.yview)

    frameBtns = Frame(tabStart, bg=pozadina)

    photo = PhotoImage(file=r"img\play_pause.png")
    photoBack = PhotoImage(file=r"img\back.png")
    photoForw = PhotoImage(file=r"img\forw.png")
    photoFav = PhotoImage(file=r"img\favorite.png")

    btnBack = Button(frameBtns, activebackground=pozadina2, font=font2, bg=pozadina, bd=0, image=photoBack,
                     command=lambda: changeSong(-1))
    btnBack.grid(row=0, column=0, padx=(60, 0))
    btnPlayPause = Button(frameBtns, font=font2, activebackground=pozadina2, bg=pozadina, bd=0,
                          command=PlayOrPause,
                          image=photo)
    btnPlayPause.grid(row=0, column=1, padx=20)
    btnForw = Button(frameBtns, image=photoForw, activebackground=pozadina2, font=font2, bg=pozadina, bd=0,
                     command=lambda: changeSong(1))
    btnForw.grid(row=0, column=2)

    btnFav = Button(frameBtns, image=photoFav, activebackground=pozadina2, font=font2, bg=pozadina, bd=0,
                    command=addToFav)
    btnFav.grid(row=0, column=3, padx=(50, 0))

    frame2 = Frame(tabStart, bg='lightgray')

    lblPlaying = Label(frame2, text='--:--', font=font3, bg='lightgray')
    lblPlaying.pack(side=RIGHT, anchor=E)
    lblSong = Label(frame2, font=font3, bg='lightgray')
    lblSong.pack(side=LEFT, anchor=W)

    tabs.add(tabStart, text='Pocetna')
    tabs.pack()

    if ulogovan.status == 'admin':
        tabPesme = Frame(tabs, bg=pozadina)
        tabKorisnici = Frame(tabs, bg=pozadina)
        tabTopPesme = Frame(tabs, bg=pozadina)

        def adminPesme():
            def chooseFile():
                path = str(askopenfilename()).split("/")[-1]
                btnChoseFile['text'] = path
                varNazivPesme.set(path.split(".")[0].replace("_", " ").capitalize())

            def featPrikaz():
                comboFeat['state'] = 'readonly' if varCheckFeat.get() == 1 else 'disabled'

            def currentPick(obj):
                return list(filter(lambda x: imenaAutora[x] == obj, [i for i in range(len(autori))]))[0]

            def popuniFormuPesme(e):
                obj = pesme[e.widget.curselection()[0]]
                btnChoseFile['text'] = obj.link.split("\\")[-1]
                varNazivPesme.set(obj.naziv)
                comboAutori.current(currentPick(obj.ime_autora))
                if obj.featuring is not None and obj.featuring != 0:
                    comboAutori.current(currentPick(obj.featuring))

            def dodajAutora(ime):
                global imenaAutora
                if str(ime).lstrip().rstrip() in imenaAutora:
                    messagebox.showinfo("Dodavanje autora", "Postoji zadati autor")

                res = requestToServer(f'writeAutor#{str(ime).capitalize()}')
                message = "Neuspesno dodavanje autora"
                if res is not None:
                    autori.clear()
                    for o in json.loads(res):
                        autori.append(o)
                    imenaAutora = [x['ime_autora'] for x in autori]
                    comboAutori['values'] = imenaAutora
                    comboFeat['values'] = imenaAutora
                message = "Uspesno dodavanje autora"
                messagebox.showinfo("Dodavanje autora", message)

            def snimiPesmuAdmin():
                btnSnimi['state'] = 'disabled'
                message = 'Doslo je do greske prilikom snimanja'
                try:
                    m = Muzika(0, varNazivPesme.get(), comboAutori.get(), 0, str(btnChoseFile['text']),
                               comboFeat.get() if varCheckFeat.get() else 0, 0)
                    provera = ''.join([i for i in [str(x) for x in pesme] if not i.isdigit()])
                    if str(m) == provera:
                        message = 'Postoji zadata pesma'
                    else:
                        requestToServer(f'writeMuzika#{m.to_json()}')
                        message = 'Uspesno ste dodali pesmu:\n' + str(m)
                        pesme.append(m)
                        varListaPesama.set(
                            list([str(x) + " " * (55 - len(str(x))) + str(minutes(int(duration(x.link)))) for x in
                                  pesme]))

                except Exception as e:
                    print(e)
                    message = 'Greska: ' + str(e)
                finally:
                    btnSnimi['state'] = 'normal'
                    messagebox.showinfo('Snimanje pesme', message)

            lblPesmeAdmin = Label(tabPesme, text="Pesme", font=font1, bg=pozadina, fg=fgWhite)
            lblPesmeAdmin.pack()

            frameAdminPesme1 = Frame(tabPesme)

            scrollbarAdminPesme = Scrollbar(frameAdminPesme1)
            scrollbarAdminPesme.pack(side=RIGHT, fill=Y)

            listaPesamaAdmin = Listbox(frameAdminPesme1, font=font2, width=50, listvariable=varListaPesama)
            listaPesamaAdmin.pack(fill=BOTH, expand=True)
            listaPesamaAdmin.activate(0)
            listaPesamaAdmin.bind("<Double-Button>", popuniFormuPesme)
            scrollbar.config(command=listaPesamaAdmin.yview)
            frameAdminPesme1.pack(fill=BOTH, expand=True)

            framePesme = Frame(tabPesme, bg=pozadina2, padx=30, pady=10)
            varNazivPesme = StringVar()
            lblFile = Label(framePesme, text='File', font=font2, bg=pozadina2, fg=fgWhite)
            lblFile.grid(row=0, column=0)
            btnChoseFile = Button(framePesme, text='Choose file', font=font3, command=chooseFile)
            btnChoseFile.grid(row=1, column=0)
            lblNaziv = Label(framePesme, text='Naziv pesme', font=font2, bg=pozadina2, fg=fgWhite)
            lblNaziv.grid(row=0, column=1)
            entNaziv = Entry(framePesme, textvariable=varNazivPesme, font=font3)
            entNaziv.grid(row=1, column=1, padx=10)
            lblAutor = Label(framePesme, text='Autor', font=font2, bg=pozadina2, fg=fgWhite)
            lblAutor.grid(row=0, column=2)
            imenaAutora = [str(x['ime_autora']).title() for x in autori]
            comboAutori = Combobox(framePesme, values=imenaAutora, font=font3, state='readonly')
            comboAutori.grid(row=1, column=2)

            lblFeat = Label(framePesme, text='Feat.', font=font2, bg=pozadina2, fg=fgWhite)
            comboFeat = Combobox(framePesme, values=imenaAutora, font=font3, state='disabled')
            lblFeat.grid(row=0, column=3)
            comboFeat.grid(row=1, column=3, padx=10)

            comboFeat.current(0)
            comboAutori.current(0)

            varCheckFeat = IntVar()
            checkFeat = Checkbutton(framePesme, text='Feat', variable=varCheckFeat, onvalue=1, offvalue=0, font=font3,
                                    bg=pozadina2, bd=3, fg=fgWhite, selectcolor='black', command=featPrikaz)

            checkFeat.grid(row=2, column=2, sticky=NW)

            btnSnimi = Button(framePesme, text='Snimi', font=font2, padx=10, command=snimiPesmuAdmin)
            btnSnimi.grid(row=2, column=3, padx=20, pady=20, sticky=SE)

            Label(framePesme, text='Dodaj autora', font=font2, bg=pozadina2, fg=fgWhite).grid(row=3, column=0)
            varDodajAutora = StringVar()
            Entry(framePesme, textvariable=varDodajAutora, font=font3).grid(row=4, column=0)
            Button(framePesme, text='Snimi autora', font=font2,
                   command=lambda: threading.Thread(target=dodajAutora,
                                                    args=(varDodajAutora.get(),)).start()).grid(row=4, column=1)
            framePesme.pack(expand=True)

        def adminKorisnici():
            pass

        def adminCharts():
            def chart():
                krug = C.create_oval(coord, fill="lightblue")
                izabraniId = pesme[listaPesamaCharts.curselection()[0]].id_muzike
                brFav = reduce((lambda x, y: x + y),
                               list(map(lambda x: x['id_muzike'] == izabraniId, res)))
                brOdslusanih = pesme[listaPesamaCharts.curselection()[0]].broj_slusanja

                rez = 1 if brOdslusanih == 0 or brFav == 0 else (brFav / (
                    (brOdslusanih / (
                            brOdslusanih ** (len(str(brOdslusanih)) - 2))) if brOdslusanih != 0 else 0.1)) * 100
                procenat1 = 100 if rez > 100 else rez
                pomeraj = procenat1 * 3.6
                arc = C.create_arc(coord, fill='purple', start=90, extent=-pomeraj)

            lblCharts = Label(tabTopPesme, text="Najslusanije pesme", pady=20, font=font1, bg=pozadina, fg=fgWhite)
            lblCharts.pack()
            res = json.loads(requestToServer('allFavorites'))
            topPesme = sorted(pesme, key=lambda x: x.broj_slusanja, reverse=True)[0:3]
            for i in range(len(topPesme)):
                Label(tabTopPesme, font=font2, bg=pozadina, fg='gold', pady=10,
                      text=f'{i + 1}# {str(topPesme[i])}').pack()

            frameCharts = Frame(tabTopPesme, bg=pozadina, pady=20)
            Label(frameCharts, text='Lista pesama', font=font2, bg=pozadina, fg=fgWhite).grid(row=0, column=0, sticky=W)
            frameScroll = Frame(frameCharts)
            scrollbarCharts = Scrollbar(frameScroll)
            scrollbarCharts.pack(side=RIGHT, fill=Y)
            listaPesamaCharts = Listbox(frameScroll, font=font3, width=45, listvariable=varListaPesama)
            listaPesamaCharts.pack()
            scrollbarCharts.config(command=listaPesamaCharts.yview)
            frameScroll.grid(row=1, column=0, padx=(10, 0))

            Label(frameCharts, text='Odnos najslusanijih/omiljenih(ljubicasto)\n pesama:', font=font2, bg=pozadina, fg=fgWhite).grid(
                row=0, column=1, sticky=E)
            C = Canvas(frameCharts, bg=pozadina, bd=0, highlightthickness=0, relief='ridge', height=250, width=300)
            C.grid(row=1, column=1)
            coord = 60, 50, 240, 210
            krug = C.create_oval(coord, fill="lightblue")

            listaPesamaCharts.bind("<Double-Button>", lambda x: chart())
            frameCharts.pack(fill=BOTH, expand=True)

        adminPesme()
        adminKorisnici()
        adminCharts()
        tabs.add(tabPesme, text="Pesme")
        # tabs.add(tabKorisnici, text="Korisnici")
        tabs.add(tabTopPesme, text="Charts")

    root.mainloop()
    onEnd()


def onEnd():
    try:
        mixer.music.stop()
        if ulogovan is not None and ulogovan.status != 'guest':
            requestToServer(f"writeBrojSlusanja#{[{f'{str(x.id_muzike)}': x.broj_slusanja} for x in pesme]}")
            favorites.insert(0, ulogovan.id_osobe)
            requestToServer(f"writeFav#{json.dumps(favorites)}")
    except Exception as e:
        print(e)


login()

# Za charts vezano za datum
# print(reduce((lambda x, y: x + y), list(map(lambda x: x==datum and niz[x]==id,niz))))
