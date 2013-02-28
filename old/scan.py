import re
import sys
import glob
 
def identifier(scanner, token): return "IDENT", token
def comment(scanner, token): return "COMMENT", token
def ident_data(scanner, token): return "IDENT_DATA", token
def constant_string(scanner, token): return "STRING", token
def email(scanner, token): return "EMAIL", token
def operator(scanner, token):   return "OPERATOR", token
def digit(scanner, token):      return "DIGIT", token
def digit_size(scanner, token):      return "DIGIT_SIZE", token
def command(scanner, token):  return "COMMAND", token
def option(scanner, token):  return "OPTION", token
def end_stmnt(scanner, token):  return "END_STATEMENT"
 
def scan(fichier):
    scanner = re.Scanner([
        (r"\#.*", comment),
        (r"[a-zA-Z_.-]*\@[a-zA-Z._-]*", email),
        (r"[a-zA-Z_]*\.[a-zA-Z_]\w*", ident_data),
        (r"SET|CHECK|SERVICE|IF|GROUP", command),
        (r"FILE|PATH|ALERT|MESSAGE|THEN", option),
        (r"[a-zA-Z_]\w*", identifier),
        (r"\+|\-|\\|\*|\=|\>|\<|\>\=|\<\=", operator),
        (r"\".*\"", constant_string),
        (r"[0-9]+(\.[0-9]+)?(Mo|M|Ko|K|Go|G|o|To|T)?", digit_size),
        (r"[0-9]+(\.[0-9]+)?", digit),
        (r"\n", end_stmnt),
        (r"\s+", None),
        ])

    to_scan = open(fichier).readlines()

    tokens, remainder = scanner.scan(" ".join(to_scan))
    print 'Reste : %s ' % remainder
    for token in tokens:
        print token


def run(rep):
    confs = glob.glob(rep+"/*")
    for c in confs:
        print "=" * 50
        scan(c)
        print "=" * 50
    

if __name__ == '__main__':
    rep = "conf.d"
    run( rep )
