import tkinter
import random
from itertools import product
import winsound
import logging
import argparse
import threading


VELIKOST_POLJA = 70
GLOBINA = 3
VELJAVNO = None
IGRALEC_1 = 1
IGRALEC_2 = 2
UNICENO = 0
ZACETNI_IGRALEC = IGRALEC_1
NEODLOCENO = None
PREMIK = True
UNICENJE = False

NAPIS_IGRALEC1_PREMIK = "Na potezi je MODRI igralec. Cas je da se premaknes."
NAPIS_IGRALEC2_PREMIK = "Na potezi je ZELENI igralec. Cas je da se premaknes."
NAPIS_IGRALEC1_UNICENJE = "Na potezi je MODRI igralec. Cas je da unicis polje."
NAPIS_IGRALEC2_UNICENJE = "Na potezi je ZELENI igralec. Cas je da unicis polje."

NAVODILA = """just kiding \n hahahah \n \n
Na polju 7*7 igralca postavita svojo figurico
na sredino nasprotnih robov. Igralca si izmenjujeta
poteze. V vsaki potezi se igralec najprej premakne
za eno polje(kot kralj pri šahu), nato odstrani
eno polje. Na polja, ki so že bila odstranjena
se ni dovoljeno premakniti. Cilj igre je odstraniti
ploščice tako, da se nasprotnik ne more več premakniti."""


def nasprotnik(igralec):
    #določi nasprotnika

    if igralec == IGRALEC_1:
        return IGRALEC_2
    else:
        return IGRALEC_1


######################################################    class Igra      #############################


