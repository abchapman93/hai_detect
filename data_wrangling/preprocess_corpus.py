"""
This script carries out preprocessing functions defined in `utils.helpers` on a corpus of texts.
Inserts a period and two lines before any known multi-word headers or default one-word headers.
"""
import glob
import os
import sys
import re
from utils import helpers


def main():
    print(datadir)
    files = glob.glob(os.path.join(datadir, '*.txt'))
    print(files)
    for file in files:
        with open(file) as f_in:
           text = f_in.read()
        #print(text)
        text = re.sub('\n', '', text) #  Get rid of the old new lines that I put in
        text = helpers.preprocess_human(text)
        text = re.sub('\n[ ]+', '\n', text) #  Get rid of new lines followed by multiple spaces
        text = re.sub('[ ]{2,}', ' ', text) #  Get rid of multiple spaces
        text = re.sub('\.\.', '.', text)
        text = re.sub(':\.', ':', text)
        with open(os.path.join(outdir, os.path.basename(file)), 'w') as f_out:
            f_out.write(text)



if __name__ == '__main__':
    datadir = sys.argv[1] # The directory containing subdirectories 'corpus' and 'saved'
    outdir = os.path.join(datadir, 'corpus')
    main()
