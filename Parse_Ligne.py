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

COMMAND = 1

class Token(object):
    """
        Un token
    """
    def __init__(self, typ, value=None):
        self.typ = typ
        self.value = value

    def __str__(self):
        return "%s:%s" % (self.typ, self.value)