class Igra():
    '''napisana je logika igre '''

    def __init__(self):
        self.polje = list([VELJAVNO]*7 for _ in range(7)) #mreza za shranjevanje veljavnih polj
        self.polje[0][3] = IGRALEC_1
        self.polje[6][3] = IGRALEC_2
        self.na_potezi = ZACETNI_IGRALEC
        self.zgodovina = []
        self.pozicija_1 = (0, 3)
        self.pozicija_2 = (6, 3)                #zacetna pozicija obeh igralcev
        self.del_poteze = PREMIK

    def shrani_pozicijo(self):
        p = [self.polje[i][:] for i in range(7)]
        self.zgodovina.append((p, self.na_potezi, self.pozicija_1, self.pozicija_2))
        #print(self.na_potezi)

    def kopija(self):
        """Vrni kopijo te igre, brez zgodovine."""
        # Kopijo igre naredimo, ko poženemo na njej algoritem.
        # Če bi algoritem poganjali kar na glavni igri, ki jo
        # uporablja GUI, potem bi GUI mislil, da se menja stanje
        # igre (kdo je na potezi, kdo je zmagal) medtem, ko bi
        # algoritem vlekel poteze
        k = Igra()
        k.polje = [self.polje[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.pozicija_1 = self.pozicija_1
        k.pozicija_2 = self.pozicija_2
        k.del_poteze = self.del_poteze
        # k.zgodovina = self.zgodovina
        return k

    def razveljavi(self):
        #print(self.na_potezi)
        (self.polje, self.na_potezi, self.pozicija_1, self.pozicija_2) = self.zgodovina.pop()


    def je_veljavna(self, i, j):
        return (self.polje[i][j] == VELJAVNO)

    def je_konec(self):
        if self.porazenec() != None:
            return True
        else:
            return False

    def pozicija_na_potezi(self):
        ''' vrne par koordinate igralca na potezi'''

        if self.na_potezi == IGRALEC_1:
            return self.pozicija_1
        else:
            return self.pozicija_2

    def pozicija_nasprotnik(self):
        if self.na_potezi == IGRALEC_2:
            return self.pozicija_1
        else:
            return self.pozicija_2


    def veljavne_poteze_premik(self, nasprotnik = False ):
        ''' preveri vsa polja okoli igralca na potezi in vrne seznam polj na katere se lahko premakne'''

        poteze = []
        if not nasprotnik:
            (a, b) = self.pozicija_na_potezi()
        else:
            (a, b) = self.pozicija_nasprotnik()
        for i in range(3):
            for j in range(3):
                c = a - 1 + i
                d = b - 1 + j
                if c >= 0 and c <= 6 and d >= 0 and d <= 6 and self.je_veljavna(c, d):
                    poteze.append((c, d))
        return poteze

    def veljavne_poteze_unici(self):
        '''vrne seznam vseh polj, ki jih lahko uničimo'''
        poteze = []
        for i in range(7):
            for j in range(7):
                if self.je_veljavna(i, j):
                    poteze.append((i, j))
        return poteze

    def naredi_pravo_potezo(self, i, j):
        if self.del_poteze == PREMIK:
            self.premik(i, j)
            #print(self.zgodovina)
        else:
            self.unici(i, j)
            #print(self.zgodovina)
    def premik(self, i, j):
        '''premaknemo se na veljavno polje, staro polje naredimo spet veljavno, zapišemo pozicijo igralca, zamenjamo del poteze'''

        if (i, j) in self.veljavne_poteze_premik():
            self.shrani_pozicijo()
            self.polje[i][j] = self.na_potezi
            (c, d) = self.pozicija_na_potezi()
            self.polje[c][d] = VELJAVNO
            if self.na_potezi == IGRALEC_1:
                self.pozicija_1 = (i, j)
            else:
                self.pozicija_2 = (i, j)
            self.del_poteze = UNICENJE

    def unici(self, i, j):
        '''uniči veljavno polje, spremeni del poteze, zamenja igralca'''

        if (i, j) in self.veljavne_poteze_unici():
            self.shrani_pozicijo()
            self.polje[i][j] = UNICENO
            self.del_poteze = PREMIK
            self.na_potezi = nasprotnik(self.na_potezi)

    def zmagovalec(self):
        pass

    def porazenec(self):
        if len(self.veljavne_poteze_premik()) == 0:
            return self.na_potezi


####################################################       človek        #####################


class Clovek():
    '''igralec, ki ga upravlja človek'''

    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        self.gui.plosca.bind('<Button-1>', self.klik)

    def klik(self, event):
        '''shrani koordinate polja kamor kliknemo'''

        i = int(event.x / self.gui.velikost_polja)
        j = int(event.y / self.gui.velikost_polja)
        self.gui.povleci_potezo(i, j)


#########################################################     racunalnik    #############################

class Racunalnik():
    '''Igralec, ki ga upravlja racunalnik'''

    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem
        self.mislec = None

    def igraj(self):
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.gui.igra.kopija()))

        self.mislec.start()

        self.gui.plosca.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        if self.algoritem.poteza is not None:
            # Algoritem je našel potezo, povleci jo, če ni bilo prekinitve
            i, j = self.algoritem.poteza
            self.gui.povleci_potezo(i , j)
            # Vzporedno vlakno ni več aktivno, zato ga "pozabimo"
            self.mislec = None
        else:
            # Algoritem še ni našel poteze, preveri še enkrat čez 100ms
            self.gui.plosca.after(100, self.preveri_potezo)

    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        if self.mislec:
            logging.debug ("Prekinjamo {0}".format(self.mislec))
            # Algoritmu sporočimo, da mora nehati z razmišljanjem
            self.algoritem.prekini()
            # Počakamo, da se vlakno ustavi
            self.mislec.join()
            self.mislec = None

    def klik(self):
        pass

#################################################       Algoritem minimax       ###################

