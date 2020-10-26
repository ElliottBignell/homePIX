import sqlite3

def lower_sorted(t):

    ls = t.lower().split( ',' )
    return ','.join( sorted( ls ) )

def word_count(t):

    ls = t.lower().split( ',' )
    return len( ls )

con = sqlite3.connect("db.sqlite3")
con.create_function("cnt", 1, word_count)
con.create_function("lc", 1, lower_sorted)
cur = con.cursor()

cur.execute("INSERT INTO homePIX_keywords(keywords,count) SELECT distinct(tags),cnt(distinct(tags)) FROM imports;")
# cur.execute("update homePIX_keywords set count=cnt(keywords);")

con.commit()
con.close()
