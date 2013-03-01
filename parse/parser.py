## -----------------------
## Objet pour le parser
## -----------------------
class Ligne(object):
    """
        Classe ligne de fichier de conf
    """
    def __init__(self, nol, ligne, typ='Mono'):
        self.numlig = nol   ## No de ligne d'origine
        self.ligne = ligne  ## La ligne en mode texte
        self.typ = typ      ## Le type de la ligne  Mono ou Multi
        self.tokens = None  ## La version tokenise

    def __str__(self):
        return "%s:%s" % (self.numlig, self.ligne)

N = 1
COMMAND     = 1   # SET CHECK IF MESSAGE MAIL
ACTION      = 2   # ALERT WRITE
OPER        = 3   # + - / * etc ...
PARAM       = 4   # THEN PATH ADD 
DIGIT       = 5   # Chiffre et autre
PERCENT     = 6   # Le signe % doit suivre un chiffre
IDENTIFIER  = 7   # Nom
STRING      = 7   # chaine de caractere


class Token(object):
    """
        Un token
    """
    def __init__(self, typ, value=None):
        self.typ = typ
        self.value = value

    def __str__(self):
        return "%s:%s" % (self.typ, self.value)

def parse(tokens):
    t = tokens.pop(0)
    if t.typ == COMMAND:
        if t.value == 'SET':
            p1 = tokens.pop(0)
            if p1.typ != PARAM:
                print "Error NOT A PARAM"
            else:
                if p1.value == "FILE":
                    name = tokens.pop(0)
                    print "OK Creation de %s avec le type %s" % (p1.value, name.value)
                else:
                    print "Error PARAM Inconnue"
        elif t.value == 'CHECK':
            pass
        elif t.value == 'IF':
            pass
        elif t.value == 'SERVICE':
            pass
        else:
            print "Error CMD inconnue : %s" % t.value
    else:
        print "Error Not a COMMAND : %s" % t
        

to_parse = []

to_parse.append( Token( COMMAND, 'SET' ) )
to_parse.append( Token( PARAM, 'FILE' ) )
to_parse.append( Token( IDENTIFIER, 'file1' ) )
to_parse.append( Token( PARAM, 'PATH' ) )
to_parse.append( Token( STRING, '"/tmp/toto"' ) )


parse(to_parse)
