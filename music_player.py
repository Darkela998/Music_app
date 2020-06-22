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
from datetime import date
from functools import reduce


class Pesma:
    def __init__(self, id_pesme, id_autora, naziv, id_zanra, datum_azuriranja, link, feat, broj_slusanja):
        self.id_pesme = id_pesme
        self.naziv = naziv.strip()
        self.id_autora = id_autora
        self.id_zanra = id_zanra
        self.datum_azuriranja = datum_azuriranja
        self.link = link.strip()
        self.feat = feat
        self.broj_slusanja = broj_slusanja if broj_slusanja is not None else 0

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

    def __str__(self):
        ispis = str.title(self.naziv) + " by " + str(
            list(filter(lambda x: x.id_autora == self.id_autora, autori))[0].ime_autora).title() + (
                    f" ft. {self.feat}" if (self.feat is not None) else "")
        return ispis + " " * (58 - len(ispis.strip())) + str(minutes(int(duration(self.link))))


class Korisnik:
    def __init__(self, id_korisnika, status, username, password, email):
        self.id_korisnika = id_korisnika
        self.status = status.strip()
        self.username = username.strip()
        self.password = password.strip()
        self.email = email

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

    def __str__(self):
        return f'Username: {self.username}, Status: {self.status}'


class Autor:
    def __init__(self, id_autora, ime_autora):
        self.id_autora = id_autora
        self.ime_autora = ime_autora.strip()

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)


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
zanrovi = []
charts = []
imenaAutora = []
obrisane = []

host = gethostname()
port = 1234

pozadina = 'gray15'
pozadina2 = 'gray25'
fgWhite = 'white'


