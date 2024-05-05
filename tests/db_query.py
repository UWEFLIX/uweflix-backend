import pymysql
from src.crud.engine import *


def run_query():
    db_config = {
        'host': host,
        'port': 3306,  # Default MySQL port
        'user': user,
        'password': password,
        'database': db,  # Optional, remove if not needed
    }

    connection = pymysql.connect(**db_config)

    with connection.cursor() as cursor:
        cursor.execute(
        """
            SELECT
                (SELECT COUNT(*) FROM users) AS user_count,
                (SELECT COUNT(*) FROM cities) AS city_count;
        """
        )
        row = cursor.fetchone()

    connection.close()
    return row[0], row[1],
