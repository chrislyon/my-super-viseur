# -*- coding: utf-8 -*-

## --------------
## Super Viseur
## --------------

"""
 Super Viseur
 Pour superviser des objets comme des fichiers, des repertoires
"""

import datetime
import time
import os, sys
import shlex
import traceback
import glob
import Parse_Ligne as P
import pudb

## ---------------
## Exceptions
## ---------------
class SV_ParseError(Exception):
    """
        Erreur de parsing : transmets la ligne + le contenu de la ligne
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

### ----------
### OBJETS 
### ----------
class SV_Object(object):
    """
    Class Object de base 
    """
    def __init__(self):
        self.nom = ""
        self.typ = None

    def get_key(self):
        """
            Renvoi une cle pour l'objet
        """
        return "%s:%s" % (self.typ, self.nom)

    def __str__(self):
        return "%s:%s" % (self.typ, self.nom)

class SV_File(SV_Object):
    """
        Class Fichier
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'FILE'
        self.path = path

    def __str__(self):
        return "%s:%s:%s" % (self.typ, self.nom, self.path)

class SV_LogFile(SV_Object):
    """
        Class Fichier de log
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'LOGFILE'
        self.path = path

    def __str__(self):
        return "%s:%s:%s" % (self.typ, self.nom, self.path)

class SV_Directory(SV_Object):
    """
        Classe Répertoire
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'DIRECTORY'
        self.path = path
    def __str__(self):
        return "%s:%s:%s" % (self.typ, self.nom, self.path)

class SV_Program(SV_Object):
    """
        Class Programme 
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'PROGRAM'
        self.path = path
    def __str__(self):
        return "%s:%s:%s" % (self.typ, self.nom, self.path)

class SV_Host(SV_Object):
    """
        Class Host 
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'HOST'

class SV_Group(SV_Object):
    """
        Class GROUP
        Groupe d'adresse mail
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'GROUP'
        self.adr = []
    def __str__(self):
        return "%s:%s:%s" % (self.typ, self.nom, self.adr)

class SV_Message(SV_Object):
    """
        Class Message
        Type de message
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'MESSAGE'
        self.cible = None
        self.source = None
        self.sujet = None
        self.corps = None
    def __str__(self):
        return "%s:%s:%s:%s:%s:%s" % (self.typ, self.nom, self.cible, self.source, self.sujet, self.corps)

class SV_Alert(SV_Object):
    """
        Class Alert
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'ALERTE'
        self.group = None
        self.message = None

class SV_Service(SV_Object):
    """
        Class Service
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'SERVICE'
        self.start = None
        self.stop = None
        self.check = {}
    def __str__(self):
        return "%s:%s:%s:%s" % (self.typ, self.nom, self.start, self.stop)


