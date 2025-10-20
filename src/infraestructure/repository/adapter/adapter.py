import psycopg2.pool
import configparser
from route import RUTA
config = configparser.ConfigParser()
config.read(RUTA+'/config.ini')
def poolConection():
    conn = psycopg2.pool.ThreadedConnectionPool(
            1,
            5,
            user=config['default']['DB_USER'],
            password=config['default']['DB_PASSWORD'],
            host=config['default']['DB_HOST'],
            port=config['default']['DB_PORT'],
            database=config['default']['DB_NAME'],
        )

    return conn

pool = poolConection()

