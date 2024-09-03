import psycopg2
from grc.utils.logger import LogLevel, Logger

logger = Logger()

conn = psycopg2.connect(
    database='postgres',
    user='postgres',
    password='password',
    host='localhost',
    port= '5432'
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE database grc')
logger.log(LogLevel.INFO, 'Database created successfully...')
conn.close()
