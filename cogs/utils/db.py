import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "user": os.getenv("DB_user"),
    "password": os.getenv("DB_pass"),
    "host": os.getenv("DB_host"),
    "database": os.getenv("DB_db"),
    "raise_on_warnings": True,
}

import mysql.connector


def connect():
    try:
        cnx = mysql.connector.connect(**db_config)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return cnx
        # cnx.close()


def query(query):
    print(f"   Quering database with: {query}")
    cnx = connect()
    cursor = cnx.cursor(named_tuple=True)

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    cnx.close()

    return rows


def insert(query):
    print(f"Quering database with: {query}")
    cnx = connect()
    cursor = cnx.cursor()

    cursor.execute(query)
    id = cursor.lastrowid

    cnx.commit()
    cursor.close()
    cnx.close()

    return id

def parse_str(db_str):
    return str(db_str).split("'")[1]