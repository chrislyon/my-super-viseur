# -*- coding: utf-8 -*-

## --------------
## Super Viseur
## --------------

"""
 Super Viseur
"""

import datetime
import time
import os, sys
import shlex
import traceback
import pudb

class SV_ParseError(Exception):
    """
        Erreur de parsing : transmets la ligne + le contenu de la ligne
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

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

class SV_File(SV_Object):
    """
        Class Fichier
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'FILE'
        self.path = path

class SV_Directory(SV_Object):
    """
        Classe Répertoire
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'DIRECTORY'
        self.path = path

class SV_Program(SV_Object):
    """
        Class Programme 
    """
    def __init__(self, nom, path):
        self.nom = nom
        self.typ = 'PROGRAM'
        self.path = path

class SV_Host(SV_Object):
    """
        Class Host 
    """
    def __init__(self, nom):
        self.nom = nom
        self.typ = 'HOST'

class Ligne(object):
    """
        Classe ligne de fichier de conf
    """
    def __init__(self, nol, ligne):
        self.numlig = nol
        self.ligne = ligne
    def __str__(self):
        return "%s:%s" % (self.numlig, self.ligne)

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
        for li in ligs:
            self.log( "\t> %s : %s " % (li.numlig, li.ligne))
            lexer = shlex.shlex(li.ligne)
            cmd = lexer.next()
            self.log( "Commande : %s " % cmd)
            if cmd == 'SET':
                obj = lexer.next()
                if obj in ('FILE', 'DIRECTORY', 'PROGRAM'):
                    try:
                        name = lexer.next()
                        cmd_path = lexer.next()
                        if cmd_path != 'PATH':
                            pudb.set_trace()
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
                elif obj == 'HOST':
                    try:
                        name = lexer.next()
                    except:
                        raise SV_ParseError(li)
                    self.add_obj( SV_Host(name) )
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
                ll.append(li)
                continue
            else:
                if ll:
                    try:
                        self.parse(ll)
                    except SV_ParseError as e:
                        self.log(" Parse Error ligne %s " % e.value)
                    except:
                        e = sys.exc_info()[0]
                        self.log(" Parse Error ligne %s " % e.value)
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
            self.log(" Objet : %s " % k)

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
    
