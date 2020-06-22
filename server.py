import json
from socket import socket, gethostname
from tkinter import *
import threading
from datetime import date, datetime
from duration import duration
import pyodbc
import time
import cv2


def server():
    lsBox.insert(0, "\n\nSERVER: started...", "\n\n")

    def posaljiResponse(lista):
        for o in range(len(lista)):
            conn.send((("" if o == 0 else ",") + json.dumps(lista[o])).encode())
        else:
            conn.send("#".encode())

    while True:
        try:
            sock = socket()
            host = gethostname()
            port = 1234
            sock.bind((host, port))
            sock.listen(5)
            conn, addr = sock.accept()
            lsBox.insert(0, "Got connection from", addr)
            req = conn.recv(1024).decode().split("#")
            case = req[0].lower()
            lsBox.insert(0, "-" * 100, "Request", case, "\n")
            if case == 'pesme':
                upitMuzika = "select id_pesme, id_autora, id_zanra, naziv, feat, " \
                             "convert(varchar, datum_azuriranja, 23) as datum_azuriranja, link, broj_slusanja  from pesma"
                posaljiResponse(dohvati(upitMuzika))
            elif case == 'korisnici':
                upitKorisnici = "select id_korisnika, username, password, (select status from Status where Status.id_statusa=Korisnik.id_statusa) as status, email from korisnik"
                posaljiResponse(dohvati(upitKorisnici))
            elif case == 'favorites':
                upitFav = f'select id_pesme, convert(varchar, datum, 23) as datum from favorites where id_korisnika={req[1]}'
                posaljiResponse(dohvati(upitFav))
            elif case == 'zanrovi':
                posaljiResponse(dohvati('select * from zanr'))
            elif case == 'writefav':
                obj = json.loads(req[1])
                fav = dohvati(
                    f'select id_pesme, convert(varchar, datum, 23) as datum from favorites where id_korisnika={obj[0]}')
                listaZaUpis = list(set([x['id_pesme'] for x in fav]) ^ set([x['id_pesme'] for x in obj[1:]]))
                if len(listaZaUpis) > 0:
                    for o in listaZaUpis:
                        cursor.execute(f"exec sp_UpisFavorites {obj[0]}, {o}")
                        db.commit()
                conn.send("#".encode())
            elif case == 'register':
                obj = json.loads(req[1])
                email = f"'{obj['email']}'"
                cursor.execute(
                    f'insert into korisnik (username, password, status, email) '
                    f"values ('{obj['username']}','{obj['password']}', '{obj['status']}', {'null' if obj['email'] is None else email})")
                db.commit()

                posaljiResponse(dohvati("select top 1 * from korisnik order by id_korisnika desc"))
            elif case == 'autori':
                posaljiResponse(dohvati("select * from autor"))
            elif case == 'zanrovi':
                posaljiResponse(dohvati("select id_zanra, TRIM(naziv_zanra) as naziv_zanra from zanr"))
            elif case == 'writemuzika':
                obj = json.loads(req[1])
                feat = obj['feat']
                naziv = str(obj['naziv']).replace("'", "''").capitalize()
                link = obj['link'].replace("'", "''")
                data = cursor.execute(
                    f"declare @res int "
                    f"exec @res=sp_UpisPesme {obj['id_autora']}, {obj['id_zanra']}, '{naziv}', '{obj['datum_azuriranja']}', '{link}', {'null' if obj['feat'] is None else feat} "
                    f"select @res")
                poruka = data.fetchone()[0]
                db.commit()
                conn.send(f'{poruka}'.encode())
                conn.send('#'.encode())
            elif case == "deletepesma":
                cursor.execute(f'delete from pesma where id_pesme={req[1]}')
                db.commit()
                upitPesma = "select id_pesme, id_autora, id_zanra, naziv, feat, " \
                            "convert(varchar, datum_azuriranja, 23) as datum_azuriranja, link, broj_slusanja  from pesma"
                posaljiResponse(dohvati(upitPesma))
            elif case == 'writeautor':
                data = cursor.execute(
                    f"declare @res int "
                    f"exec @res=sp_UpisAutora N'{req[1]}'"
                    f"select @res")
                res = data.fetchone()[0]
                db.commit()
                conn.send(f'{res},'.encode())
                conn.send(json.dumps(dohvati("select * from autor")).encode())
                conn.send('#'.encode())
            elif case == 'writezanr':
                zanr = req[1].title()
                cursor.execute(f"insert into Zanr (naziv_zanra) values (N'{zanr}')")
                db.commit()
                posaljiResponse(
                    dohvati(f"select id_zanra, TRIM(naziv_zanra) as naziv_zanra from zanr where naziv_zanra='{zanr}'"))
            elif case == 'charts':
                posaljiResponse(dohvati('select * from View_Charts'))
            elif case == 'writebrojslusanja':
                obj = json.loads(req[1].replace("\'", "\""))
                for o in obj:
                    for i in o:
                        cursor.execute(f"update pesma set broj_slusanja={o[i]} where id_pesme={int(i)}")
                        db.commit()

                conn.send("#".encode())
            elif case == 'obrisanepesme':
                upitKorpa = "select id_pesme, id_autora, id_zanra, naziv, feat, " \
                            "convert(varchar, datum_azuriranja, 23) as datum_azuriranja, link, broj_slusanja  from IzbrisanePesme"
                posaljiResponse(dohvati(upitKorpa))
            elif case == 'recover':
                cursor.execute(
                               'set identity_insert pesma on '
                               'insert into pesma (id_autora, id_zanra, id_pesme, naziv, feat, datum_azuriranja, link, broj_slusanja) '
                               f'select * from IzbrisanePesme where id_pesme={req[1]} '
                               f'update pesma set datum_azuriranja=GETDATE(), broj_slusanja=null where id_pesme={req[1]} '
                               f'delete from IzbrisanePesme where id_pesme={req[1]} ')
                db.commit()
                posaljiResponse([])
            sock.close()

        except Exception as ex:
            lsBox.insert(0, ex)
            fd.write(f'{date.today()} -> {ex}')

    conn.close()


def CallStoredProc(conn, procName, *args):
    sql = """DECLARE @ret int
             EXEC @ret = %s %s
             SELECT @ret""" % (procName, ','.join(['?'] * len(args)))
    a = int(conn.execute(sql, args).fetchone()[0])
    db.commit()
    return a


def dohvati(upit):
    try:
        cursor.execute(upit)
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
serverName = f"{gethostname()}\\SQLEXPRESS01"
database = "Music_player"


def startUp():
    global db, cursor
    try:
        db = pyodbc.connect(driver='{SQL Server}', host=serverName, database=database,
                            trusted_connection='yes')
        cursor = db.cursor()

    except Exception as e:
        lsBox.insert(0, e)
        fd.write(f'{date.today()} -> {e}')


try:
    fd = open("error_log.txt", "a")

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
