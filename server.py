import json
from socket import socket, gethostname
from tkinter import *
import threading
from datetime import date
from duration import duration
import pymysql
import time


def server():
    lsBox.insert(0, "\n\nSERVER: started...", "\n\n")

    def posaljiResponse(lista):
        for o in range(len(lista)):
            conn.send((("" if o == 0 else ",") + json.dumps(lista[o])).encode())
        else:
            conn.send("#".encode())

    while True:
        try:
            conn, addr = sock.accept()
            lsBox.insert(0, "Got connection from", addr)
            req = conn.recv(1024).decode().lower().split("#")
            case = req[0]
            lsBox.insert(0, "-" * 100, "Request", case, "\n")
            if case == 'pesme':
                upitMuzika = "select muzika.id_muzike as id_muzike,naziv,ime_autora, date_format(datum_azuriranja,'%d/%m/%Y') as datum_azuriranja, link, imeAutora(IFNULL(feat,0)) as featuring, broj_slusanja " \
                             "from pesma " \
                             "inner join muzika " \
                             " on pesma.id_muzike=muzika.id_muzike " \
                             " inner join autor on " \
                             "autor.id_autora=muzika.id_autora "
                posaljiResponse(dohvati(upitMuzika))
            elif case == 'korisnici':
                upitKorisnici = "select * from korisnik"
                posaljiResponse(dohvati(upitKorisnici))
            elif case == 'favorites':
                upitFav = f'select id_muzike from favorites where id_osobe={req[1]}'
                conn.send(json.dumps(dohvati(upitFav)).encode())
            elif case == 'writefav':
                obj = json.loads(req[1])
                if len(obj) > 1:
                    cursor.execute(f'delete from favorites where id_osobe={obj[0]}')
                    db.commit()
                    for i in obj[1:]:
                        cursor.execute(
                            f'insert into favorites values (CURRENT_DATE(),{i},{obj[0]})')
                        db.commit()
                conn.send("#".encode())
            elif case == 'register':
                obj = json.loads(req[1])
                cursor.execute(
                    f'insert into korisnik '
                    f'values ((select max(id_osobe)+1 from (select * from korisnik) as m),"{obj["status"]}","{obj["username"]}","{obj["password"]}")')
                db.commit()
                posaljiResponse(dohvati("select * from korisnik order by id_osobe desc limit 1"))
            elif case == 'autori':
                posaljiResponse(dohvati("select * from autor"))
            elif case == 'writemuzika':
                obj = json.loads(req[1])
                cursor.execute(f"insert into pesma values (maxIdPesme()+1, \"{obj['naziv']}\") ")
                db.commit()
                cursor.execute(
                    f"insert into muzika values (maxIdPesme(),  (select id_autora from autor where ime_autora=\'{obj['ime_autora']}\'), CURRENT_DATE(), \"{obj['link']}\" , idAutora(\'{obj['featuring']}\'), {obj['broj_slusanja']})")
                db.commit()
                conn.send('#'.encode())
            elif case == 'writeautor':
                id_autora = "(select max(id_autora)+1 from (select * from autor) as t)"
                cursor.execute(f'insert into autor values ({id_autora},\"{str(req[1]).capitalize()}\")')
                db.commit()
                posaljiResponse(dohvati("select * from autor"))
            elif case == 'allfavorites':
                posaljiResponse(dohvati("SELECT DATE_FORMAT(datum, '%Y-%m-%d') as datum, id_muzike from favorites"))
            elif case == 'writebrojslusanja':
                obj = json.loads(req[1].replace("\'", "\""))
                for o in obj:
                    for i in o:
                        cursor.execute(f"update muzika set broj_slusanja={o[i]} where id_muzike={int(i)}")
                        db.commit()

                conn.send("#".encode())

        except Exception as ex:
            lsBox.insert(0, ex)
            fd.write(f'{date.today()} -> {ex}')

    conn.close()


def dohvati(upit):
    try:
        cursor.execute(upit)
        db.commit()
        data = cursor.fetchall()
        row_headers = [x[0] for x in cursor.description]
        json_data = []
        for result in data:
            json_data.append(dict(zip(row_headers, result)))
        return json_data
    except Exception as ex:
        if db is not None:
            db.rollback()
        greska = "Greska prilikom povezivanja sa bazom"
        lsBox.insert(0, greska)
        print(ex)
        fd.write(f'{date.today()} -> {greska}')
        return ""


db = None
cursor = None


def startUp():
    global db, cursor
    try:
        db = pymysql.connect(host="localhost", user="root", passwd="", port=3306, db="fp")
        cursor = db.cursor()
    except Exception as e:
        lsBox.insert(0, e)
        fd.write(f'{date.today()} -> {e}')


try:
    fd = open("error_log.txt", "a")
    sock = socket()
    host = gethostname()
    port = 1234
    sock.bind((host, port))
    sock.listen(5)

    root = Tk()
    lsBox = Listbox(root, selectmode=SINGLE, width=55, height=35)
    lsBox.pack(fill=BOTH, expand=TRUE)

    t = threading.Thread(target=server, name='ThreadServer')
    t.setDaemon(True)

    tStartUp = threading.Thread(target=startUp, name='ThreadStartUp')
    tStartUp.setDaemon(True)

    t.start()
    tStartUp.start()

    root.mainloop()

    if db is not None:
        db.close()
except Exception as e:
    print(e)
    fd.write(f'{date.today()} -> {e}')
    input("Press <Enter> to terminate")
finally:
    fd.close()
