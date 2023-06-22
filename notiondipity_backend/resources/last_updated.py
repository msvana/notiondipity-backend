from datetime import datetime, timedelta

from psycopg2.extensions import cursor


def get_last_updated_time(crs: cursor, user_id: str) -> datetime:
    crs.execute('SELECT * FROM last_updates WHERE user_id = %(user_id)s LIMIT 1', {'user_id': user_id})
    last_updated_record = crs.fetchone()
    if last_updated_record is None:
        return datetime.now() - timedelta(days=1)
    return last_updated_record[1]


def update_last_updated_time(crs: cursor, user_id: str):
    query_params = {'now': datetime.now(), 'user_id': user_id}
    crs.execute('UPDATE last_updates SET last_update = %(now)s WHERE user_id = %(user_id)s', query_params)
    if crs.rowcount == 0:
        crs.execute('INSERT INTO last_updates VALUES (%(user_id)s, %(now)s, 0)', query_params)


def has_finished_update(crs: cursor, user_id: str) -> bool:
    crs.execute(
        'SELECT * FROM last_updates WHERE user_id = %(user_id)s AND finished = 1 LIMIT 1', {'user_id': user_id})
    return crs.rowcount > 0


def mark_finished_update(crs: cursor, user_id: str):
    crs.execute('UPDATE last_updates SET finished = 1 WHERE user_id = %(user_id)s', {'user_id': user_id})
