## -----------------------
## Objet pour le parser
## -----------------------
class Ligne(object):
    """
        Classe ligne de fichier de conf
    """
    def __init__(self, nol, ligne, typ='Mono'):
        self.numlig = nol
        self.ligne = ligne
        self.typ = typ

    def __str__(self):
        return "%s:%s" % (self.numlig, self.ligne)

