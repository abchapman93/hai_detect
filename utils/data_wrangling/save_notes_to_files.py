"""
This script saves all notes that are within 30 days
to a single directory called 'patient_cohort'
that is subdivided into 'train', 'val', and 'test'.
Minimal preprocessing is done to insert new lines before headers.
"""

import os, sys
from datetime import datetime
import pandas as pd
import sqlite3 as sqlite

from utils import helpers


def save_notes(note_info, note_ids, yes_notes, no_notes, con, train_val_test='train'):
    """
     Saves the notes found in a given set
    :param note_info: DataFrame with info about each note
    :param note_ids: a set of notes ids to save
    :param yes_notes: a set of note ids containing all note with complications
    :param no_notes: a set of note ids containing all note without complications
    :param con: connection to sqlite database
    :param train_val_test: which dataset this is in.
        Will save in a directory named with this value
    """
    df =  pd.read_sql("SELECT * FROM epic_notes WHERE NOTE_ID in {} AND LENGTH(NOTE) >= 100".format(note_ids), con)

    # Directory to save in
    outdir = os.path.join(datadir, 'patient_cohort', train_val_test)
    try:
        os.mkdir(outdir)
    except FileExistsError:
        pass



    # Configure DataFrame datatypes
    df['SERVICE_DTM'] = df['SERVICE_DTM'].apply(pd.to_datetime)
    df['NOTE_TYPE'] = df.NOTE_TYPE.apply(lambda x: '_'.join(x.split()).replace('/', '-') if x else 'NOTE_TYPE_UNKNOWN')
    df['PROV_TYPE'] = df.PROV_TYPE.apply(lambda x: '_'.join(x.split()) if x else 'PROV_TYPE_UNKNOWN')
    df.SERVICE_DTM = df.SERVICE_DTM.apply(lambda x: datetime.strftime(x, '%m-%d-%Y'))

    for i, row in df.iterrows():
        if row.NOTE_ID in yes_notes:
            has_complication = 'yes'
        else:
            has_complication = 'no'
        case_number = note_info[note_info.NOTE_ID == row.NOTE_ID].iloc[0].case_number
        save_note(row, case_number, outdir, has_complication)





def save_note(row, case_number, outdir, has_complication='yes'):
    fname = "{}_{}_".format(has_complication, case_number)
    fname += "{NOTE_ID}_{SERVICE_DTM}_{PROV_TYPE}_{NOTE_TYPE}.txt".format(**dict(row))
    outpath = os.path.join(outdir, fname)
    with open(outpath, 'w') as f:
        f.write(helpers.preprocess(row.NOTE))

def main():
    db = os.path.join(datadir, 'databases', 'epic.sqlite')
    con = sqlite.connect(db)

    outdir = os.path.join(datadir, 'patient_cohort')

    note_info = pd.read_sql("SELECT * FROM note_info WHERE is_within_30_days IN (0, 1) ", con)
    print(note_info.head())

    yes_notes = set(note_info[note_info.has_complication == 1].NOTE_ID)
    no_notes = set(note_info[note_info.has_complication == 0].NOTE_ID)

    # Save training notes
    train_note_ids = tuple(note_info[note_info.train_val_test == 'train'].NOTE_ID)
    save_notes(note_info, train_note_ids, yes_notes, no_notes, con, 'train')

    # Save val notes
    val_note_ids = tuple(note_info[note_info.train_val_test == 'val'].NOTE_ID)
    save_notes(note_info, val_note_ids, yes_notes, no_notes, con, 'val')

    # Save test notes
    test_note_ids = tuple(note_info[note_info.train_val_test == 'test'].NOTE_ID)
    save_notes(note_info, test_note_ids, yes_notes, no_notes, con, 'test')
    con.close()
    exit()

    train_dir = os.path.join(outdir, 'train')
    try:
        os.mkdir(train_dir)
    except FileExistsError:
        pass

    train_notes = pd.read_sql("SELECT * FROM epic_notes WHERE NOTE_ID in {} AND LENGTH(NOTE) >= 100".format(train_note_ids), con)
    print(train_notes.head())
    train_notes['SERVICE_DTM'] = train_notes['SERVICE_DTM'].apply(pd.to_datetime)
    train_notes['NOTE_TYPE'] = train_notes.NOTE_TYPE.apply(lambda x: '_'.join(x.split()).replace('/', '-') if x else 'NOTE_TYPE_UNKNOWN')
    train_notes['PROV_TYPE'] = train_notes.PROV_TYPE.apply(lambda x: '_'.join(x.split()) if x else 'PROV_TYPE_UNKNOWN')
    train_notes.SERVICE_DTM = train_notes.SERVICE_DTM.apply(lambda x: datetime.strftime(x, '%m-%d-%Y'))
    print(train_notes.head())

    for i, row in train_notes.iterrows():
        if row.NOTE_ID in yes_notes:
            has_complication = 'yes'
        else:
            has_complication = 'no'
        case_number = note_info[note_info.NOTE_ID == row.NOTE_ID].iloc[0].case_number
        save_note(row, case_number, train_dir, has_complication)

    con.close()
    pass


if __name__ == '__main__':
    datadir = sys.argv[1]
    main()
