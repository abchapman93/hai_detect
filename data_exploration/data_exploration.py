import os, sys
import pandas as pd
import sqlite3 as sqlite

def main():
    db = os.path.join(datadir, 'epic.sqlite')
    con = sqlite.connect(db)
    info = {}
    # How many patients in `epic_notes`
    info['num_patients'] = con.execute("SELECT COUNT (DISTINCT PAT_ID) FROM epic_notes").fetchone()[0]
    # How many notes
    info['num_notes'] = con.execute("SELECT COUNT (DISTINCT NOTE_ID) FROM epic_notes").fetchone()[0]
    # How many pats with notes within 30 days?
    info['pats_with_notes_within_30_days'] = con.execute("SELECT COUNT (DISTINCT PAT_ID) FROM note_info\
                                                         WHERE (is_within_30_days = 1)").fetchone()[0]

    info['notes_within_30_days'] = con.execute("SELECT COUNT (DISTINCT NOTE_ID) FROM note_info\
                                               WHERE is_within_30_days = 1").fetchone()[0]
    info['pats_within_30_days_with_hai'] = con.execute("SELECT COUNT (DISTINCT PAT_ID) FROM note_info\
                                               WHERE is_within_30_days = 1\
                                               AND has_complication = 1").fetchone()[0]
    info['notes_within_30_days_with_hai'] = con.execute("SELECT COUNT (DISTINCT NOTE_ID) FROM note_info\
                                               WHERE is_within_30_days = 1\
                                               AND has_complication = 1").fetchone()[0]
    info['% of pats in cohort with hai'] = info['pats_within_30_days_with_hai'] / info['pats_with_notes_within_30_days'] * 100
    print("Total number of patients in table `epic_notes`: {num_patients}".format(**info))
    print("Total number of notes in table `epic_notes`: {num_notes}".format(**info))
    print('Total number of patients with notes within 30 days of an operation: {pats_with_notes_within_30_days}'.format(**info))
    print("Total number of notes within 30 days: {notes_within_30_days}".format(**info))
    print('Total number of patients with notes within 30 days of an operation with HAI: {pats_within_30_days_with_hai}'.format(**info))
    print("Total number of notes within 30 days with HAI: {notes_within_30_days_with_hai}".format(**info))
    print("Percentage of patients in chort with HAI: {% of pats in cohort with hai}%".format(**info))


    con.close()



if __name__ == '__main__':
    datadir = sys.argv[1]
    main()