class Minimax():
    # Algoritem minimax predstavimo z objektom, ki hrani stanje igre in
    # algoritma, nima pa dostopa do GUI (ker ga ne sme uporabljati, saj deluje
    # v drugem vlaknu kot tkinter).
    def __init__(self, globina = GLOBINA):
        self.globina = globina  # do katere globine iščemo?
        self.prekinitev = False # ali moramo končati?
        self.igra_kopija = None # objekt, ki opisuje igro (ga dobimo kasneje)
        self.jaz = None  # katerega igralca igramo (podatek dobimo kasneje)
        self.poteza = None # sem napišemo potezo, ko jo najdemo

    def prekini(self):
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True


    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        # To metodo pokličemo iz vzporednega vlakna
        self.igra_kopija = igra
        self.prekinitev = False # Glavno vlakno bo to nastvilo na True, če moramo nehati
        self.jaz = self.igra_kopija.na_potezi
        self.poteza = None # Sem napišemo potezo, ko jo najdemo
        # Poženemo minimax
        (poteza, vrednost) = self.minimax(self.globina, True)
        self.jaz = None
        self.igra_kopija = None
        if not self.prekinitev:
            # Potezo izvedemo v primeru, da nismo bili prekinjeni
            logging.debug("minimax: poteza {0}, vrednost {1}".format(poteza, vrednost))
            self.poteza = poteza

    ZMAGA = 100000 # Mora biti vsaj 10^5
    NESKONCNO = ZMAGA + 1 # Več kot zmaga



    def vrednost_pozicije_premik(self, i, j):
        return 100

    def vrednost_pozicije_unici(self, i, j):
        return 100



    def minimax(self, globina, maksimiziramo):
        if self.prekinitev:
             # Sporočili so nam, da moramo prekiniti
             logging.debug ("Minimax prekinja, globina = {0}".format(globina))
             return (None, 0)
        if self.igra_kopija.del_poteze == PREMIK:
            return self.premik_minimax(globina, maksimiziramo)
        else:
            return self.unici_minimax(globina, maksimiziramo)

    def premik_minimax(self, globina, maksimiziramo):
        (i, j) = self.igra_kopija.pozicija_na_potezi()
        if globina == 0:
            return ((i,j), self.vrednost_pozicije_premik(i, j))
        else:
            if maksimiziramo:
                # Maksimiziramo
                najboljsa_poteza = None
                vrednost_najboljse = -Minimax.NESKONCNO
                for (a, b) in self.igra_kopija.veljavne_poteze_premik():
                    self.igra_kopija.naredi_pravo_potezo(a, b)
                    (p,vrednost) = self.minimax(globina-1, not maksimiziramo)
                    if self.igra_kopija.zgodovina != []:
                        self.igra_kopija.razveljavi()
                    if vrednost > vrednost_najboljse:
                        vrednost_najboljse = vrednost
                        najboljsa_poteza = p
                return (najboljsa_poteza, vrednost_najboljse)
            else:
                najboljsa_poteza = None
                vrednost_najboljse = Minimax.NESKONCNO
                for (a, b) in self.igra_kopija.veljavne_poteze_premik():
                    self.igra_kopija.naredi_pravo_potezo(a, b)
                    (p,vrednost) = self.minimax(globina-1, not maksimiziramo)
                    if self.igra_kopija.zgodovina != []:
                        self.igra_kopija.razveljavi()
                    if vrednost < vrednost_najboljse:
                        vrednost_najboljse = vrednost
                        najboljsa_poteza = p
                return (najboljsa_poteza, vrednost_najboljse)



    def unici_minimax(self, globina, maksimiziramo):
        (i, j) = self.igra_kopija.pozicija_na_potezi()
        if globina == 0:
            return ((i,j), self.vrednost_pozicije_unici(i, j))
        else:
            if maksimiziramo:
                # Maksimiziramo
                najboljsa_poteza = None
                vrednost_najboljse = -Minimax.NESKONCNO
                for (a, b) in self.igra_kopija.veljavne_poteze_unici():
                    self.igra_kopija.naredi_pravo_potezo(a, b)
                    (p,vrednost) = self.minimax(globina-1, not maksimiziramo)
                    if self.igra_kopija.zgodovina != []:
                        self.igra_kopija.razveljavi()
                    if vrednost > vrednost_najboljse:
                        vrednost_najboljse = vrednost
                        najboljsa_poteza = p
                return (najboljsa_poteza, vrednost_najboljse)
            else:
                najboljsa_poteza = None
                vrednost_najboljse = Minimax.NESKONCNO
                for (a, b) in self.igra_kopija.veljavne_poteze_unici():
                    self.igra_kopija.naredi_pravo_potezo(a, b)
                    (p,vrednost) = self.minimax(globina-1, not maksimiziramo)
                    if self.igra_kopija.zgodovina != []:
                        self.igra_kopija.razveljavi()
                    if vrednost < vrednost_najboljse:
                        vrednost_najboljse = vrednost
                        najboljsa_poteza = p
                return (najboljsa_poteza, vrednost_najboljse)

    # def minimax(self, globina, maksimiziramo):
    #     if self.prekinitev:
    #         # Sporočili so nam, da moramo prekiniti
    #         logging.debug ("Minimax prekinja, globina = {0}".format(globina))
    #         return (None, 0)
    #     if globina == 0:
    #             return (None, self.vrednost_pozicije())
    #     else:
    #         # Naredimo eno stopnjo minimax
    #         if maksimiziramo:
    #             # Maksimiziramo
    #             najboljsa_poteza = None
    #             vrednost_najboljse = -Minimax.NESKONCNO
    #             for p in self.igra_kopija.veljavne_poteze():
    #                 self.igra_kopija.povleci_potezo(p)
    #                 vrednost = self.minimax(globina-1, not maksimiziramo)[1]
    #                 self.igra_kopija.razveljavi()
    #                 if vrednost > vrednost_najboljse:
    #                     vrednost_najboljse = vrednost
    #                     najboljsa_poteza = p
    #         else:
    #             # Minimiziramo
    #             najboljsa_poteza = None
    #             vrednost_najboljse = Minimax.NESKONCNO
    #             for p in self.igra_kopija.veljavne_poteze():
    #                 self.igra_kopija.povleci_potezo(p)
    #                 vrednost = self.minimax(globina-1, not maksimiziramo)[1]
    #                 self.igra_kopija.razveljavi()
    #                 if vrednost < vrednost_najboljse:
    #                     vrednost_najboljse = vrednost
    #                     najboljsa_poteza = p
    #         return (najboljsa_poteza, vrednost_najboljse)





