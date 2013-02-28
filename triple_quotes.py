import glob
import Parse_Ligne as P


def search_triple_quotes(fichier):
    buf = []
    rlines = []
    lines = open(fichier).readlines()
    append_mode = False
    nol = 0
    for l in lines:
        ## testons si ya des """
        if '"""' in l:
            if not append_mode:
                #print "Found START"
                append_mode = True
                buf = []
            else:
                #print "Found END"
                append_mode = False
                buf.append(l)
                #print str(buf)
                nol += 1 
                rlines.append( P.Ligne( nol, buf) )
                continue
        if append_mode:
            buf.append(l)
            continue
        ## Sinon c'est une ligne normale
        nol += 1
        rlines.append( P.Ligne( nol, l) )
    return rlines

def test():
    rep = "conf.d"
    for f in glob.glob(rep+"/*"):
        print f
        r = search_triple_quotes(f)

    for l in r:
        print l


if __name__ == "__main__":
    test()
