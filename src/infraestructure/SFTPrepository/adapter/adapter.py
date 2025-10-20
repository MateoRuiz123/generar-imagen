import pysftp
import configparser
from route import RUTA
config = configparser.RawConfigParser()
print(RUTA+'/config.ini'+'----------->')
config.read(RUTA+'/config.ini')
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

def connectSFTP():
    return pysftp.Connection(host=config['default']['SFTP_HOST'], username=config['default']['SFTP_USER'], password=config['default']['SFTP_PASSWORD'], cnopts=cnopts)

    
