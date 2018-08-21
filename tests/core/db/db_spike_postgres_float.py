import sys
import time
from random import random

import psycopg2


def main(args=None):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect("dbname=test user=eocdb password=bdcoe")
        cursor = connection.cursor()

        initialize_database(connection, cursor)
        fill_database(connection, cursor)
        search_database(connection, cursor)

    finally:
        clean_up_db(connection, cursor)

    return 0

def initialize_database(conn, cursor):
    print("initialize database ...")

    cursor.execute("CREATE TABLE in_situ_point (id SERIAL PRIMARY KEY, lon real, lat real, acquisition_time TIMESTAMP, description varchar);")
    cursor.execute("CREATE INDEX in_situ_point_gix ON in_situ_point (lon, lat);")
    conn.commit()

    print("done")

def fill_database(conn, cursor):
    num_entries = 1000000
    print("fill database ({} values)...".format(num_entries))

    t_start = time.clock()

    try:

        for idx in range(0, num_entries):
            lon = 180.0 - (random() * 360.0)
            lat = 90.0 - (random() * 180.0)
            desc_text = "A random description, version " + str(idx)
            cursor.execute('''INSERT INTO in_situ_point(lon, lat, description) VALUES ( %s, %s, %s);''', (lon, lat, desc_text, ))
    finally:
        conn.commit()

    print("done - ({} sec)".format(time.clock() - t_start))

def search_database(conn, cursor):
    print("search database...")
    t_start = time.clock()

    lon_min = -30.0
    lon_max = -25.0
    lat_min = -60.0
    lat_max = -55.0

    try:
        cursor.execute("SELECT * FROM in_situ_point WHERE lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s;", (lon_min, lon_max, lat_min, lat_max,))
        #cursor.execute("SELECT ST_AsText(in_situ_point.location) FROM in_situ_point")
        results = cursor.fetchall()
        print(len(results))
    except Exception as e:
        print(e)
        conn.rollback()

    print("done - ({} sec)".format(time.clock() - t_start))

def clean_up_db(connection, cursor):
    print("clean up database ...")

    cursor.execute("DROP TABLE IF EXISTS in_situ_point;")
    connection.commit()

    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

    print("done")


if __name__ == "__main__":
    sys.exit(main())
