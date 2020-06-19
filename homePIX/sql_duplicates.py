import sqlite3

def nameFromPath(t):

    ls = t.lower().split( '/' )
    return ls[-1]

con = sqlite3.connect("db.sqlite3")
con.create_function("strip", 1, nameFromPath)
cur = con.cursor()

cur.execute("DELETE FROM homePIX_picturefile WHERE rowid NOT IN ( SELECT MAX(rowid) FROM homePIX_picturefile GROUP BY strip(file));")

con.commit()
con.close()