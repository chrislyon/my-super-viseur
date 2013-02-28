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
        self.suite = suite  # a virer

    def __str__(self):
        return "%s:%s" % (self.numlig, self.ligne)

