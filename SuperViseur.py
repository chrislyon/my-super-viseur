# -*- coding: utf-8 -*-

## --------------
## Super Viseur
## --------------

import datetime
import time
import os, sys
import pudb
import shlex

class SV_ParseError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    

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
        for l in ligs:
            self.log( "\t> %s " % l)
            lexer = shlex.shlex(l)
            cmd = lexer.next()
            self.log( "Commande : %s " % cmd)
            if cmd == 'SET':
                obj = lexer.next()
                if obj in ('FILE', 'DIRECTORY', 'PROGRAM'):
                    try:
                        name = lexer.next()
                        cmd_path = lexer.next()
                        if cmd_path != 'PATH':
                            raise SV_ParseError(l)
                        path = lexer.next()
                    except:
                        raise SV_ParseError(l)
                else:
                    self.log( "\t\t%s : %s " % (obj, lexer.next() ))
            else:
                self.log( "CMD : %s non reconnu" )
                
                


    def load_config(self):
        """
            Chargement de la configuration
        """
        #pudb.set_trace()
        self.log("load config %s " % self.conf_file)
        if os.path.exists(self.conf_file):
            self.run_ok = True
            with open(self.conf_file) as f:
                ll = []
                for l in f.readlines():
                    l = l.rstrip()
                    if l.startswith('#'):
                        continue
                    if l:
                        ## Si cela commence par une suite
                        if l.startswith(('\t', ' ')):
                            ll.append(l)
                            continue
                        else:
                            if ll:
                                try:
                                    self.parse(ll)
                                except:
                                    e = sys.exc_info()[0]
                                    self.log(" Error : %s " % e)
                                    self.run_ok = False
                                ll=[]
                            ll.append(l)
        else:
            self.log("Fichier config %s inexistant" % self.conf_file)
            self.run_ok = False

    def maj_obj(self):
        """
            Mise a jour des objets
        """
        self.log("maj_obj")

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
    s = Superviseur()
    s.run()

if __name__ == '__main__':
    test()
    
