import re
 
def identifier(scanner, token): return "IDENT", token
def comment(scanner, token): return "COMMENT", token
def ident_data(scanner, token): return "IDENT_DATA", token
def constant_string(scanner, token): return "STRING", token
def operator(scanner, token):   return "OPERATOR", token
def digit(scanner, token):      return "DIGIT", token
def digit_size(scanner, token):      return "DIGIT_SIZE", token
def command(scanner, token):  return "COMMAND", token
def option(scanner, token):  return "OPTION", token
def end_stmnt(scanner, token):  return "END_STATEMENT"
 
## Note il faut bien mettre les choses dans l'ordre
## Exemple 100G (digit_size) doit etre avant 100 (digit)
scanner = re.Scanner([
    (r"\#.*", comment),
    (r"SET|CHECK|SERVICE|IF", command),
    (r"FILE|PATH|ALERT|MESSAGE|THEN", option),
    (r"[a-zA-Z_]+(\.[a-zA-Z_]+)", ident_data),
    (r"[a-zA-Z_]\w*", identifier),
    (r"\+|\-|\\|\*|\=|\>|\<|\>\=|\<\=", operator),
    (r"\".*\"", constant_string),
    (r"[0-9]+(\.[0-9]+)?(Mo|M|Ko|K|Go|G|o|To|T)?", digit_size),
    (r"[0-9]+(\.[0-9]+)?", digit),
    (r"\n", end_stmnt),
    (r"\s+", None),
    ])

to_scan = """
## TEST
foo = 5 * 30
bar = bar - 60
## SUITE
SET FILE TOTO PATH "/tmp/toto"
CHECK FILE TOTO
IF TOTO.size > 100Go THEN ALERT MAIL SYSADMIN MESSAGE WARNING
"""

tokens, remainder = scanner.scan(to_scan)
print 'Reste : %s ' % remainder
for token in tokens:
    print token