def startUp(strVar):
    try:
        global zanrovi, charts
        zanrovi = json.loads(requestToServer('zanrovi'))
        charts = json.loads(requestToServer('charts'))
        request = {'korisnici': korisnici, 'pesme': pesme, 'autori': autori}
        for i in request:
            res = json.loads(requestToServer(i))
            if not str.strip(str(res)):
                strVar.set("Aplikacija ne moze da upostavi konekciju sa bazom, molimo vas pokusajte kasnije.")
            else:
                for o in res:
                    request[i].append(
                        (Autor if i == 'autori' else Korisnik if i == 'korisnici' else Pesma).from_json(json.dumps(o)))
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
        req = list(filter(
            lambda x: x.username.strip() == varUser.get().strip() and x.password.strip() == varPasswd.get().strip(),
            korisnici))
        if len(req) != 0:
            ulogovan = req[0]
            r.destroy()
        else:
            pocetniError.set("Pogrešan username ili password")
            lblLogStatus['fg'] = 'red'

    def guest(*a):
        global ulogovan
        ulogovan = Korisnik(-1, 'gost', 'Guest', '', None)
        r.destroy()

    def register(*a):

        def provera_unosa_reg():
            def ok():
                res = requestToServer(
                    f"register#{Korisnik.to_json(Korisnik(0, 'korisnik'.strip(), varUserReg.get(), varRePassw.get(), varEmail.get() if len(varEmail.get().strip()) > 0 else None))}")

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
                email = varEmail.get().strip()
                poruka = ""

                if email:
                    poruka = 'Nevalidan format email-a'
                    if not match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', varEmail.get()):
                        errorReg.set(poruka)
                        return

                if username and passw and repassw:
                    if varUserReg.get() not in [x.username for x in korisnici]:
                        if varPasswdReg.get() == varRePassw.get():
                            if match(r'^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{8,}$', varRePassw.get()):
                                threading.Thread(target=ok).start()
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

        lblUsernameReg = Label(tabRegister, text='*Username', font=fontLogin, bg=pozadina, fg=fgWhite)
        lblUsernameReg.grid(row=0, column=0, columnspan=2)

        varUserReg = StringVar()
        entUsernameReg = Entry(tabRegister, font=fontLogin, textvariable=varUserReg)
        entUsernameReg.grid(row=1, column=0, pady=10, columnspan=2)

        lblPasswordReg = Label(tabRegister, text='*Password', font=fontLogin, bg=pozadina, fg=fgWhite)
        lblPasswordReg.grid(row=2, column=0, columnspan=2)

        varPasswdReg = StringVar()
        entPasswordReg = Entry(tabRegister, font=fontLogin, textvariable=varPasswdReg, show='*')
        entPasswordReg.grid(row=3, column=0, pady=10, columnspan=2)

        lblRePassw = Label(tabRegister, text='*Repeat Password', font=fontLogin, bg=pozadina, fg=fgWhite)
        lblRePassw.grid(row=4, column=0, columnspan=2)

        varRePassw = StringVar()
        entlblRePassw = Entry(tabRegister, font=fontLogin, textvariable=varRePassw, show='*')
        entlblRePassw.grid(row=5, column=0, pady=10, columnspan=2)

        lblEmail = Label(tabRegister, text='Email',
                         font=fontLogin, bg=pozadina, fg=fgWhite)
        lblEmail.grid(row=6, column=0, columnspan=2)

        varEmail = StringVar()
        entEmail = Entry(tabRegister, font=fontLogin, textvariable=varEmail)
        entEmail.grid(row=7, column=0, pady=10, columnspan=3)

        errorReg = StringVar()
        lblRegStatus = Label(tabRegister, fg='red', bg=pozadina, textvariable=errorReg)
        lblRegStatus.grid(row=8, column=0, columnspan=2)

        r.bind('<Return>', lambda x: threading.Thread(target=provera_unosa_reg).start())

        btnReg = Button(tabRegister, text='Register', font=fontLogin, width=entPassword['width'],
                        command=provera_unosa_reg)
        btnReg.grid(row=9, column=0, pady=10, padx=100, columnspan=2)
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
        lblSong['text'] = str(nowPlaying)[:(len(str(nowPlaying)) - 5)]
        t = threading.Thread(target=ispis, args=(nowPlaying.link,), name='ThreadIspis')
        t.setDaemon(True)
        t.start()
        changeFav()
        if prethodnaPesma != nowPlaying.id_pesme:
            nowPlaying.broj_slusanja += 1
        prethodnaPesma = nowPlaying.id_pesme

    def changeFav():
        photoFav.config(file=r'img\favorite1.png' if len(favorites) and True in list(
            map(lambda x: x['id_pesme'] == nowPlaying.id_pesme, favorites)) else r'img\favorite.png')

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
        if True in list(map(lambda x: x['id_pesme'] == nowPlaying.id_pesme, favorites)):
            favorites[:] = [d for d in favorites if d['id_pesme'] != nowPlaying.id_pesme]
        else:
            favorites.append({'id_pesme': nowPlaying.id_pesme, "datum": date.today().strftime("%Y-%m-%d")})
        brojFav = len(list(filter(lambda x: x['id_pesme'] == nowPlaying.id_pesme, favorites)))
        list(filter(lambda x: x['id_pesme'] == nowPlaying.id_pesme, charts))[0]['broj_fav'] = brojFav
        print(charts)
        changeFav()

    def ucitajFav():
        global favorites
        res = json.loads(requestToServer(f'favorites#{ulogovan.id_korisnika}'))
        favorites = res

    def logout(*a):
        global ulogovan, b
        favorites.insert(0, ulogovan.id_korisnika)
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
            filter(lambda x: x.id_pesme in [x['id_pesme'] for x in favorites], pesme)) if varCheckFav.get() else pesme))

    chkFav.grid(row=0, column=0, pady=(10, 0))

    btnSort = Button(frameBtns1, text='Sort', bg='gold', font=font2)
    # btnSort.grid(row=0, column=1, padx=20, pady=(10, 0))

    frameBtns1.pack(side=BOTTOM, anchor=S)

    varListaPesama.set([str(x) for x in pesme])

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

    if ulogovan.status.lower() == 'admin':
        def ucitajObrisane():
            res = json.loads(requestToServer('obrisanepesme'))
            for i in res:
                obrisane.append(Pesma.from_json(json.dumps(i)))

        t = threading.Thread(target=ucitajObrisane)
        t.setDaemon(True)
        t.start()
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

            def currentPick(id, lista, tip):
                return list(filter(lambda x: (lista[x].id_autora if tip == Autor else lista[x]['id_zanra'])
                                             == id, [i for i in range(len(lista))]))[0]

            def popuniFormuPesme(e):
                btnObrisi['state'] = 'normal'
                obj = pesme[e.widget.curselection()[0]]
                btnChoseFile['text'] = obj.link.split("\\")[-1]
                varNazivPesme.set(obj.naziv)
                comboAutori.current(currentPick(obj.id_autora, autori, Autor))
                comboZanr.current(currentPick(obj.id_zanra, zanrovi, None))
                if obj.feat is not None and obj.feat != 0:
                    comboAutori.current(currentPick(obj.feat), autori, Autor)

            def dodajAutora(ime):
                global imenaAutora
                if str(ime).lower().replace(" ", "") in [str(x).lower().replace(" ", "") for x in imenaAutora]:
                    messagebox.showinfo("Dodavanje autora", "Postoji zapis autora")
                    return

                res = json.loads(requestToServer(f'writeAutor#{str(ime).lower().title()}'))
                boolDodajAutora = res[0]
                if boolDodajAutora:
                    a = Autor.from_json(json.dumps(res[1]))
                    autori.append(a)
                    imenaAutora.append(a.ime_autora)
                    comboAutori['values'] = imenaAutora
                    comboFeat['values'] = imenaAutora

                message = "Postoji zapis autoraa" if not boolDodajAutora else "Uspesno ste dodali autora"
                messagebox.showinfo("Dodavanje autora", message)

            def dodajZanr(zanr):
                global zanrovi
                if str(zanr).lower().replace(" ", "") in [str(x['naziv_zanra']).lower().replace(" ", "") for x in
                                                          zanrovi]:
                    messagebox.showinfo('Dodavanje zanra', 'Postoji zapis zanra')
                    return 0
                res = json.loads(requestToServer(f'writeZanr#{zanr}'))
                zanrovi.append(res[0])
                comboZanr['values'] = [x['naziv_zanra'] for x in zanrovi]
                messagebox.showinfo('Dodavanje zanra', 'Uspesno ste dodali zanr')

            def pesmaIzForme():
                id_a = list(
                    filter(lambda x: str(x.ime_autora).lower().strip() == str(comboAutori.get()).lower().strip(),
                           autori))[0].id_autora
                id_z = list(
                    filter(lambda x: str(x['naziv_zanra']).lower().strip() == str(comboZanr.get()).lower().strip(),
                           zanrovi))[0]['id_zanra']
                p = Pesma(0, id_a, varNazivPesme.get(), id_z, date.today().strftime("%Y-%m-%d"),
                          str(btnChoseFile['text']),
                          comboFeat.get() if varCheckFeat.get() else None, 0)
                return p

            def snimiPesmuAdmin():
                if not btnSnimi['text'].strip() or not entNaziv.get().strip():
                    messagebox.showinfo('Greska', 'Sva polja moraju biti popunjena')
                    return

                btnSnimi['state'] = 'disabled'
                message = 'Doslo je do greske prilikom snimanja'
                try:
                    m = pesmaIzForme()
                    if str(m) in [str(x) for x in pesme]:
                        message = 'Postoji zadata pesma'
                    else:
                        message = requestToServer(f'writeMuzika#{m.to_json()}').replace("[", "").replace("]", "")
                        pesme.append(m)
                        varListaPesama.set(list([str(x) for x in pesme]))

                except Exception as e:
                    print(e)
                    message = 'Greska: ' + str(e)
                finally:
                    btnSnimi['state'] = 'normal'
                    messagebox.showinfo('Snimanje pesme', message)

            def obrisiPesmuAdmin():
                btnObrisi['state'] = 'disabled'
                if not btnSnimi['text'].strip() or not entNaziv.get().strip():
                    messagebox.showinfo('Greska', 'Sva polja moraju biti popunjena')
                    return
                message = ""
                song = pesmaIzForme()
                p = list(filter(lambda s: str(s) == str(song), pesme))
                if len(p) > 0:
                    obrisane.append(p[0])
                    res = json.loads(requestToServer(f'deletePesma#{p[0].id_pesme}'))
                    pesme.clear()
                    for x in res:
                        pesme.append(Pesma.from_json(json.dumps(x)))
                        varListaPesama.set([str(i) for i in pesme])
                    message = 'Uspesno ste obrisali pesmu'
                else:
                    message = 'Ne postoji zadata pesma'

                messagebox.showinfo('Brisanje pesme', message)
                btnObrisi['state'] = 'normal'

            def korpa():
                def recoverSong():
                    curr = lboxObrisanihPesama.curselection()
                    if len(curr) > 0:
                        obj = list(filter(lambda x: str(x) == lboxObrisanihPesama.get(curr), obrisane))[0]
                        requestToServer(f'recover#{obj.id_pesme}')
                        obrisane.remove(obj)
                        varObrisanePesme.set([str(x) for x in obrisane])
                        pesme.append(obj)
                        varListaPesama.set([str(x) for x in pesme])
                        messagebox.showinfo('Recovery', 'Uspesno ste povratili pesmu')
                    else:
                        messagebox.showinfo('Recovery', 'Morate selektovati pesmu iz listboxa')

                tabKorpa = Frame(tabs, bg=pozadina, pady=50)
                Label(tabKorpa, text="Obrisane pesme", font=font1, bg=pozadina, fg=fgWhite).pack()
                varObrisanePesme = StringVar()
                lboxObrisanihPesama = Listbox(tabKorpa, font=font2, width=50, listvariable=varObrisanePesme)
                varObrisanePesme.set([str(x) for x in obrisane])
                lboxObrisanihPesama.pack()
                btnRecover = Button(tabKorpa, text='Recover', font=font2, padx=10,
                                    command=lambda: threading.Thread(target=recoverSong).start())
                btnRecover.pack()
                tabs.add(tabKorpa, text='Korpa')
                tabs.select(tabKorpa)

            # photoTrashcan = PhotoImage(file=r"img\back.png")
            btnTrascan = Button(tabPesme, activebackground=pozadina2, font=font2, bg=pozadina, bd=0, text='Korpa',
                                fg=fgWhite, command=korpa)
            btnTrascan.pack(anchor=E)
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

            framePesme = Frame(tabPesme, bg=pozadina2, pady=10, padx=5)
            varNazivPesme = StringVar()
            lblFile = Label(framePesme, text='File', font=font2, bg=pozadina2, fg=fgWhite)
            lblFile.grid(row=0, column=0)
            btnChoseFile = Button(framePesme, text='Choose file', command=chooseFile)
            btnChoseFile.grid(row=1, column=0)

            lblNaziv = Label(framePesme, text='Naziv pesme', font=font2, bg=pozadina2, fg=fgWhite)
            lblNaziv.grid(row=0, column=1)
            entNaziv = Entry(framePesme, textvariable=varNazivPesme, font=font3)
            entNaziv.grid(row=1, column=1)

            Label(framePesme, text='Zanr', font=font2, bg=pozadina2, fg=fgWhite).grid(row=0, column=2)
            comboZanr = Combobox(framePesme, values=[x['naziv_zanra'] for x in zanrovi], width=15, font=font3,
                                 state='readonly')
            comboZanr.grid(row=1, column=2)

            lblAutor = Label(framePesme, text='Autor', font=font2, bg=pozadina2, fg=fgWhite)
            lblAutor.grid(row=0, column=3)
            global imenaAutora
            imenaAutora = [str(x.ime_autora).title() for x in autori]
            comboAutori = Combobox(framePesme, values=imenaAutora, width=15, font=font3, state='readonly')
            comboAutori.grid(row=1, column=3)
            lblFeat = Label(framePesme, text='Feat.', font=font2, bg=pozadina2, fg=fgWhite)
            comboFeat = Combobox(framePesme, values=imenaAutora, width=15, font=font3, state='disabled')
            lblFeat.grid(row=0, column=4)
            comboFeat.grid(row=1, column=4, padx=10)

            comboZanr.current(0)
            comboFeat.current(0)
            comboAutori.current(0)

            varCheckFeat = IntVar()
            checkFeat = Checkbutton(framePesme, text='Feat', variable=varCheckFeat, onvalue=1, offvalue=0, font=font3,
                                    bg=pozadina2, bd=3, fg=fgWhite, selectcolor='black', command=featPrikaz)

            checkFeat.grid(row=2, column=3, sticky=NW)

            frameBtnAdminPesma = Frame(framePesme, bg=pozadina2)

            btnObrisi = Button(frameBtnAdminPesma, text='Obrisi', state='disabled', font=font2, padx=10,
                               command=lambda: threading.Thread(target=obrisiPesmuAdmin).start())
            btnObrisi.grid(row=0, column=0)

            btnSnimi = Button(frameBtnAdminPesma, text='Snimi', font=font2, padx=10,
                              command=lambda: threading.Thread(target=snimiPesmuAdmin).start())
            btnSnimi.grid(row=0, column=1, padx=5)
            frameBtnAdminPesma.grid(row=2, column=4, pady=20, sticky=SE)

            Label(framePesme, text='Dodaj autora', font=font2, bg=pozadina2, fg=fgWhite).grid(row=3, column=0)
            varDodajAutora = StringVar()
            Entry(framePesme, textvariable=varDodajAutora, font=font3).grid(row=4, column=0)
            Button(framePesme, text='Snimi autora', font=font2,
                   command=lambda: threading.Thread(target=dodajAutora,
                                                    args=(varDodajAutora.get(),)).start()).grid(row=4, column=1)
            Label(framePesme, text='Dodaj zanr', font=font2, bg=pozadina2, fg=fgWhite).grid(row=3, column=2)
            varDodajZanr = StringVar()
            Entry(framePesme, textvariable=varDodajZanr, font=font3).grid(row=4, column=2)
            Button(framePesme, text='Snimi zanr', font=font2,
                   command=lambda: threading.Thread(target=dodajZanr,
                                                    args=(varDodajZanr.get(),)).start()).grid(row=4, column=3)

            framePesme.pack(expand=True)

        def adminKorisnici():
            pass

        def adminCharts():
            def chart(e):
                global charts
                krug = C.create_oval(coord, fill="lightblue")
                pesma = list(filter(lambda x: str(x) == e.widget.get(ACTIVE), pesme))[0]
                chartZaPesmu = [x for x in charts if x['id_pesme'] == pesma.id_pesme][0]
                brOdslusanih = chartZaPesmu['broj_slusanja']
                brFav = chartZaPesmu['broj_fav']
                rez = 1 if brOdslusanih == 0 or brFav == 0 else (brFav / (
                    (brOdslusanih / (
                            brOdslusanih ** (len(str(brOdslusanih)) - 2))) if brOdslusanih != 0 else 0.1)) * 100
                procenat1 = 100 if rez > 100 else rez
                pomeraj = procenat1 * 3.6
                arc = C.create_arc(coord, fill='purple', start=90, extent=-pomeraj)

            lblCharts = Label(tabTopPesme, text="Najslusanije pesme", pady=20, font=font1, bg=pozadina, fg=fgWhite)
            lblCharts.pack()
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

            Label(frameCharts, text='Odnos najslusanijih/omiljenih(ljubicasto)\n pesama:', font=font2, bg=pozadina,
                  fg=fgWhite).grid(
                row=0, column=1, sticky=E)
            C = Canvas(frameCharts, bg=pozadina, bd=0, highlightthickness=0, relief='ridge', height=250, width=300)
            C.grid(row=1, column=1)
            coord = 60, 50, 240, 210
            krug = C.create_oval(coord, fill="lightblue")

            listaPesamaCharts.bind("<Double-Button>", chart)
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
        if ulogovan is not None and ulogovan.status != 'gost' and ulogovan.id_korisnika != -1:
            requestToServer(f"writeBrojSlusanja#{[{f'{str(x.id_pesme)}': x.broj_slusanja} for x in pesme]}")
            favorites.insert(0, ulogovan.id_korisnika)
            requestToServer(f"writeFav#{json.dumps(favorites)}")
    except Exception as e:
        print(e)


def containsNumber(string):
    return True in list(map(lambda x: str(x).isnumeric(), string))


login()
