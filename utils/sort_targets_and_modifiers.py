"""
This is a helper script to arrange the targets and modifiers file
so that we can keep it in the correct order while easily editing it.
Targets sorted by: TYPE, LEX,
Modifiers sorted as: ANATOMY, SURGICAL_SITE, others
and by TYPE, LEX within each category
"""

import os


def sort_targets(targets_file):
    with open(targets_file) as f_in:
        lines = f_in.read().splitlines()
    header = lines[0]
    targets = [line.split('\t') for line in lines[1:]]
    targets = sorted(targets, key=lambda x: (x[1], x[0])) #  Type, Lex
    targets = ['\t'.join(line) for line in targets]
    with open(targets_file, 'w') as f_out:
        f_out.write(header)
        f_out.write('\n')
        f_out.write('\n'.join(targets))
    print("Sorted targets")


def sort_modifiers(modifiers_file):

    mapping = {'ANATOMY': 0, 'SURGICAL_SITE': 1}
    with open(modifiers_file) as f_in:
        lines = f_in.read().splitlines()
    header = lines[0]
    modifiers = [line.split('\t') for line in lines[1:]]
    # First sort to be [ANATOMY, SURGICAL_SITE, other],
    # and then sort by [TYPE, LEX]
    modifiers = sorted(modifiers, key=lambda x: (mapping[x[1]], x[1], x[0]) if x[1] in mapping else (2, x[1], x[0]))

    print(modifiers[:5])
    modifiers = ['\t'.join(line) for line in modifiers]
    with open(modifiers_file, 'w') as f_out:
        f_out.write(header)
        f_out.write('\n')
        f_out.write('\n'.join(modifiers))
    print("Sorted modifiers")



def main():
    targets_file = os.path.join(datadir, 'targets.tsv')
    sort_targets(targets_file)

    modifiers_file = os.path.join(datadir, 'modifiers.tsv')
    sort_modifiers(modifiers_file)


if __name__ == '__main__':
    datadir = '../lexicon'
    main()
