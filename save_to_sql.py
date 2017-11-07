#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import csv

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

NODES_FILE = "nodes.csv"
NODE_TAGS_FILE = "nodes_tags.csv"
WAYS_FILE = "ways.csv"
WAY_NODES_FILE = "ways_nodes.csv"
WAY_TAGS_FILE = "ways_tags.csv"

def createTable():
    db = sqlite3.connect("sg.db")
    c = db.cursor()

    c.execute('''CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT);''')

    db.commit()

    c.execute('''CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id));''')

    db.commit()

    c.execute('''CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT);''')

    db.commit()

    c.execute('''CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id));''')

    db.commit()

    c.execute('''CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id));''')

    db.commit()

    db.close()


def insertData():
    db = sqlite3.connect("sg.db")
    db.text_factory = str
    c = db.cursor()

    with open(NODES_FILE, 'rb') as sd:
        r = csv.DictReader(sd)
        for line in r:
            my_list = []
            my_list.append(int(line['id']))
            my_list.append(float(line['lat']))
            my_list.append(float(line['lon']))
            my_list.append(str(line['user']))
            my_list.append(int(line['uid']))
            my_list.append(int(line['version']))
            my_list.append(int(line['changeset']))
            my_list.append(str(line['timestamp']))

            c.execute('''insert into nodes (id,lat,lon,user,uid,version,changeset,timestamp) 
                       values (?,?,?,?,?,?,?,?)''', my_list)
            db.commit()

    with open(NODE_TAGS_FILE, 'rb') as sd:
        node_tag_file = csv.DictReader(sd)
        for line in node_tag_file:
            my_list = []
            my_list.append(line['id'])
            my_list.append(line['key'])
            my_list.append(line['value'])
            my_list.append(line['type'])

            c.execute('''insert into nodes_tags (id,key,value,type) 
                       values (?,?,?,?)''', my_list)
            db.commit()

    with open(WAYS_FILE, 'rb') as sd:
        way_file = csv.DictReader(sd)
        for line in way_file:
            my_list = []
            my_list.append(line['id'])
            my_list.append(line['user'])
            my_list.append(line['uid'])
            my_list.append(line['version'])
            my_list.append(line['changeset'])
            my_list.append(line['timestamp'])

            c.execute('''insert into ways (id,user,uid,version,changeset,timestamp) 
                       values (?,?,?,?,?,?)''', my_list)
            db.commit()

    with open(WAY_TAGS_FILE, 'rb') as sd:
        way_tag_file = csv.DictReader(sd)
        for line in way_tag_file:
            my_list = []
            my_list.append(line['id'])
            my_list.append(line['key'])
            my_list.append(line['value'])
            my_list.append(line['type'])

            c.execute('''insert into ways_tags (id,key,value,type) 
                       values (?,?,?,?)''', my_list)
            db.commit()

    with open(WAY_NODES_FILE, 'rb') as sd:
        way_nd_file = csv.DictReader(sd)
        for line in way_nd_file:
            my_list = []
            my_list.append(line['id'])
            my_list.append(line['node_id'])
            my_list.append(line['position'])

            c.execute('''insert into ways_nodes (id,node_id,position) 
                       values (?,?,?)''', my_list)
            db.commit()

    db.close()

