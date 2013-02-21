##
## Check sys
##

SERVICE_NAME = "CHECK SYSTEME"


with SYSTEM.df as DF
    if DF.root.usage > 80%:
        alert SYSADMIN "Root usage 80%"
    if DF.ado.usage > 80%
        alert SYSADMIN "ADO usage 80%"

MAIL_ROOT = FILE /var/spool/mail/root

if MAIL_ROOT.size 
    alert(subject=" Mail root trop gros a verifier" )

X3V5 = ORACLE INSTANCE 

for TBS in X3V5.tbs
    if TBS.usage > 80%
        alert "X3V5 Tbs : %s usage 80%" % TBS.name

HOST = 127.0.0.1

if HOST.port(80)

OBJET a gerer
---------------

SERVICE
    UP / DOWN
    COMPTEUR

SYSTEME
    DF  usage volume 
    LOAD    USER SYS WAIT IDLE
    SYSLOG

DATE 
    NOW
    TODAY
    TOMORROW
    DAY
    MONTH
    YEAR

SAR

PROGRAM
    STATUS
    EXEC

FILE
    UIG / GID
    PERM
    SIZE
    TIMESTAMP CHANGED
    LOCATION
    CONTENT ( "*minated*" / written )

REP
    NB FILES
    NB REP
    SIZE TOTAL

HOST 
    PORT
    PING
    PROTOCOL (HTTP / SSH ...)

PRINTER
    ONLINE / OFFLINE

PROCESSUS 
    CPU
    MEM

ORACLE INSTANCE
    MEMORY
    TBS
    STOCKAGE / VOLUMETRIE
    CACHE TAMPON
    ERROR
    TABLE
    STATISTICS


MYSQL INSTANCE 
POSTGRESQL INSTANCE

ACTION
-------
ALERT
    SUBJECT
    GROUP
    MESSAGE
    TYPE DE MESSAGE

SERVICE
    STOP/START
    ADD

LOG FILE Message    Ecrit dans un fichier de log
LOG BASE Message    

EXEC 

