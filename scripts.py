import psycopg2
from psycopg2.extensions import cursor, connection
from hashlib import sha256


def user_id_to_hash():
    db: connection = psycopg2.connect(
        host='10.252.1.1',
        port='10002',
        user='postgres',
        password='postgresDevPasswordNew',
        database='notiondipity_test')
    crs: cursor = db.cursor()
    crs.execute('ALTER TABLE last_updates ALTER COLUMN user_id TYPE VARCHAR(64)')
    crs.execute('ALTER TABLE embeddings ALTER COLUMN user_id TYPE VARCHAR(64)')
    db.commit()

    crs.execute('SELECT user_id FROM last_updates')
    user_ids = [r[0] for r in crs.fetchall()]

    for user_id in user_ids:
        user_id_hash = sha256(user_id.encode()).hexdigest()
        crs.execute('UPDATE last_updates SET user_id = %s WHERE user_id = %s', [user_id_hash, user_id])
        crs.execute('UPDATE embeddings SET user_id = %s WHERE user_id = %s', [user_id_hash, user_id])

    db.commit()