### --------------
### SUPERVISEUR
### --------------
class Superviseur(object):
    """
        La classe superviseur : qui regule tout
    """
    def __init__(self):
        self.name = "Superviseur"
        self.sleep = 0
        self.obj = {}
        self.service = {}
        self.conf_file = "main.conf"
        self.conf_dir = 'conf.d'
        self.run_ok = False
        self.log_file = None
        self.stop_running = False
        self.verbose = True

    def init(self):
        """
            Initialisation du superviseur
        """
        self.log_file = open("default.log","w")
        
    def add_obj(self, obj):
        """
            Ajout d'un objet dans la liste
        """
        self.obj[ obj.get_key() ] = obj

    def add_service(self, obj):
        """
            Ajout d'un service dans la liste
        """
        self.service[ obj.get_key() ] = obj

    def log(self, msg):
        """
            Ecrit dans le journal principal
        """
        ts = datetime.datetime.now()
        l = "%s : %s" % (ts.strftime("%j %X"), msg)
        self.log_file.write(l+'\n')
        if self.verbose:
            print l
        
    def parse(self, ligs):
        """
            -------------------------------
            Parsing d'un groupe coherent
            -------------------------------
        """
        curr_obj = None
        body_mode = False
        for li in ligs:
            self.log( "\t> %s : %s " % (li.numlig, li.ligne))
            ## Mode "body" on prend c'est tout
            ## Sinon on parse
            lexer = shlex.shlex(li.ligne)
            cmd = lexer.next()
            self.log( "Commande : %s " % cmd)
            ## Mode body on rcupere c'est tout
            if body_mode and curr_obj and not 'BODY END' in cmd:
                curr_obj.corps.append( li.ligne )
                continue
            ## Si c'est une suite de commande
            if li.suite:
                if curr_obj.typ == 'MESSAGE':
                    if cmd in ('FROM', 'TO', 'SUBJECT', 'BODY'):
                        try:
                            data = lexer.next()
                            if cmd == 'FROM':
                                curr_obj.source = data
                            elif cmd == 'TO':
                                curr_obj.cible = data
                            elif cmd == 'SUBJECT':
                                curr_obj.sujet = data
                            elif cmd == 'BODY':
                                if data == 'BEGIN':
                                    curr_obj.corps = []
                                    body_mode = True
                                elif data == 'END':
                                    body_mode = False
                            else:
                                raise SV_ParseError(li)
                        except:
                            raise SV_ParseError(li)
                        continue
                elif curr_obj.typ == 'GROUP':
                    if cmd == 'ADD':
                        try:
                            adr = list(lexer)
                            curr_obj.adr.append(''.join(adr))
                        except:
                            raise SV_ParseError(li)
                elif curr_obj.typ == 'SERVICE':
                    if cmd == 'START':
                        try:
                            prog = lexer.next()
                            curr_obj.start = prog
                        except:
                            raise SV_ParseError(li)
                    elif cmd == 'STOP':
                        try:
                            prog = lexer.next()
                            curr_obj.stop = prog
                        except:
                            raise SV_ParseError(li)
                    else:
                        raise SV_ParseError(li)
                else:
                    raise SV_ParseError(li)
                continue
            else:
                curr_obj = None
            ## Sinon c'est un commande de base
            if cmd == 'SET':
                obj = lexer.next()
                if obj in ('FILE', 'DIRECTORY', 'PROGRAM', 'LOG_FILE'):
                    try:
                        name = lexer.next()
                        cmd_path = lexer.next()
                        if cmd_path != 'PATH':
                            raise SV_ParseError(li)
                        path = ''.join(list(lexer))
                    except:
                        raise SV_ParseError(li)
                    ## Si j'arrive ici c'est que la syntaxe est bonne
                    if obj == 'FILE':
                        self.add_obj( SV_File(name, path))
                    elif obj == 'DIRECTORY':
                        self.add_obj( SV_Directory(name, path))
                    elif obj == 'PROGRAM':
                        self.add_obj( SV_Program(name, path))
                    elif obj == 'LOG_FILE':
                        self.add_obj( SV_LogFile(name, path))
                    else:
                        raise SV_ParseError(li)
                elif obj == 'HOST':
                    try:
                        name = lexer.next()
                        self.add_obj( SV_Host(name) )
                    except:
                        raise SV_ParseError(li)
                elif obj in ( 'GROUP', 'MESSAGE'):
                    try:
                        name = lexer.next()
                    except:
                        raise SV_ParseError(li)
                    if obj == 'GROUP':
                        curr_obj = SV_Group(name)
                        self.add_obj( curr_obj )
                    if obj == 'MESSAGE':
                        curr_obj = SV_Message(name)
                        self.add_obj( curr_obj )
                else:
                    self.log( "\t\t%s : %s " % (obj, lexer.next() ))
            elif cmd == 'SERVICE':
                try:
                    name = lexer.next()
                    curr_obj = SV_Service(name)
                    self.add_service( curr_obj )
                except:
                    raise SV_ParseError(li)
            else:
                self.log( "CMD : %s non reconnu" % cmd )

    def parse_lines(self, lines):
        """
        ------------------------------
        Parsing d'un groupe de lignes
        ------------------------------
        """
        ll = []
        for li in lines:
            ## Si cela commence par une suite
            if li.ligne.startswith(('\t', ' ')):
                li.suite = True
                ll.append(li)
                continue
            else:
                if ll:
                    try:
                        self.parse(ll)
                    except SV_ParseError as e:
                        self.log(" Parse Error ligne %s " % e.value)
                        self.run_ok = False
                    except:
                        e = sys.exc_info()[0]
                        self.log(" TraceBack : ")
                        traceback.print_exc(file=self.log_file)
                        traceback.print_exc(file=sys.stdout)
                        self.run_ok = False
                    ll = []
                ll.append(li)

    def load_file(self, fichier):
        """
            Chargement d'un fichier et parsing
        """
        with open(fichier) as f:
            nol = 0
            ll = []
            for l in f.readlines():
                nol += 1
                l = l.rstrip()
                if l.startswith('#'):
                    continue
                if l:
                    ll.append( P.Ligne( nol, l) )
        self.parse_lines(ll)

    def load_config(self):
        """
            ---------------------------------------
            Chargement de la configuration
            on commence par conf_dir / main.conf
            puis par tout les autres fichiers
            ---------------------------------------
        """
        self.log("start load config %s " % self.conf_dir)
        self.run_ok = True
        ## d'abord on traite le main.conf
        main_conf = os.path.join(self.conf_dir, self.conf_file)
        if os.path.exists(main_conf):
            self.log("**** Parsing main : %s " % main_conf)
            self.load_file(main_conf)
        else:
            self.log("Fichier config %s inexistant" % main_conf)
            self.run_ok = False
        ## Ensuite les fichiers dans conf.d
        if self.run_ok:
            for f in glob.glob( os.path.join(self.conf_dir,'*') ):
                if f == main_conf:
                    continue
                self.log("**** Parsing file : %s " % f)
                self.load_file(f)

        self.log("end load config %s " % self.conf_dir)

    def maj_obj(self):
        """
            ------------------------
            Mise a jour des objets
            ------------------------
        """
        self.log("DEBUT maj_obj")
        for k in self.obj:
            self.log("===> Objet : %s " % k)
            self.log("     %s " % str(self.obj[k]))

        self.log("FIN maj_obj")


    def check_service(self):
        """
            -------------------
            Test des services 
            -------------------
        """
        self.log("DEBUT check service")
        for k in self.service:
            self.log("===> service : %s " % k)
            self.log("     %s " % str(self.service[k]))
        self.log("FIN   check service")

    def run(self):
        """
            -------------------------
            Execution du superviseur
            -------------------------
        """
        self.init()
        self.log("debut")
        self.load_config()
        if self.run_ok:
            while not self.stop_running:
                self.maj_obj()
                self.check_service()
                self.end_of_turn()
        self.shutdown()

    def end_of_turn(self):
        """
            ------------
            Fin du tour 
            ------------
        """
        self.log("End of Turn")
        time.sleep(self.sleep)
        self.stop_running = True

    def shutdown(self):
        """
            --------------------
            Arret du superviseur
            --------------------
        """
        self.log("Fin")
        self.log_file.close()

### -----------------------------
## Lancement procedure de test
### -----------------------------
def test():
    """
        LANCEMENT DES TESTS
    """
    s = Superviseur()
    s.run()

if __name__ == '__main__':
    test()
    
