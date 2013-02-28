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
import re
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
        

    def identifier(self, scanner, token):       return "IDENT", token
    def comment(self, scanner, token):          return "COMMENT", token
    def ident_data(self, scanner, token):       return "IDENT_DATA", token
    def constant_string(self, scanner, token):  return "STRING", token
    def email(self, scanner, token):            return "EMAIL", token
    def operator(self, scanner, token):         return "OPERATOR", token
    def digit(self, scanner, token):            return "DIGIT", token
    def percent(self, scanner, token):          return "PERCENT", token
    def digit_size(self, scanner, token):       return "DIGIT_SIZE", token
    def command(self, scanner, token):          return "COMMAND", token
    def option(self, scanner, token):           return "OPTION", token
    def action(self, scanner, token):           return "ACTION", token
    def end_stmnt(self, scanner, token):        return "END_STATEMENT"

    def parse_lines(self,lines):
        """
            Parsing des lignes
        """
        scanner = re.Scanner([
            (r"\#.*", self.comment),
            (r"[a-zA-Z_.-]*\@[a-zA-Z._-]*", self.email),
            (r"[a-zA-Z_]*\.[a-zA-Z_]\w*", self.ident_data),
            (r"SET|CHECK|SERVICE|IF|GROUP", self.command),
            (r"FILE|PATH|MESSAGE|THEN|ADD", self.option),
            (r"(ALERT|COUNTER)\b", self.action),
            (r"[a-zA-Z_]\w*", self.identifier),
            (r"[%]", self.percent),
            (r"\+|\-|\\|\*|\=|\>|\<|\>\=|\<\=", self.operator),
            (r"\".*\"", self.constant_string),
            (r"\'.*\'", self.constant_string),
            (r"[0-9]+(\.[0-9]+)?(%|Mo|M|Ko|K|Go|G|o|To|T)\b", self.digit_size),
            (r"[0-9]+(\.[0-9]+)?\b", self.digit),
            (r"\n", self.end_stmnt),
            (r"\s+", None),
            ])

        for l in lines:
            print l

            if l.typ == "Mono":
                tokens, remainder = scanner.scan(l.ligne)
            else:
                continue

            if remainder:
                print 'Reste : %s ' % remainder
            for token in tokens:
                print token

    def clean_conf_file(self, fichier):
        with open(fichier) as f:
            buf = []
            nol = 0
            append_mode = False
            rlines = []
            for l in f.readlines():
                nol += 1
                l = l.rstrip()
                if l.startswith('#'):
                    continue
                if l:
                    if '"""' in l:
                        if not append_mode:
                            append_mode = True
                            buf = []
                        else:
                            append_mode = False
                            buf.append(l)
                            nol += 1 
                            rlines.append( P.Ligne( nol, buf, typ='Multi') )
                            continue
                    if append_mode:
                        buf.append(l)
                        continue
                    ## Sinon c'est une ligne normale
                    nol += 1
                    rlines.append( P.Ligne( nol, l, typ='Mono') )
            return rlines


    def load_file(self, fichier):
        """
            Chargement d'un fichier et parsing
        """
        lines = self.clean_conf_file(fichier)
        self.parse_lines(lines)


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
    
