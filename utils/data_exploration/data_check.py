"""
This script asserts that there is no overlap
between train, val and test notes
and prints out info about the distribution of notes
"""
import os, glob, sys


def main():
    assert(os.path.exists(datadir))
    train_notes = glob.glob(os.path.join(datadir, 'train', '*.txt'))
    val_notes = glob.glob(os.path.join(datadir, 'val', '*.txt'))
    test_notes = glob.glob(os.path.join(datadir, 'test', '*.txt'))

    train_notes = set([os.path.basename(f) for f in train_notes])
    val_notes = set([os.path.basename(f) for f in val_notes])
    test_notes = set([os.path.basename(f) for f in test_notes])

    assert len(train_notes.intersection(val_notes)) == 0
    assert len(val_notes.intersection(test_notes)) == 0
    assert len(train_notes.intersection(test_notes)) == 0

    total_nb_notes = (len(train_notes) + len(val_notes) + len(test_notes))
    print("Location of notes: {}".format(datadir))
    print("Total number of notes: {}".format(total_nb_notes))
    for set_name, note_set in (('train', train_notes), ('val', val_notes), ('test', test_notes)):
        cases = set([f.split('_')[1] for f in note_set])
        print(set_name)
        print("# cases: {}".format(len(cases)))
        print("# notes: {}".format(len(note_set)))
        print("% notes: {}".format(len(note_set) / (len(train_notes) + len(val_notes) + len(test_notes))))



if __name__ == '__main__':
    datadir = sys.argv[1]
    main()



