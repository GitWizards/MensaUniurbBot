#!/bin/python3.6
import sqlite3

# Database name
DB_NAME = 'mensauniurb.db'

# Open DB
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

try:
    # Create tables
    query = ('CREATE TABLE user('
             'chat_id integer primary key,'
             'username text,'
             'name text,'
             'notification text,'
             'language text)')
    c.execute(query)

    query = ('CREATE TABLE action('
             'id integer primary key autoincrement,'
             'name text)')
    c.execute(query)

    query = ('CREATE TABLE request('
            'id integer primary key autoincrement,'
            'date date,'
            'user integer,'
            'action integer,'
            'foreign key(user) references user(chat_id),'
            'foreign key(action) references action(id))')
    c.execute(query)

    query = ('CREATE TABLE poll('
             'ask text primary key,'
             'answer1 text,'
             'answer2 text)')
    c.execute(query)

    query = ('CREATE TABLE user_answer('
             'user integer,'
             'poll text,'
             'answer text,'
             'foreign key(user) references user(chat_id),'
             'foreign key(poll) references poll(ask),'
             'primary key(user, poll))')
    c.execute(query)

    c.execute('INSERT INTO action(name) VALUES("/duca")')
    c.execute('INSERT INTO action(name) VALUES("/tridente")')
    c.execute('INSERT INTO action(name) VALUES("/sogesta")')
    c.execute('INSERT INTO action(name) VALUES("/cibusduca")')
    c.execute('INSERT INTO action(name) VALUES("/cibustridente")')
    c.execute('INSERT INTO action(name) VALUES("/orari")')
    c.execute('INSERT INTO action(name) VALUES("/prezzi")')
    c.execute('INSERT INTO action(name) VALUES("/allergeni")')
    c.execute('INSERT INTO action(name) VALUES("/info")')
except:
    print("DB exist already!")
finally:
    conn.commit()
    conn.close()
