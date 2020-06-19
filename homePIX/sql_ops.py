import sqlite3

def lower_sorted(t):

    ls = t.lower().split( ',' )
    return ','.join( sorted( ls ) )

def word_count(t):

    ls = t.lower().split( ',' )
    return len( ls )

con = sqlite3.connect("db.sqlite3")
con.create_function("cnt", 1, word_count)
# con.create_function("lc", 1, lower_sorted)
cur = con.cursor()

cur.execute("update homePIX_keywords set count=cnt(keywords);")
# cur.execute("update imports set tags=lc(tags);")

con.commit()
con.close()