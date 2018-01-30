"""
This script adds SERVICE_DTM to epic_notes.note_info
"""

import os, sys
import sqlite3 as sqlite
import pandas as pd


def main():
    con = sqlite.connect(db)

    #con.execute("ALTER TABLE note_info ADD COLUMN SERVICE_DTM TEXT;")
    #con.execute("UPDATE note_info\
    #            SET SERVICE_DTM = (\
    #              SELECT SERVICE_DTM\
    #              FROM epic_notes t2\
    #              WHERE NOTE_ID = t2.NOTE_ID);")
    #df = pd.read_sql("SELECT * FROM note_info WHERE is_within_30_days = 1;", con)
    note_info = pd.read_sql("SELECT * FROM note_info", con)
    note_dates = pd.read_sql("SELECT NOTE_ID, SERVICE_DTM FROM epic_notes", con)
    print(note_dates.head())

    note_dates = {note_id: dtm for (note_id, dtm) in zip(note_dates.NOTE_ID, note_dates.SERVICE_DTM)}

    note_info.SERVICE_DTM = note_info.NOTE_ID.apply(lambda note_id: note_dates[note_id])
    note_info = note_info.drop(columns=['level_0', 'index'])
    print(note_info[note_info.is_within_30_days == 1].head())
    note_info.to_sql("note_info", con, if_exists='replace')
    con.close()



if __name__ == '__main__':
    db = sys.argv[1]
    main()
