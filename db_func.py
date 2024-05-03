import mysql.connector
from playlist import Playlist

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Beenguyen2002",
            database="musicplayer"
        )
        return connection
    except mysql.connector.Error as error:
        print("Failed to connect to the database: {}".format(error))
        return None
    
def execute_fetch_all(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as error:
        print("Error executing query: {}".format(error))
        return None
    
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as error:
        print("Error execute query: {}".format(error))

def load_playlists(conn):
    playlists = []
    try:
        conn.connect()
        query = "select * from playlists"
        list = execute_fetch_all(conn, query)
        for item in list:
            playlist = Playlist(item[0], item[1])
            playlists.append(playlist)
        return playlists
    except mysql.connector.Error as error:
        print(f'Error: {error}')
        return None    

def load_song_of_playlist(conn, playlist_id):
    songs = []
    try:
        print(playlist_id)
        conn.connect()
        query = f"select * from songs where playlist_id = '{int(playlist_id)}'"
        list = execute_fetch_all(conn, query)
        for item in list:
            songs.append(item[1])
        return songs
    except mysql.connector.Error as error:
        print(f'Error: {error}')
        return None  

def add_song_to_playlist(conn, path, playlist_id):
    try:
        conn.connect()
        query= f"insert into songs(path, playlist_id) values ('{path}', '{playlist_id}')"
        execute_query(conn, query)
        return True
    except mysql.connector.Error as error:
        return False
    finally:
        conn.close()

def add_playlist(conn, name):
    try:
        conn.connect()
        query= f"insert into playlists(name) values ('{name}')"
        execute_query(conn, query)
        return True
    except mysql.connector.Error as error:
        return False
    finally:
        conn.close()

def delete_playlist(conn, id):
    try:
        conn.connect()
        query = f"delete from songs where playlist_id = '{id}'"
        execute_query(conn, query)
        query = f"delete from playlists where playlist_id = '{id}'"
        execute_query(conn, query)
        return True
    except mysql.connector.Error as error:
        return False
    
def delete_all_playlists(conn):
    try:
        conn.connect()
        query = f"delete from playlists"
        execute_query(conn, query)
        return True
    except mysql.connector.Error as error:
        return False