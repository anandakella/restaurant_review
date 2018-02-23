import os
OUTPUT_DIR = '/tmp'
DB_NAME = 'revapp.db'
os.path.join(OUTPUT_DIR, DB_NAME)
DB_TYPE = 'SQLITE'
if DB_TYPE == 'SQLITE':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(OUTPUT_DIR, DB_NAME))
SQLALCHEMY_TRACK_MODIFICATIONS = False
RATINGS_USER_WAIT_TIME_IN_SECONDS = 60 * 60 * 30 * 24