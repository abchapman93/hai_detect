"""
This script carries out preprocessing functions defined in `utils.helpers` on a corpus of texts.
Inserts a period and two lines before any known multi-word headers or default one-word headers.
"""
import glob
import os
import sys
import re
import helpers


def process_text(text):
    text = re.sub('\n', ' ', text) #  Get rid of the old new lines that I put in
    #target = re.compile('([a-zA-Z0-9/:]{3,})\.([a-zA-Z0-9/:]{3,})', flags=re.IGNORECASE)
    #text = target.sub(r'\1. \2', text)
    #text = re.sub('([a-zA-Z]{3,}).([a-zA-Z]{3,})', '\1. \2', text)

    text = helpers.preprocess_human(text)
    text = re.sub('\n[ ]+', '\n', text) #  Get rid of new lines followed by multiple spaces
    text = re.sub('[ ]{2,}', ' ', text) #  Get rid of multiple spaces
    text = re.sub('\.\.', '.', text)
    text = re.sub(':\.', ':', text)

    # Check if the document classification addendum is present
    # If it is, add new lines
    # If not, add it
    addendum = """Annotate the following statement as a document classification: Based on THIS DOCUMENT ONLY the patient DOES or DOES NOT have a HAI"""
    if addendum in text:
        text = text.replace(addendum, '\n\n'+addendum)
    else:
        text += '\n\n' + addendum
    return text


def main():
    print(datadir)
    files = glob.glob(os.path.join(datadir, '*', '*.txt'))
    #files = glob.glob(os.path.join(datadir, 'corpus', '*.txt'))
    print(len(files))
    for file in files:
        with open(file) as f_in:
           text = f_in.read()
        text = process_text(text)
        #print(text)

        with open(file, 'w') as f_out:
        ##with open(os.path.join(outdir, os.path.basename(file)), 'w') as f_out:
            f_out.write(text)



if __name__ == '__main__':
    datadir = sys.argv[1] # The directory containing subdirectories 'corpus' and 'saved'
    #outdir = os.path.join(datadir, 'corpus')
    main()
