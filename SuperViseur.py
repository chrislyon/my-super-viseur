# -*- coding: utf-8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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


## -----------------------
## Objet pour le parser
## -----------------------
class Ligne(object):
    """
        Classe ligne de fichier de conf
    """
    def __init__(self, nol, ligne, suite=False):
        self.numlig = nol
        self.ligne = ligne
        self.suite = suite

    def __str__(self):
        return "%s:%s" % (self.numlig, self.ligne)

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
            Parsing d'un groupe coherent
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
            if body_mode and curr_obj and not 'BODY END' in cmd:
                curr_obj.corps.append( li.ligne )
                continue
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
                else:
                    raise SV_ParseError(li)
                continue
            else:
                curr_obj = None
            if cmd == 'SET':
               obj = lexer.next()
               if obj in ('FILE', 'DIRECTORY', 'PROGRAM', 'LOG_FILE'):
                  try:
                     name = lexer.next()
                     cmd_path = lexer.next()
                     if cmd_path != 'PATH':
                        raise SV_ParseError(li)
                     path = lexer.next()
                  except:
                     raise SV_ParseError(li)
                  ## Si j'arrive ici c'est que la syntaxe est bonne
                  if obj == 'FILE':
                     self.add_obj( SV_File(name, path))
                  if obj == 'DIRECTORY':
                     self.add_obj( SV_Directory(name, path))
                  if obj == 'PROGRAM':
                     self.add_obj( SV_Program(name, path))
                  if obj == 'LOG_FILE':
                     self.add_obj( SV_LogFile(name, path))
               elif obj in ('HOST', 'SERVICE'):
                  try:
                     name = lexer.next()
                  except:
                     raise SV_ParseError(li)
                  if obj == 'HOST':
                     self.add_obj( SV_Host(name) )
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
            else:
               self.log( "CMD : %s non reconnu" % cmd )

    def parse_lines(self, lines):
        """
        Parsing d'un groupe de lignes
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

    def load_config(self):
        """
            Chargement de la configuration
        """
        #pudb.set_trace()
        self.log("load config %s " % self.conf_file)
        if os.path.exists(self.conf_file):
            self.run_ok = True
            with open(self.conf_file) as f:
                nol = 0
                ll = []
                for l in f.readlines():
                    nol += 1
                    l = l.rstrip()
                    if l.startswith('#'):
                        continue
                    if l:
                        ll.append( Ligne( nol, l) )
            self.parse_lines(ll)
        else:
            self.log("Fichier config %s inexistant" % self.conf_file)
            self.run_ok = False

    def maj_obj(self):
        """
            Mise a jour des objets
        """
        self.log("DEBUT maj_obj")
        for k in self.obj:
            self.log("===> Objet : %s " % k)
            self.log("     %s " % str(self.obj[k]))

        self.log("FIN maj_obj")


    def check_service(self):
        """
            Test des services 
        """
        self.log("check service")

    def run(self):
        """
            Execution du superviseur
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
            Fin du tour 
        """
        self.log("End of Turn")
        time.sleep(self.sleep)
        self.stop_running = True

    def shutdown(self):
        """
            Arret du superviseur
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
    