#########################################################     class Gui     ################################

class Gui():
    '''graficni vmesnik'''

    def __init__(self, master, velikost, globina = GLOBINA):
        self.napis = tkinter.StringVar()
        self.napis.set(NAPIS_IGRALEC1_PREMIK)
        #self.napis = tkinter.StringVar(master, value=NAPIS_IGRALEC1)
        tkinter.Label(master, textvariable=self.napis).grid(row=0, column=0, columnspan = 4)

        self.velikost_polja = velikost
        self.velikost_plosce = self.velikost_polja * 7          #dolocimo velikost celotnega polja in posameznih celic


        self.plosca = tkinter.Canvas(master, width=self.velikost_plosce, height=self.velikost_plosce)       #pripravimo platno
        self.plosca.grid(row=1, column=0, columnspan = 4)

        self.kvadratki = self.narisi_kvadratke()

        self.izbira_igralcev()
        self.globina = globina



    def izbira_igralcev(self):
        self.igralec_1 = Clovek(self)
        #self.igralec_2 = Clovek(self)
        self.igralec_2 = Racunalnik(self, Minimax(GLOBINA))
        self.zacni_igro()

    def zacni_igro(self):
        '''Nastavi stanje igre na zacetek igre.'''

        self.igra = Igra()
        (a1, b1) = self.igra.pozicija_1
        (a2, b2) = self.igra.pozicija_2
        self.narisi_igralca(a1, b1, "blue")
        self.narisi_igralca(a2, b2, "green")
        self.igralec_1.igraj()              #sprement v random

    def koncaj_igro(self):
        '''Nastavi stanje igre na konec igre.'''

        print ("KONEC!")

    def povleci_potezo(self, i, j):
        '''celoten potek poteze'''

        if self.igra.del_poteze:    #če je del poteze nastavljen na PREMIK
            if (i, j) in self.igra.veljavne_poteze_premik():
                self.narisi_premik(i, j)
                self.igra.naredi_pravo_potezo(i, j)
                self.spremeni_napis()

            else:
               # print("napacna poteza")
                if self.igra.na_potezi == IGRALEC_1:
                    self.igralec_1.igraj()
                else:
                    self.igralec_2.igraj()
        else:                                   #če je del poteze nastavljen na UNIČENJE
            if (i, j) in self.igra.veljavne_poteze_unici():
                self.narisi_uniceno(i, j)
                self.igra.naredi_pravo_potezo(i, j)
                self.spremeni_napis()

            else:
               # print("napacna poteza")
                if self.igra.na_potezi == IGRALEC_1:
                    self.igralec_1.igraj()
                else:
                    self.igralec_2.igraj()

        if self.igra.je_konec():
                self.koncaj_igro()
        else:
            if self.igra.na_potezi == IGRALEC_1:
                self.igralec_1.igraj()
            else:
                self.igralec_2.igraj()






    def narisi_uniceno(self, i, j):
        self.plosca.create_rectangle(i * self.velikost_polja, j * self.velikost_polja, (i + 1) * self.velikost_polja, (j + 1) * self.velikost_polja, fill="red", outline="black")


    def narisi_premik(self, i, j):
        '''premakne igralca, ki je na potezi na izbrano polje'''
        self.narisi_veljavno()
        self.narisi_igralca(i, j)

    def narisi_igralca(self, i, j, barva = None):
        '''na izbrano polje nariše igralca'''

        if barva == None:
            if self.igra.na_potezi == IGRALEC_1:
                barva = "blue"
            else:
                barva = "green"
        self.plosca.create_oval(i * self.velikost_polja, j * self.velikost_polja, (i + 1) * self.velikost_polja, (j + 1) * self.velikost_polja, fill=barva, outline="black")


    def narisi_veljavno(self, a = None, b = None):
        '''polje nariše spet veljavno, brez argumentov ga nariše kjer je igralec na potezi'''

        if a == None and b == None:
            (a,b) = self.igra.pozicija_na_potezi()
        self.plosca.create_rectangle(a * self.velikost_polja, b * self.velikost_polja, (a + 1) * self.velikost_polja, (b + 1) * self.velikost_polja, fill="white", outline="black")

    def narisi_kvadratke(self):
        '''narise polje ob zacetku igre'''

        for (i, j) in product(range(7), range(7)):
            coordX1 = (i * self.velikost_polja)
            coordY1 = (j * self.velikost_polja)
            coordX2 = coordX1 + self.velikost_polja
            coordY2 = coordY1 + self.velikost_polja
            color = "white" #if i%2 == j%2 else "black"
            self.plosca.create_rectangle(coordX1, coordY1, coordX2, coordY2, fill = color, outline = "black")


    def spremeni_napis(self, napis = None):
        if napis == None:

            if self.igra.na_potezi == IGRALEC_1:
                if self.igra.del_poteze:
                    self.napis.set(NAPIS_IGRALEC1_PREMIK)
                else:
                    self.napis.set(NAPIS_IGRALEC1_UNICENJE)
            else:
                if self.igra.del_poteze:
                    self.napis.set(NAPIS_IGRALEC2_PREMIK)
                else:
                    self.napis.set(NAPIS_IGRALEC2_UNICENJE)
        else:
            self.napis.set(napis)

