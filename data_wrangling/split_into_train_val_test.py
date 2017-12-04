"""
This script splits the notes in epic.epic_notes into three sets
Train, val, and test
(0.6,  0.2,      0.2).
It first accounts for notes that have already been saved/annotated
And then adds the remaining number of yes/no notes
"""

import glob, os, sys
import re
import random
import sqlite3 as sqlite
import pandas as pd


def get_annotated_case_nums():
    notes = glob.glob(os.path.join(datadir, 'initial_batches', 'Batch_*', 'corpus', '*.txt'))
    print(len(notes))

    case_nums = [os.path.basename(n).split('_')[1] for n in notes]

    return set(case_nums)

def assign_to_set(*args):
    case_num, train, val, test = args
    if case_num in train:
        return 'train'
    elif case_num in val:
        return 'val'
    elif case_num in test:
        return 'test'
    else:
        return ''


def main():
    annotated_case_nums = get_annotated_case_nums()
    print(len(annotated_case_nums))

    # Get all case numbers from cohort
    db = os.path.join(datadir, 'databases', 'epic.sqlite')
    print(db)
    con = sqlite.connect(db)

    df = pd.read_sql("SELECT * FROM note_info", con)
    print(len(df))
    #df = df[df.case_number != 0]
    print(df.head())
    print(len(df))

    all_case_nums = set(df.case_number)
    yes_case_nums = set(df[(df.has_complication ==1) & (df.is_within_30_days == 1)].case_number)
    no_case_nums = set(df[(df.has_complication ==0) & (df.is_within_30_days == 1)].case_number)

    nb_yes = len(yes_case_nums)
    nb_no = len(set(all_case_nums) - set(yes_case_nums))

    print(nb_yes, nb_no)


    # Put the cases that have already been annotated
    # into the training set
    yes_train = [case_num for case_num in annotated_case_nums if case_num in yes_case_nums]
    no_train = [case_num for case_num in annotated_case_nums if case_num not in yes_case_nums]
    print(len(yes_case_nums))
    print(len(no_case_nums))

    # Take them out of the sampling pool
    yes_case_nums = set(yes_case_nums) - set(annotated_case_nums)
    no_case_nums = set(no_case_nums) - set(annotated_case_nums)
    print(len(yes_case_nums))
    print(len(no_case_nums))


    yes_val = []
    no_val = []

    yes_test = []
    no_test = []

    # Overall numbers for each set
    nb_train_yes = int(nb_yes * 0.6)
    nb_train_no = int(nb_no * 0.6)

    nb_val_yes = int(nb_yes * 0.2)
    nb_val_no = int(nb_no * 0.2)

    nb_test_yes = nb_yes - nb_train_yes - nb_val_yes
    nb_test_no = nb_no - nb_train_no - nb_val_no

    print(nb_train_yes, nb_train_no)
    print(nb_val_yes, nb_val_no)
    print(nb_test_yes, nb_test_no)

    yes_case_nums = list(yes_case_nums)
    no_case_nums = list(no_case_nums)

    # Number of case numbers to put in train
    # after adding those that have already been annotated
    nb_yes_to_sample_train = nb_train_yes - len(yes_train)
    nb_no_to_sample_train = nb_train_no - len(no_train)
    print(nb_yes_to_sample_train, nb_no_to_sample_train)
    print(nb_val_yes, nb_val_no)
    print(nb_test_yes, nb_test_no)

    print(len(yes_train), len(no_train))

    random.shuffle(list(set(yes_case_nums)))
    random.shuffle(list(set(no_case_nums)))

    yes_train.extend(yes_case_nums[:nb_yes_to_sample_train])
    no_train.extend(no_case_nums[:nb_no_to_sample_train])

    yes_val.extend(yes_case_nums[nb_yes_to_sample_train:nb_yes_to_sample_train + nb_val_yes])
    no_val.extend(no_case_nums[nb_no_to_sample_train:nb_no_to_sample_train + nb_val_no])

    yes_test.extend(yes_case_nums[nb_yes_to_sample_train + nb_val_yes: ])
    no_test.extend(no_case_nums[nb_no_to_sample_train + nb_val_no: ])

    print("Yes Train: {}".format(len(yes_train)))
    print("No Train: {}".format(len(no_train)))
    print("Yes Val: {}".format(len(yes_val)))
    print("No Val: {}".format(len(no_val)))
    print("Yes Test: {}".format(len(yes_test)))
    print("No Test: {}".format(len(no_test)))

    print(nb_yes_to_sample_train, nb_no_to_sample_train)

    train = set(yes_train).union(no_train)
    val = set(yes_val).union(no_val)
    test = set(yes_test).union(no_test)


    try:
        assert len(set(train).intersection(set(val))) == 0
    except Exception as e:
        print(train.intersection(val))
        raise e
    assert len(set(val).intersection(set(test))) == 0
    assert len(set(train).intersection(set(test))) == 0

    df['train_val_test'] = df.case_number.apply(lambda x: assign_to_set(x, train, val, test))
    print(df[df.train_val_test != ''].head())

    df[df.train_val_test != ''].to_csv('train_val_test.csv')
    print(os.getcwd())

    df.to_sql('note_info', con, if_exists='replace')

    exit()
    print("Saved new table at {}".format(db))





if __name__ == '__main__':
    datadir = sys.argv[1]
    print(datadir)
    main()
