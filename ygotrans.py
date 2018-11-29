#!/usr/bin/env python3

"""
YGOPro CDB's translator script
Written in Python3
The script will firstly copy the cdb passed as argument to a backup version (name + .backup)
Then the script will go through the cdb and search in wikia for a translation

Usage: python3 ygotrans.py [OPTIONAL --yugipedia][path to cdb] [language code]
"""

import sqlite3
import argparse
import requests
import time
import pyprog
from shutil import copyfile
from bs4 import BeautifulSoup


def argparser():
    parser = argparse.ArgumentParser(prog = "YGOTrans", description = "YGOTrans aim to translate automatically CDB files from YGOPRO")
    parser.add_argument("cdb", help="The cdb file to process")
    parser.add_argument("lang", help="de, fr, pt, es, it")
    parser.add_argument("--yugipedia", "-y", action="store_true", help = "Use Yugipedia instead of Wikia")
    args = parser.parse_args()
    return args

def search_card(id, yugipedia=False):
    if yugipedia:
        page = requests.get("https://yugipedia.com/wiki/" + id)
    else:
        page = requests.get("http://yugioh.wikia.com/wiki/" + id)
    return page

def sql_connection(cdb):
    con = sqlite3.connect(cdb)
    return con

def count(arg):
    return len(str(arg))

#adding zero to the passcode (if they need)
def add_zero(arg):
    result = ""
    for x in range(0, 8-count(arg)):
        result += "0"
    result = result + str(arg)
    return result

def remove_accents(s):
    alpha1 = "ÀâÂÄåÅÇÉèÈêÊëËîÎïÏôÔöÖùÙûÛÜÿŸ"
    alpha2 = "AaAAaACEeEeEeEiIiIoOoOuUuUUyY"
    s = s.translate(str.maketrans(alpha1, alpha2))
    return s.replace('œ', 'oe')

def is_pendulum(id, cdb):
    con = sql_connection(cdb)
    cursor = con.cursor()
    cursor.execute("SELECT type FROM datas WHERE id = (?)", (id,))
    type_card = cursor.fetchone()
    if (type_card[0] & int('1000000', 16)) == int('1000000', 16):
        return True
    return False

def missing(id):
    file = open('missing_translation.txt', 'a')
    file.write(id + '\n')
    file.close()

def get_info(id, page, args):
    if page.status_code != 200:
        missing(id)
        return None
    else:
        soup = BeautifulSoup(page.text, "lxml")
        if args.yugipedia:
            spans = soup.find_all('td', attrs={'lang':args.lang})
            if len(spans) == 0:
                missing(id)
                return None
            name = str(spans[0].text)
            description = str(spans[1].text)
            if is_pendulum(id, args.cdb):
                description += str(spans[2].text)
            name = remove_accents(name).encode("utf-8")
            description = remove_accents(description).encode("utf-8")
            return {'name': name, 'description': description}
        else:
            spans = soup.find_all('span', attrs={'lang':args.lang})
            name = str(spans[0].text)
            if len(spans) == 2:
                description = str(spans[1].text)
            elif len(spans) == 5:
                description = str(spans[1].text) + str(": ")#penduleffect
                description += str(spans[2].text) + str('\n\n')
                description += str(spans[3].text) + str(": ")#monstereffect
                description += str(spans[4].text)
            else:
                missing(id)
                return None
            name = remove_accents(name).encode("utf-8")
            description = remove_accents(description).encode("utf-8")
            return {'name': name, 'description': description}

def main():
    time_elapsed = int(time.time())
    args = argparser()
    copyfile(args.cdb, args.cdb + ".backup") #make a backup of the cards.cdb
    con = sql_connection(args.cdb)
    cursor = con.cursor()
    cursor.execute("SELECT id FROM texts")
    req = cursor.fetchall()
    prog = pyprog.ProgressBar("", "", len(req), complete_symbol="█", not_complete_symbol="-")
    prog2 = pyprog.ProgressIndicatorFraction("", "", len(req))
    prog.update()
    prog2.update()
    i = 0
    for row in req:
        i += 1
        prog.set_stat(i)
        prog2.set_stat(i)
        prog.update()
        prog2.update()
        id = add_zero(row[0])
        page = search_card(id, args.yugipedia)
        info = get_info(id, page, args)
        if info is not None:
            cursor.execute("UPDATE texts SET name = (?), desc = (?) WHERE id = (?)", (info['name'], info['description'], row[0]))
            con.commit()
    time_elapsed = int(time.time()) - time_elapsed
    print()
    print("Script ended in: " + str(time_elapsed))
    con.close()

if __name__ == '__main__':
    main()