#########################################################    class Meni    ##################################


class Meni():
    '''meni'''

    def __init__(self, master, velikost_polja):
        self.master = master
        self.velikost_polja = velikost_polja

        #winsound.PlaySound("files\\two.wav", winsound.SND_ASYNC|winsound.SND_LOOP)

        self.napis = tkinter.StringVar(master, value="Isola!")
        tkinter.Label(master, textvariable=self.napis).grid(row=0, column=0, columnspan = 4)

        #gumb play
        master.slika_play = slika_play = tkinter.PhotoImage(file="files\play.png")
        self.gumb_play = tkinter.Button(master, command = self.play, image = slika_play)
        self.gumb_play.grid(row=2, column=0)

        #gumb options
        master.slika_options = slika_options = tkinter.PhotoImage(file="files\options.png")
        self.gumb_options = tkinter.Button(master, command = self.options, image = slika_options)
        self.gumb_options.grid(row=2, column=1)

        #gumb help
        master.slika_help = slika_help = tkinter.PhotoImage(file="files\help.png")
        self.gumb_help = tkinter.Button(master, command = self.help, image = slika_help)
        self.gumb_help.grid(row=2, column=2)

        #gumb close
        master.slika_close = slika_close = tkinter.PhotoImage(file="files\close.png")
        self.gumb_close = tkinter.Button(master, command = self.close, image = slika_close)
        self.gumb_close.grid(row=2, column=3)

        #naredi igralno ploščo
        self.play()


    def play(self, event = None):
        self.aplication2 = Gui(root, self.velikost_polja, 1)
        #sam da vidm kva se zgodi pr manši globini

    def options(self):
        print("options")
        pass

    def help(self):
        napis_help = "NAVODILA"
        navodila = NAVODILA

        self.aplication2.spremeni_napis(napis_help)

        self.velikost_plosce = 7 * self.velikost_polja
        self.plosca = tkinter.Canvas(self.master, width=self.velikost_plosce, height=self.velikost_plosce)
        self.plosca.grid(row=1, column=0, columnspan = 4)
        self.plosca.create_text(self.velikost_plosce/2, self.velikost_polja*5, text = navodila)

        print("help")
        pass

    def close(self):
        root.destroy()

if __name__ == "__main__":
    # Naredimo glavno okno in nastavimo ime
    root = tkinter.Tk()
    root.title("Isola")
    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    # sicer bo Python mislil, da je objekt neuporabljen in ga bo pobrisal
    # iz pomnilnika.
    aplication1 = Meni(root, VELIKOST_POLJA)
    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()
